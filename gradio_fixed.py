#!/usr/bin/env python3
"""
Fixed Progressive Results Version of Gradio GemFinder
Fixes frontend display issues and improves performance
"""

import gradio as gr
import os
import time
from typing import List, Dict, Any, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading

# Your existing modules
from providers import (
    SearchManager,
    DiscogsProvider, RevibedProvider,
    ItunesProvider, BeatportProvider, BandcampProvider, TraxsourceProvider
)
from gradio_state_manager import GradioAppState
from utils import get_platform_info, is_fuzzy_match
from text_extract import extract_text_from_image, analyze_text_with_gpt4
from gradio_helpers import GradioDiscogsMaketplace, create_mobile_responsive_css

class FixedGemFinder:
    def __init__(self):
        self.app_state = GradioAppState()
        # Temporarily disable Bandcamp due to timeout issues
        self.digital_providers = [ItunesProvider(), BeatportProvider(), TraxsourceProvider()]
        # TODO: Re-enable Bandcamp with better timeout handling
        self.secondary_providers = [DiscogsProvider(), RevibedProvider()]
        
        # Enhanced components
        self.marketplace = GradioDiscogsMaketplace()
        
        # Search state
        self.search_in_progress = False
        self.search_results = {
            'digital': [],
            'discogs': [],
            'revibed': []
        }
        
        # Progress tracking
        self.search_status = "Ready"
        self.platforms_completed = 0
        self.total_platforms = 0
        
    def check_search_criteria(self, tracks: str, artist: str, album: str, catalog: str) -> Tuple[bool, str]:
        """Check if minimum search criteria are met"""
        # Update app state with current inputs
        self.app_state.update({
            'tracks_input': tracks,
            'artist_input': artist, 
            'album_input': album,
            'catalog_number_input': catalog
        })
        
        criteria = self.app_state.get_criteria()
        
        # Check which platforms can search
        can_search_digital = any(p.can_search(criteria) for p in self.digital_providers)
        can_search_secondary = any(p.can_search(criteria) for p in self.secondary_providers)
        
        if can_search_digital or can_search_secondary:
            searchable_platforms = []
            if can_search_digital:
                searchable_platforms.extend([p.name for p in self.digital_providers if p.can_search(criteria)])
            if can_search_secondary:
                searchable_platforms.extend([p.name for p in self.secondary_providers if p.can_search(criteria)])
            return True, f"Ready to search: {', '.join(searchable_platforms)}"
        else:
            return False, "Please fill in minimum required fields to enable search."
    
    def extract_text_from_upload(self, image_file) -> Tuple[str, str, str, str, str]:
        """Extract text from uploaded image and return structured fields"""
        if image_file is None:
            return "", "", "", "", ""
            
        try:
            # Extract text from image
            extracted_text = extract_text_from_image(image_file)
            
            # Analyze text to get structured fields (upload mode = discogs-only scenario)
            artist, album, tracks, label, catalog = analyze_text_with_gpt4(extracted_text, mode_context='upload')
            
            # Handle tracks (join if list, or use as string)
            if tracks:
                if isinstance(tracks, list):
                    track_list = [str(t).strip() for t in tracks if str(t).strip()]
                    tracks_str = "; ".join(track_list) if track_list else ""
                else:
                    tracks_str = str(tracks) if tracks else ""
            else:
                tracks_str = ""
            
            return (
                tracks_str,
                str(artist) if artist else "",
                str(album) if album else "",
                str(catalog) if catalog else "",
                f"✅ Extracted: Artist={artist}, Album={album}, Tracks={len(track_list) if isinstance(tracks, list) else bool(tracks_str)}, Catalog={catalog}"
            )
        except Exception as e:
            return "", "", "", "", f"❌ Error extracting text: {str(e)}"
    
    def search_platform_thread_safe(self, provider, criteria) -> Dict[str, Any]:
        """Thread-safe search without UI updates"""
        try:
            result = provider.search(criteria)
            return {"status": "success", "result": result, "provider": provider.name}
        except Exception as e:
            print(f"❌ {provider.name} error: {str(e)}")
            return {"status": "error", "error": str(e), "provider": provider.name}
    
    def perform_search(self, tracks: str, artist: str, album: str, catalog: str, selected_track: str) -> Tuple[str, str, str, str, List[str], Dict]:
        """Perform the actual search and return formatted results"""
        if self.search_in_progress:
            return "Search already in progress...", "", "", "⏳ Search in progress", [], gr.update(visible=False)
        
        self.search_in_progress = True
        self.search_results = {'digital': [], 'discogs': [], 'revibed': []}
        self.platforms_completed = 0
        
        try:
            # Update app state
            self.app_state.update({
                'tracks_input': tracks,
                'artist_input': artist,
                'album_input': album,
                'catalog_number_input': catalog,
                'selected_track': selected_track or tracks.split(';')[0].strip() if tracks else ""
            })
            
            criteria = self.app_state.get_criteria()
            
            # Check what we can search
            can_search_digital = any(p.can_search(criteria) for p in self.digital_providers)
            can_search_secondary = any(p.can_search(criteria) for p in self.secondary_providers)
            
            if not (can_search_digital or can_search_secondary):
                return "❌ Insufficient search criteria", "", "", "❌ Cannot search", [], gr.update(visible=False)
            
            self.total_platforms = (len([p for p in self.digital_providers if p.can_search(criteria)]) + 
                                   len([p for p in self.secondary_providers if p.can_search(criteria)]))
            
            # Stage 1: Digital platforms with faster timeout
            digital_results = []
            if can_search_digital:
                self.search_status = "🔍 Searching digital platforms..."
                
                # Use stable providers (Bandcamp already excluded from digital_providers)
                stable_providers = [p for p in self.digital_providers if p.can_search(criteria)]
                
                with ThreadPoolExecutor(max_workers=3) as executor:  # Reduced workers
                    futures = {executor.submit(self.search_platform_thread_safe, p, criteria): p 
                              for p in stable_providers}
                    
                    for future in as_completed(futures, timeout=20):  # 20 second timeout
                        try:
                            thread_result = future.result(timeout=8)  # 8 second per provider
                            self.platforms_completed += 1
                            
                            if thread_result["status"] == "success":
                                entry = thread_result["result"]
                            else:
                                entry = {
                                    "platform": thread_result["provider"],
                                    "title": "Fehler",
                                    "artist": "",
                                    "album": "",
                                    "label": "",
                                    "price": "",
                                    "cover_url": "",
                                    "url": "",
                                    "error": thread_result["error"]
                                }
                            
                            digital_results.append(entry)
                            self.search_results['digital'] = digital_results
                            
                        except Exception as e:
                            print(f"❌ Digital search timeout: {e}")
                            continue
            
            # Stage 2: Secondary platforms (Discogs and Revibed)
            secondary_results_discogs = []
            secondary_results_revibed = []
            
            if can_search_secondary:
                self.search_status = "🔍 Searching Discogs and Revibed..."
                
                with ThreadPoolExecutor(max_workers=2) as executor:
                    secondary_futures = []
                    
                    for p in self.secondary_providers:
                        if p.can_search(criteria):
                            future = executor.submit(self.search_platform_thread_safe, p, criteria)
                            secondary_futures.append((future, p.name))
                    
                    for future, provider_name in secondary_futures:
                        try:
                            thread_result = future.result(timeout=15)  # 15 second timeout
                            self.platforms_completed += 1
                            
                            if thread_result["status"] == "success":
                                if provider_name == "Discogs":
                                    result = thread_result["result"]
                                    secondary_results_discogs = result.get("releases", [])
                                    self.search_results['discogs'] = secondary_results_discogs
                                elif provider_name == "Revibed":
                                    result = thread_result["result"]
                                    secondary_results_revibed = [result] if result else []
                                    self.search_results['revibed'] = secondary_results_revibed
                        except Exception as e:
                            print(f"❌ Secondary search timeout: {e}")
                            continue
            
            # Format results
            digital_html = self.format_search_results(digital_results) if digital_results else ""
            discogs_html = self.format_discogs_results(secondary_results_discogs) if secondary_results_discogs else ""
            revibed_html = self.format_revibed_results(secondary_results_revibed) if secondary_results_revibed else ""
            
            # Status summary
            digital_count = len([r for r in digital_results if self._is_valid_result(r)])
            discogs_count = len(secondary_results_discogs)
            revibed_count = len([r for r in secondary_results_revibed if self._is_valid_result(r)])
            
            status = f"✅ Search complete! Digital: {digital_count}, Discogs: {discogs_count}, Revibed: {revibed_count}"
            
            # Marketplace choices
            release_choices = []
            marketplace_visible = False
            if secondary_results_discogs:
                release_choices = [
                    f"{r.get('title', 'Unknown')} - {r.get('label', ['Unknown'])[0] if r.get('label') else 'Unknown'} ({r.get('year', 'Unknown')})"
                    for r in secondary_results_discogs[:10]
                ]
                marketplace_visible = True
            
            return digital_html, discogs_html, revibed_html, status, release_choices, gr.update(visible=marketplace_visible)
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return f"❌ Search error: {str(e)}", "", "", "Search failed", [], gr.update(visible=False)
        finally:
            self.search_in_progress = False
    
    def format_search_results(self, results: List[Dict]) -> str:
        """Format search results for display"""
        if not results:
            return "<p>No digital results found.</p>"
        
        html_output = "<div style='padding: 10px;'>"
        
        for entry in results:
            platform = entry.get("platform", "Unknown")
            title = entry.get("title", "")
            artist = entry.get("artist", "")
            album = entry.get("album", "")
            price = entry.get("price", "")
            url = entry.get("url", "")
            cover_url = entry.get("cover_url", "") or entry.get("cover", "")
            
            # Check if this is a valid result
            is_valid = title and title.lower() not in ["kein treffer", "fehler", ""]
            
            if is_valid:
                html_output += f"""
                <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background: #f9f9f9;">
                    <div style="display: flex; align-items: flex-start;">
                        {"<img src='" + cover_url + "' style='width: 80px; height: 80px; object-fit: cover; margin-right: 15px; border-radius: 4px;'>" if cover_url else ""}
                        <div>
                            <h3 style="margin: 0 0 5px 0; color: #333;">
                                {"<a href='" + url + "' target='_blank' style='text-decoration: none; color: #0066cc;'>" + platform + "</a>" if url else platform}
                            </h3>
                            <p style="margin: 2px 0; font-weight: bold; font-size: 16px;">{title}</p>
                            {f"<p style='margin: 2px 0; color: #666;'>{artist}</p>" if artist else ""}
                            {f"<p style='margin: 2px 0; font-style: italic;'>{album}</p>" if album else ""}
                            {f"<p style='margin: 5px 0; color: #009900; font-weight: bold;'>{price}</p>" if price else ""}
                        </div>
                    </div>
                </div>
                """
            else:
                # Show "no hit" results differently
                platform_url, _ = get_platform_info(platform)
                html_output += f"""
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 10px; margin: 5px 0; background: #fafafa; opacity: 0.7;">
                    <p style="margin: 0;">
                        <a href="{platform_url}" target="_blank" style="text-decoration: none; color: #666;">{platform}</a>: 
                        <span style="color: #999;">{title}</span>
                    </p>
                </div>
                """
        
        html_output += "</div>"
        return html_output
    
    def format_discogs_results(self, releases: List[Dict]) -> str:
        """Format Discogs releases for display"""
        if not releases:
            return "<p>No Discogs releases found.</p>"
        
        html_output = "<div style='padding: 10px;'><h3>Discogs Releases</h3>"
        
        for i, release in enumerate(releases[:5]):  # Show top 5
            title = release.get('title', 'Unknown Title')
            label = release.get('label', ['-'])[0] if release.get('label') else '-'
            year = release.get('year', '-')
            format_info = ', '.join(release.get('format', [])) if release.get('format') else '-'
            uri = release.get('uri', '')
            cover = release.get('cover_image', '') or release.get('thumb', '')
            
            community = release.get('community', {})
            have_count = community.get('have', '-')
            want_count = community.get('want', '-')
            
            html_output += f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin: 10px 0; background: #f9f9f9;">
                <div style="display: flex; align-items: flex-start;">
                    {"<img src='" + cover + "' style='width: 100px; height: 100px; object-fit: cover; margin-right: 15px; border-radius: 4px;'>" if cover else ""}
                    <div>
                        <h4 style="margin: 0 0 8px 0;">
                            {"<a href='https://www.discogs.com" + uri + "' target='_blank' style='text-decoration: none; color: #0066cc;'>" + title + "</a>" if uri else title}
                        </h4>
                        <p style="margin: 2px 0;"><strong>Label:</strong> {label}</p>
                        <p style="margin: 2px 0;"><strong>Year:</strong> {year}</p>
                        <p style="margin: 2px 0;"><strong>Format:</strong> {format_info}</p>
                        <p style="margin: 5px 0;"><strong>Have/Want:</strong> <span style="color: green;">{have_count}</span>/<span style="color: red;">{want_count}</span></p>
                    </div>
                </div>
            </div>
            """
        
        html_output += "</div>"
        return html_output
    
    def format_revibed_results(self, results: List[Dict]) -> str:
        """Format Revibed results for display"""
        if not results:
            return "<p>No Revibed results found.</p>"
        
        html_output = "<div style='padding: 10px;'><h3>Revibed Results</h3>"
        
        for entry in results:
            title = entry.get('title', '')
            artist = entry.get('artist', '')
            album = entry.get('album', '')
            price = entry.get('price', '')
            url = entry.get('url', '')
            cover = entry.get('cover_url', '') or entry.get('cover', '')
            
            # Check if valid result
            if title and title.lower() not in ["kein treffer", "fehler", "nicht verfügbar"]:
                html_output += f"""
                <div style="border: 1px solid #1ad6cc; border-radius: 8px; padding: 15px; margin: 10px 0; background: #f0fdfc;">
                    <div style="display: flex; align-items: flex-start;">
                        {"<img src='" + cover + "' style='width: 80px; height: 80px; object-fit: cover; margin-right: 15px; border-radius: 4px;'>" if cover else ""}
                        <div>
                            <h4 style="margin: 0 0 8px 0; color: #1ad6cc;">Revibed</h4>
                            <p style="margin: 2px 0; font-weight: bold;">{title}</p>
                            {f"<p style='margin: 2px 0; color: #666;'>{artist}</p>" if artist else ""}
                            {f"<p style='margin: 2px 0;'>{album}</p>" if album else ""}
                            {f"<p style='margin: 5px 0; color: #1ad64a; font-weight: bold;'>{price}</p>" if price else ""}
                            {f"<a href='{url}' target='_blank' style='color: #0066cc;'>View on Revibed</a>" if url else ""}
                        </div>
                    </div>
                </div>
                """
            else:
                html_output += f"""
                <div style="border: 1px solid #eee; border-radius: 8px; padding: 10px; margin: 5px 0; background: #fafafa;">
                    <p style="margin: 0; color: #1ad6cc;"><strong>Revibed:</strong> <span style="color: #999;">{title or 'No results found'}</span></p>
                </div>
                """
        
        html_output += "</div>"
        return html_output
    
    def _is_valid_result(self, result: Dict) -> bool:
        """Check if a search result is valid (not a 'no hit' response)"""
        title = result.get('title', '').lower()
        return title and title not in ['kein treffer', 'fehler', 'nicht verfügbar', '']
    
    def get_track_options(self, tracks_input: str) -> List[str]:
        """Get list of tracks for selection"""
        if not tracks_input:
            return []
        return [t.strip() for t in tracks_input.split(';') if t.strip()]
    
    def create_interface(self):
        """Create the fixed interface with better result display"""
        
        # Custom CSS for better mobile experience and styling
        css = create_mobile_responsive_css()
        
        with gr.Blocks(title="GEM DETECTOR - FIXED", css=css) as interface:
            
            # Header
            gr.HTML("""
                <div style="text-align: center; padding: 20px;">
                    <img src="record_mole_copy.png" width="220" style="margin-bottom: 10px;">
                    <h1 style="margin: 0; color: #333;">GEM DETECTOR</h1>
                    <p style="color: #666;">Fixed Version - Stable Results Display!</p>
                </div>
            """)
            
            # Mode selection
            with gr.Row():
                mode = gr.Radio(
                    choices=["Manual Input", "Upload photo", "Take a picture"],
                    value="Manual Input",
                    label="Choose Input Mode"
                )
                reset_btn = gr.Button("Reset", variant="secondary", size="sm")
            
            # Input fields (always visible)
            with gr.Group():
                tracks_input = gr.Textbox(
                    label="Track(s)",
                    placeholder="Enter one or more track titles separated by semicolon (;)",
                    lines=1
                )
                artist_input = gr.Textbox(
                    label="Artist",
                    placeholder="Enter artist name",
                    lines=1
                )
                catalog_input = gr.Textbox(
                    label="Catalog Number",
                    placeholder="Enter catalog number",
                    lines=1
                )
                album_input = gr.Textbox(
                    label="Album",
                    placeholder="Enter album name",
                    lines=1
                )
            
            # Photo upload (conditional)
            with gr.Group(visible=False) as photo_group:
                image_upload = gr.Image(
                    label="Upload Photo",
                    type="filepath",
                    sources=["upload"]
                )
                extraction_status = gr.Textbox(
                    label="Extraction Status",
                    interactive=False
                )
            
            # Camera input (conditional)  
            with gr.Group(visible=False) as camera_group:
                camera_input = gr.Image(
                    label="Take Picture",
                    type="filepath",
                    sources=["webcam"]
                )
                camera_extraction_status = gr.Textbox(
                    label="Extraction Status", 
                    interactive=False
                )
            
            # Track selection (appears when multiple tracks)
            track_selector = gr.Dropdown(
                label="Select Track for Search",
                choices=[],
                visible=False,
                interactive=True
            )
            
            # Search status and button
            search_status = gr.Textbox(
                label="Search Status",
                value="Please fill in minimum required fields to enable search.",
                interactive=False
            )
            
            search_btn = gr.Button(
                "Search",
                variant="primary",
                size="lg",
                interactive=False
            )
            
            # Live status display
            live_status = gr.Textbox(
                label="Live Status",
                value="",
                interactive=False,
                visible=False
            )
            
            # Results section with fixed display
            with gr.Tabs():
                with gr.Tab("🎵 Digital Platforms"):
                    digital_results = gr.HTML(label="Digital Results", value="<p>No search performed yet.</p>")
                
                with gr.Tab("📀 Discogs"):
                    with gr.Column():
                        discogs_results = gr.HTML(label="Discogs Results", value="<p>No search performed yet.</p>")
                        
                        # Discogs marketplace section
                        with gr.Group(visible=False) as marketplace_group:
                            gr.Markdown("### 🛒 Marketplace Offers")
                            
                            with gr.Row():
                                release_selector = gr.Dropdown(
                                    label="Select Release",
                                    choices=[],
                                    interactive=True
                                )
                                load_offers_btn = gr.Button("Load Offers", variant="secondary")
                            
                            marketplace_results = gr.HTML(label="Offers")
                
                with gr.Tab("🎧 Revibed"):
                    revibed_results = gr.HTML(label="Revibed Results", value="<p>No search performed yet.</p>")
            
            # Event handlers
            
            def update_mode_visibility(mode_value):
                return (
                    gr.update(visible=(mode_value == "Upload photo")),
                    gr.update(visible=(mode_value == "Take a picture"))
                )
            
            def check_criteria_and_update(tracks, artist, album, catalog):
                can_search, status = self.check_search_criteria(tracks, artist, album, catalog)
                track_options = self.get_track_options(tracks)
                
                return (
                    gr.update(value=status),
                    gr.update(interactive=can_search),
                    gr.update(choices=track_options, visible=len(track_options) > 1, value=track_options[0] if track_options else "")
                )
            
            def reset_all():
                self.search_in_progress = False
                self.search_results = {'digital': [], 'discogs': [], 'revibed': []}
                return (
                    "", "", "", "", "", "", 
                    gr.update(choices=[], visible=False), 
                    "Please fill in minimum required fields.", 
                    gr.update(interactive=False),
                    gr.update(visible=False),
                    "<p>No search performed yet.</p>", 
                    "<p>No search performed yet.</p>", 
                    "<p>No search performed yet.</p>",
                    "Ready for search"
                )
            
            def extract_from_upload(image_file):
                return self.extract_text_from_upload(image_file)
            
            def search_wrapper(tracks, artist, album, catalog, selected_track):
                # Show that search is starting
                gr.update(value="🔍 Search started...", visible=True)
                
                # Perform the search
                digital_html, discogs_html, revibed_html, status, release_choices, marketplace_update = \
                    self.perform_search(tracks, artist, album, catalog, selected_track)
                
                return (
                    digital_html,
                    discogs_html, 
                    revibed_html,
                    gr.update(value=status, visible=True),
                    release_choices,
                    marketplace_update
                )
            
            def load_marketplace_offers(selected_release_idx):
                if selected_release_idx is None or not self.search_results['discogs']:
                    return "Please select a release first."
                
                try:
                    # Find the release by matching the dropdown text
                    for i, release in enumerate(self.search_results['discogs']):
                        release_text = f"{release.get('title', 'Unknown')} - {release.get('label', ['Unknown'])[0] if release.get('label') else 'Unknown'} ({release.get('year', 'Unknown')})"
                        if release_text == selected_release_idx:
                            offers_html, status = self.marketplace.load_and_display_offers(release, False)
                            return offers_html
                except Exception as e:
                    return f"Error loading offers: {str(e)}"
                
                return "Error loading offers for selected release."
            
            # Wire up events
            mode.change(
                update_mode_visibility,
                inputs=[mode],
                outputs=[photo_group, camera_group]
            )
            
            # Update search status when inputs change
            for input_component in [tracks_input, artist_input, album_input, catalog_input]:
                input_component.change(
                    check_criteria_and_update,
                    inputs=[tracks_input, artist_input, album_input, catalog_input],
                    outputs=[search_status, search_btn, track_selector]
                )
            
            # Reset functionality
            reset_btn.click(
                reset_all,
                outputs=[
                    tracks_input, artist_input, album_input, catalog_input, 
                    extraction_status, camera_extraction_status, 
                    track_selector, search_status, search_btn, live_status,
                    digital_results, discogs_results, revibed_results,
                    live_status
                ]
            )
            
            # Image extraction
            image_upload.change(
                extract_from_upload,
                inputs=[image_upload],
                outputs=[tracks_input, artist_input, album_input, catalog_input, extraction_status]
            )
            
            camera_input.change(
                extract_from_upload,
                inputs=[camera_input],
                outputs=[tracks_input, artist_input, album_input, catalog_input, camera_extraction_status]
            )
            
            # Search functionality
            search_btn.click(
                search_wrapper,
                inputs=[tracks_input, artist_input, album_input, catalog_input, track_selector],
                outputs=[digital_results, discogs_results, revibed_results, live_status, release_selector, marketplace_group]
            )
            
            # Marketplace functionality
            load_offers_btn.click(
                load_marketplace_offers,
                inputs=[release_selector],
                outputs=[marketplace_results]
            )
        
        return interface

# Initialize and run the application
def main():
    gem_finder = FixedGemFinder()
    interface = gem_finder.create_interface()
    
    # Launch with similar settings to Streamlit
    interface.launch(
        server_name="0.0.0.0",
        server_port=7862,  # Different port
        share=False,
        debug=True,
        show_error=True
    )

if __name__ == "__main__":
    main()