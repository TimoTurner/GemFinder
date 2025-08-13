"""
Gradio UI Helpers for GemFinder
Specialized components for enhanced user experience
"""

import gradio as gr
from typing import List, Dict, Any, Tuple, Optional
from ui_helpers import (
    get_user_location, filter_offers_by_currency, filter_offers_by_condition,
    CURRENCY_MAPPING, CONDITION_HIERARCHY, HIGH_QUALITY_CONDITIONS, parse_price
)
from scrape_search import scrape_discogs_marketplace_offers
from selenium_scraper import selenium_filter_offers_parallel

class GradioDiscogsMaketplace:
    """Enhanced Discogs marketplace component for Gradio"""
    
    def __init__(self):
        self.user_location = None
        self.offer_cache = {}
    
    def create_marketplace_interface(self, release_data: Dict) -> gr.Blocks:
        """Create marketplace interface for a specific release"""
        
        with gr.Blocks() as marketplace_interface:
            gr.Markdown(f"## Discogs Marketplace: {release_data.get('title', 'Unknown Release')}")
            
            # Location and filter controls
            with gr.Row():
                with gr.Column():
                    location_info = gr.Textbox(
                        label="Your Location",
                        value=self._get_location_string(),
                        interactive=False
                    )
                
                with gr.Column():
                    quality_filter = gr.Checkbox(
                        label="Show only VG+ or better",
                        value=False
                    )
                    
                    refresh_btn = gr.Button("🔄 Refresh Offers", variant="secondary")
            
            # Offers display
            offers_display = gr.HTML(label="Marketplace Offers")
            loading_status = gr.Textbox(
                label="Status",
                value="Click 'Load Offers' to search marketplace",
                interactive=False
            )
            
            load_offers_btn = gr.Button("Load Offers", variant="primary")
            
            # Event handlers
            def load_offers_handler(quality_only):
                return self.load_and_display_offers(release_data, quality_only)
            
            def refresh_offers_handler(quality_only):
                # Clear cache and reload
                release_id = release_data.get("id")
                if release_id in self.offer_cache:
                    del self.offer_cache[release_id]
                return self.load_and_display_offers(release_data, quality_only)
            
            def update_quality_filter(quality_only):
                # Re-filter existing offers without reloading
                return self.display_cached_offers(release_data, quality_only)
            
            load_offers_btn.click(
                load_offers_handler,
                inputs=[quality_filter],
                outputs=[offers_display, loading_status]
            )
            
            refresh_btn.click(
                refresh_offers_handler,
                inputs=[quality_filter],
                outputs=[offers_display, loading_status]
            )
            
            quality_filter.change(
                update_quality_filter,
                inputs=[quality_filter],
                outputs=[offers_display]
            )
        
        return marketplace_interface
    
    def _get_location_string(self) -> str:
        """Get formatted location string"""
        if not self.user_location:
            self.user_location = get_user_location()
        
        return f"{self.user_location.get('city', 'Unknown')}, {self.user_location['country']} ({self.user_location['currency']})"
    
    def load_and_display_offers(self, release_data: Dict, quality_only: bool) -> Tuple[str, str]:
        """Load offers with progress indication"""
        release_id = release_data.get("id")
        if not release_id:
            return "❌ Release ID not found", "Error: No release ID"
        
        try:
            # Check cache first
            if release_id not in self.offer_cache:
                # Load user location
                if not self.user_location:
                    self.user_location = get_user_location()
                
                # Scrape offers with selenium enhancement
                offers = scrape_discogs_marketplace_offers(
                    release_id, 
                    max_offers=10, 
                    user_country=self.user_location['country']
                )
                
                if offers:
                    # Enhance with Selenium for shipping availability
                    offers = selenium_filter_offers_parallel(
                        offers, 
                        self.user_location['country'], 
                        max_workers=5
                    )
                
                self.offer_cache[release_id] = offers
            
            offers = self.offer_cache[release_id]
            
            if not offers:
                return "📭 No marketplace offers found for this release.", "No offers found"
            
            # Filter offers
            filtered_offers = self._filter_offers(offers, quality_only)
            
            if not filtered_offers:
                quality_msg = " in VG+ or better condition" if quality_only else ""
                return f"No offers found in {self.user_location['currency']}{quality_msg}.", "No matching offers"
            
            # Display offers
            html_output = self._format_offers_html(filtered_offers)
            status_msg = f"Found {len(filtered_offers)} offers"
            
            return html_output, status_msg
            
        except Exception as e:
            return f"❌ Error loading offers: {str(e)}", f"Error: {str(e)}"
    
    def display_cached_offers(self, release_data: Dict, quality_only: bool) -> str:
        """Display cached offers with quality filter"""
        release_id = release_data.get("id")
        
        if release_id not in self.offer_cache:
            return "No cached offers. Click 'Load Offers' first."
        
        offers = self.offer_cache[release_id]
        filtered_offers = self._filter_offers(offers, quality_only)
        
        if not filtered_offers:
            quality_msg = " in VG+ or better condition" if quality_only else ""
            return f"No offers found in {self.user_location['currency']}{quality_msg}."
        
        return self._format_offers_html(filtered_offers)
    
    def _filter_offers(self, offers: List[Dict], quality_only: bool) -> List[Dict]:
        """Apply currency and quality filters to offers"""
        if not self.user_location:
            self.user_location = get_user_location()
        
        preferred_currency = self.user_location['currency']
        
        # Parse and filter offers
        parsed_offers = []
        for offer in offers:
            price_amount, price_currency = parse_price(offer.get('price', ''))
            shipping_amount, shipping_currency = parse_price(offer.get('shipping', ''))
            
            # Skip offers in different currencies
            if price_currency and price_currency != preferred_currency:
                continue
            
            # Skip invalid offers
            if price_amount <= 0:
                continue
            
            total_amount = price_amount + shipping_amount
            
            offer_copy = offer.copy()
            offer_copy.update({
                'price_amount': price_amount,
                'price_currency': price_currency,
                'shipping_amount': shipping_amount,
                'total_amount': total_amount
            })
            parsed_offers.append(offer_copy)
        
        # Apply quality filter
        if quality_only:
            parsed_offers = filter_offers_by_condition(parsed_offers, high_quality_only=True)
        
        # Sort by total price
        parsed_offers.sort(key=lambda x: x.get('total_amount', 0))
        
        return parsed_offers
    
    def _format_offers_html(self, offers: List[Dict]) -> str:
        """Format offers as HTML for display"""
        if not offers:
            return "No offers to display."
        
        html_output = f"<div style='max-height: 600px; overflow-y: auto;'>"
        
        for i, offer in enumerate(offers[:10], 1):
            price_amount = offer.get('price_amount', 0)
            price_currency = offer.get('price_currency', 'EUR')
            shipping_amount = offer.get('shipping_amount', 0)
            total_amount = offer.get('total_amount', price_amount + shipping_amount)
            
            condition = offer.get('condition', 'Unknown')
            seller = offer.get('seller', 'Unknown')
            seller_rating = offer.get('seller_rating', '')
            country = offer.get('country', '')
            offer_url = offer.get('offer_url', '#')
            
            # Clean up condition text
            clean_condition = condition.replace('Zustand des Tonträgers: ', '').replace('Zustand der Hülle: ', ' / ').strip()
            
            # Format prices
            try:
                price_str = f"{float(price_amount):.2f} {price_currency}"
                shipping_str = f"{float(shipping_amount):.2f} {price_currency}" if shipping_amount > 0 else "Free"
                total_str = f"{float(total_amount):.2f} {price_currency}"
            except (ValueError, TypeError):
                price_str = f"{price_amount} {price_currency}"
                shipping_str = str(shipping_amount) if shipping_amount else "Free"
                total_str = f"{total_amount} {price_currency}"
            
            # Quality indicator
            quality_score = CONDITION_HIERARCHY.get(clean_condition.split('\n')[0].split(' /')[0], 0)
            if quality_score >= 3:
                quality_icon = "💎"
            elif quality_score >= 1:
                quality_icon = "✨"
            else:
                quality_icon = "📦"
            
            html_output += f"""
            <div style="border: 1px solid #ddd; border-radius: 8px; padding: 12px; margin: 8px 0; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div style="flex: 1;">
                        <h4 style="margin: 0 0 5px 0;">
                            <a href="{offer_url}" target="_blank" style="text-decoration: none; color: #0066cc;">
                                #{i} - {total_str}
                            </a>
                            {quality_icon}
                        </h4>
                        <p style="margin: 2px 0; font-style: italic; color: #666;">{clean_condition}</p>
                        <p style="margin: 2px 0; color: #333;">
                            Seller: <strong>{seller}</strong> 
                            {f"({seller_rating})" if seller_rating else ""} 
                            {f"🌍 {country}" if country else ""}
                        </p>
                    </div>
                    <div style="text-align: right;">
                        <p style="margin: 0; font-weight: bold; color: #0066cc;">{price_str}</p>
                        <p style="margin: 0; font-size: 0.9em; color: #666;">+ {shipping_str} shipping</p>
                    </div>
                </div>
            </div>
            """
        
        html_output += "</div>"
        return html_output


class GradioSearchProgress:
    """Enhanced search progress component"""
    
    def __init__(self):
        self.search_state = {}
    
    def create_progress_interface(self) -> Tuple[gr.HTML, gr.Progress]:
        """Create progress tracking interface"""
        
        progress_display = gr.HTML(value="<div>Ready to search...</div>")
        progress_bar = gr.Progress()
        
        return progress_display, progress_bar
    
    def update_progress(self, stage: str, completed: int, total: int, platform: str = "") -> str:
        """Update progress display"""
        if stage == "digital":
            progress_text = f"Searching digital platforms... ({completed}/{total})"
            if platform:
                progress_text += f" - {platform}"
        elif stage == "secondary":
            progress_text = f"Searching Discogs and Revibed... ({completed}/{total})"
            if platform:
                progress_text += f" - {platform}"
        else:
            progress_text = f"{stage}... ({completed}/{total})"
        
        return f"""
        <div style="padding: 10px; background: #f0f8ff; border-radius: 8px; border-left: 4px solid #0066cc;">
            <p style="margin: 0; font-weight: bold;">🔍 {progress_text}</p>
        </div>
        """


def create_enhanced_results_display():
    """Create enhanced results display with tabs and filtering"""
    
    with gr.Blocks() as results_interface:
        
        # Results summary
        results_summary = gr.HTML(value="")
        
        # Main results tabs
        with gr.Tabs():
            
            # Digital results tab
            with gr.Tab("🎵 Digital Platforms"):
                digital_results = gr.HTML(label="Digital Results")
                
                # Platform filter
                with gr.Row():
                    platform_filter = gr.CheckboxGroup(
                        choices=["iTunes", "Beatport", "Bandcamp", "Traxsource"],
                        value=["iTunes", "Beatport", "Bandcamp", "Traxsource"],
                        label="Show Platforms"
                    )
            
            # Discogs tab with enhanced features
            with gr.Tab("📀 Discogs"):
                discogs_results = gr.HTML(label="Discogs Releases")
                
                # Discogs controls
                with gr.Row():
                    release_selector = gr.Dropdown(
                        label="Select Release for Offers",
                        choices=[],
                        interactive=True
                    )
                    show_offers_btn = gr.Button("Show Marketplace Offers", variant="secondary")
                
                # Marketplace offers
                marketplace_offers = gr.HTML(label="Marketplace Offers")
            
            # Revibed tab
            with gr.Tab("🎧 Revibed"):
                revibed_results = gr.HTML(label="Revibed Results")
    
    return results_interface


def create_mobile_responsive_css() -> str:
    """Create mobile-responsive CSS for better UX"""
    return """
    <style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        .gradio-container {
            padding: 10px !important;
        }
        
        .gradio-row {
            flex-direction: column !important;
        }
        
        .gradio-column {
            width: 100% !important;
            margin-bottom: 10px !important;
        }
        
        .gradio-button {
            width: 100% !important;
            margin: 5px 0 !important;
        }
        
        .gradio-textbox, .gradio-dropdown {
            width: 100% !important;
        }
    }
    
    /* Enhanced visual styling */
    .search-result-card {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 16px;
        margin: 10px 0;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .search-result-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.15);
    }
    
    .platform-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .price-tag {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 6px 16px;
        border-radius: 25px;
        font-weight: bold;
        font-size: 14px;
    }
    
    .progress-bar {
        width: 100%;
        height: 6px;
        background: #e0e0e0;
        border-radius: 3px;
        overflow: hidden;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
    }
    </style>
    """