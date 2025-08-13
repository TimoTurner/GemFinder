#!/usr/bin/env python3
"""
GemFinder Gradio Interface
Migrated from Streamlit to resolve state management and performance issues
"""

import gradio as gr
import os
import time
from typing import List, Dict, Any, Tuple, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Your existing modules
from providers import (
    SearchManager,
    DiscogsProvider, RevibedProvider,
    ItunesProvider, BeatportProvider, BandcampProvider, TraxsourceProvider
)
from gradio_state_manager import GradioAppState
from utils import get_platform_info, is_fuzzy_match
from text_extract import extract_text_from_image, analyze_text_with_gpt4
from gradio_helpers import GradioDiscogsMaketplace, GradioSearchProgress, create_mobile_responsive_css

class GradioGemFinder:
    def __init__(self):
        self.app_state = GradioAppState()
        self.digital_providers = [ItunesProvider(), BeatportProvider(), BandcampProvider(), TraxsourceProvider()]
        self.secondary_providers = [DiscogsProvider(), RevibedProvider()]
        
        # Enhanced components
        self.marketplace = GradioDiscogsMaketplace()
        self.progress_tracker = GradioSearchProgress()
        
        # Search state
        self.search_in_progress = False
        self.current_results = {
            'digital': [],
            'discogs': [],
            'revibed': []
        }
        self.selected_discogs_release = None
        
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
            return {"status": "error", "error": str(e), "provider": provider.name}
    
    def format_search_results(self, results: List[Dict]) -> str:
        """Format search results for display"""
        if not results:
            return "No results found."
        
        html_output = ""
        
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
                            {f"<p style='margin: 5px 0; color: #009900; font-weight: bold;'>{price}</p>" if price and url else f"<p style='margin: 5px 0; color: #009900; font-weight: bold;'>{price}</p>" if price else ""}
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
        
        return html_output or "No valid results found."
    
    def perform_search_progressive(self, tracks: str, artist: str, album: str, catalog: str, selected_track: str):
        """Generator function for progressive search results"""
        if self.search_in_progress:
            yield "Search already in progress...", "", "", "⏳ Search in progress", [], gr.update(visible=False)
            return
        
        self.search_in_progress = True
        
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
                yield "❌ Insufficient search criteria", "", "", "❌ Cannot search", [], gr.update(visible=False)
                return
            
            # Initialize results
            digital_results = []
            secondary_results_discogs = []
            secondary_results_revibed = []
            
            # Stage 1: Digital platforms with immediate updates
            if can_search_digital:
                yield ("", "", "", "🔍 Starting digital platform search...", [], gr.update(visible=False))
                
                with ThreadPoolExecutor(max_workers=4) as executor:
                    # Submit all digital platform searches
                    futures = {executor.submit(self.search_platform_thread_safe, p, criteria): p 
                              for p in self.digital_providers if p.can_search(criteria)}
                    
                    completed = 0
                    total_digital = len(futures)
                    
                    # Show results immediately as they complete
                    for future in as_completed(futures):
                        thread_result = future.result()
                        completed += 1
                        
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
                        self.current_results['digital'] = digital_results
                        
                        # Yield immediate update with current results
                        digital_html = self.format_search_results(digital_results)
                        status = f"🔍 Digital platforms: {completed}/{total_digital} complete"
                        yield (digital_html, "", "", status, [], gr.update(visible=False))
            
            # Check for digital hits
            real_digital_hits = [r for r in digital_results 
                               if (r.get("title") or "").strip().lower() not in ("kein treffer", "", "fehler")]
            has_digital_hits = len(real_digital_hits) > 0
            
            # Stage 2: Secondary platforms with immediate updates
            if can_search_secondary:
                yield (
                    self.format_search_results(digital_results) if digital_results else "",
                    "", 
                    "", 
                    "🔍 Starting Discogs and Revibed search...",
                    [],
                    gr.update(visible=False)
                )
                
                with ThreadPoolExecutor(max_workers=2) as executor:
                    secondary_futures = []
                    
                    for p in self.secondary_providers:
                        if p.can_search(criteria):
                            future = executor.submit(self.search_platform_thread_safe, p, criteria)
                            secondary_futures.append((future, p.name))
                    
                    completed = 0
                    total_secondary = len(secondary_futures)
                    
                    # Show secondary results immediately as they complete
                    for future, provider_name in secondary_futures:
                        thread_result = future.result()
                        completed += 1
                        
                        if thread_result["status"] == "success":
                            if provider_name == "Discogs":
                                result = thread_result["result"]
                                secondary_results_discogs = result.get("releases", [])
                                self.current_results['discogs'] = secondary_results_discogs
                                
                                # Yield immediate Discogs results
                                discogs_html = self.format_discogs_results(secondary_results_discogs)
                                status = f"✅ Discogs complete, Revibed: {completed-1}/{total_secondary}"
                                
                                # Update marketplace selector if we have results
                                release_choices = []
                                marketplace_visible = False
                                if secondary_results_discogs:
                                    release_choices = [
                                        f"{r.get('title', 'Unknown')} - {r.get('label', ['Unknown'])[0] if r.get('label') else 'Unknown'} ({r.get('year', 'Unknown')})"
                                        for r in secondary_results_discogs[:10]
                                    ]
                                    marketplace_visible = True
                                
                                yield (
                                    self.format_search_results(digital_results) if digital_results else "",
                                    discogs_html,
                                    self.format_revibed_results(secondary_results_revibed) if secondary_results_revibed else "",
                                    status,
                                    release_choices,
                                    gr.update(visible=marketplace_visible)
                                )
                                
                            elif provider_name == "Revibed":
                                result = thread_result["result"]
                                secondary_results_revibed = [result] if result else []
                                self.current_results['revibed'] = secondary_results_revibed
                                
                                # Yield immediate Revibed results
                                revibed_html = self.format_revibed_results(secondary_results_revibed)
                                status = f"✅ Revibed complete, Total: {completed}/{total_secondary}"
                                
                                # Final update with all results
                                release_choices = []
                                marketplace_visible = False
                                if secondary_results_discogs:
                                    release_choices = [
                                        f"{r.get('title', 'Unknown')} - {r.get('label', ['Unknown'])[0] if r.get('label') else 'Unknown'} ({r.get('year', 'Unknown')})"
                                        for r in secondary_results_discogs[:10]
                                    ]
                                    marketplace_visible = True
                                
                                yield (
                                    self.format_search_results(digital_results) if digital_results else "",
                                    self.format_discogs_results(secondary_results_discogs) if secondary_results_discogs else "",
                                    revibed_html,
                                    status,
                                    release_choices,
                                    gr.update(visible=marketplace_visible)
                                )
            
            # Final summary
            digital_count = len([r for r in digital_results if self._is_valid_result(r)])
            discogs_count = len(secondary_results_discogs)
            revibed_count = len([r for r in secondary_results_revibed if self._is_valid_result(r)])
            
            final_status = f"✅ Search complete! Digital: {digital_count}, Discogs: {discogs_count}, Revibed: {revibed_count}"
            
            release_choices = []
            marketplace_visible = False
            if secondary_results_discogs:
                release_choices = [
                    f"{r.get('title', 'Unknown')} - {r.get('label', ['Unknown'])[0] if r.get('label') else 'Unknown'} ({r.get('year', 'Unknown')})"
                    for r in secondary_results_discogs[:10]
                ]
                marketplace_visible = True
            
            yield (
                self.format_search_results(digital_results) if digital_results else "",
                self.format_discogs_results(secondary_results_discogs) if secondary_results_discogs else "",
                self.format_revibed_results(secondary_results_revibed) if secondary_results_revibed else "",
                final_status,
                release_choices,
                gr.update(visible=marketplace_visible)
            )
            
        finally:
            self.search_in_progress = False
    
    def format_discogs_results(self, releases: List[Dict]) -> str:
        """Format Discogs releases for display"""
        if not releases:
            return "No Discogs releases found."
        
        html_output = "<h3>Discogs Releases</h3>"
        
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
        
        return html_output
    
    def format_revibed_results(self, results: List[Dict]) -> str:
        """Format Revibed results for display"""
        if not results:
            return "No Revibed results found."
        
        html_output = "<h3>Revibed Results</h3>"
        
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
        """Create the main Gradio interface"""
        
        # Custom CSS for better mobile experience and styling
        css = create_mobile_responsive_css()
        
        with gr.Blocks(title="GEM DETECTOR", theme=gr.themes.Soft(), css=css) as interface:
            
            # Header
            gr.HTML("""
                <div style="text-align: center; padding: 20px;">
                    <img src="record_mole_copy.png" width="220" style="margin-bottom: 10px;">
                    <h1 style="margin: 0; color: #333;">GEM DETECTOR</h1>
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
            
            # Real-time status for progressive updates
            live_status = gr.Textbox(
                label="Live Search Progress",
                value="",
                interactive=False,
                visible=False
            )
            
            search_btn = gr.Button(
                "Search",
                variant="primary",
                size="lg",
                interactive=False
            )
            
            # Results section with enhanced display
            results_summary = gr.HTML(value="", visible=False)
            
            # Results tabs
            with gr.Tabs() as results_tabs:
                with gr.Tab("🎵 Digital Platforms"):
                    digital_results = gr.HTML(label="Digital Results")
                
                with gr.Tab("📀 Discogs"):
                    with gr.Column():
                        discogs_results = gr.HTML(label="Discogs Results")
                        
                        # Discogs marketplace section
                        with gr.Group(visible=False) as marketplace_group:
                            gr.Markdown("### 🛒 Marketplace Offers")
                            
                            with gr.Row():
                                release_selector = gr.Dropdown(
                                    label="Select Release",
                                    choices=[],
                                    interactive=True,
                                    allow_custom_value=True
                                )
                                load_offers_btn = gr.Button("Load Offers", variant="secondary")
                            
                            marketplace_results = gr.HTML(label="Offers")
                
                with gr.Tab("🎧 Revibed"):
                    revibed_results = gr.HTML(label="Revibed Results")
            
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
                return "", "", "", "", "", "", gr.update(choices=[], visible=False), "Please fill in minimum required fields.", gr.update(interactive=False)
            
            def extract_from_upload(image_file):
                return self.extract_text_from_upload(image_file)
            
            def perform_search_wrapper(tracks, artist, album, catalog, selected_track):
                # Show live status when search starts
                gr.update(value="🔍 Search started...", visible=True)
                
                # Use the progressive search generator
                search_generator = self.perform_search_progressive(tracks, artist, album, catalog, selected_track)
                
                # Get the final result from the generator
                final_result = None
                for result in search_generator:
                    final_result = result
                    # Each intermediate result is: (digital_html, discogs_html, revibed_html, status, release_choices, marketplace_update)
                    yield (
                        result[0],  # digital_html
                        result[1],  # discogs_html  
                        result[2],  # revibed_html
                        gr.update(value=result[3], visible=True),  # live_status
                        gr.update(choices=result[4], value=result[4][0] if result[4] else None),  # release_choices with proper update
                        result[5]   # marketplace_group visibility
                    )
                
                # Final update with complete results
                if final_result:
                    # Show results summary
                    digital_count = len([r for r in self.current_results['digital'] if self._is_valid_result(r)])
                    discogs_count = len(self.current_results['discogs'])
                    revibed_count = len([r for r in self.current_results['revibed'] if self._is_valid_result(r)])
                    
                    summary_html = f"""
                    <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 10px 0;">
                        <h3 style="margin: 0 0 10px 0;">🎯 Search Results Summary</h3>
                        <p style="margin: 5px 0;">Digital Platforms: <strong>{digital_count} results</strong></p>
                        <p style="margin: 5px 0;">Discogs Releases: <strong>{discogs_count} releases</strong></p>
                        <p style="margin: 5px 0;">Revibed: <strong>{revibed_count} results</strong></p>
                    </div>
                    """
                    
                    yield (
                        final_result[0],  # digital_html
                        final_result[1],  # discogs_html
                        final_result[2],  # revibed_html
                        gr.update(value="✅ Search complete!", visible=True),  # live_status
                        gr.update(choices=final_result[4], value=final_result[4][0] if final_result[4] else None),  # release_choices with proper update
                        final_result[5]   # marketplace_group visibility
                    )
            
            def load_marketplace_offers(selected_release_idx):
                if selected_release_idx is None or not self.current_results['discogs']:
                    return "Please select a release first."
                
                try:
                    # Find the release by matching the dropdown text
                    for i, release in enumerate(self.current_results['discogs']):
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
                outputs=[tracks_input, artist_input, album_input, catalog_input, extraction_status, camera_extraction_status, track_selector, search_status, search_btn]
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
            
            # Search functionality - generator for real-time updates
            search_btn.click(
                perform_search_wrapper,
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
    gem_finder = GradioGemFinder()
    interface = gem_finder.create_interface()
    
    # Launch with similar settings to Streamlit
    interface.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        debug=True,
        show_error=True
    )

if __name__ == "__main__":
    main()
