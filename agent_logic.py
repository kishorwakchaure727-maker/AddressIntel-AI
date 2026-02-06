import re
import time
import json
from urllib.parse import urljoin, urlparse

from playwright.sync_api import sync_playwright
from openai import OpenAI
from duckduckgo_search import DDGS

class AgenticExtractor:
    def __init__(self, openai_api_key=None, proxy_url=None):
        self.openai_api_key = openai_api_key
        self.proxy_url = proxy_url
        self.client = None
        if self.openai_api_key:
            self.client = OpenAI(api_key=self.openai_api_key)

    # ... (rest of methods)

    def process_url(self, url):
        extracted_data = []
        
        with sync_playwright() as p:
            launch_args = {"headless": True}
            if self.proxy_url:
                print(f"Using Proxy: {self.proxy_url}")
                launch_args["proxy"] = {"server": self.proxy_url}
                
            browser = p.chromium.launch(**launch_args)
            context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36")
            page = context.new_page()
            
            try:
                print(f"Navigating to {url}")
                page.goto(url, timeout=30000, wait_until="networkidle")
                
                # 1. Scan Homepage
                content = page.inner_text("body")
                
                # 2. Look for keywords to click
                contact_words = ["contact", "location", "offices", "where to buy", "about us"]
                found_links = []
                
                # Get all links
                links = page.query_selector_all("a")
                for link in links:
                    txt = link.inner_text().lower()
                    href = link.get_attribute("href")
                    if href and any(w in txt for w in contact_words):
                        full_url = urljoin(url, href)
                        found_links.append(full_url)
                
                # Prioritize "contact" and "locations"
                targets = sorted(list(set(found_links)), key=lambda x: "contact" in x or "location" in x, reverse=True)[:3]
                targets.insert(0, url) # Check homepage first/again with LLM
                
                processed_targets = set()

                for target in targets:
                    if target in processed_targets: continue
                    processed_targets.add(target)
                    
                    print(f"Checking page: {target}")
                    try:
                        if target != url:
                            page.goto(target, timeout=20000)
                            time.sleep(2) # Wait for JS renders
                        
                        # --- DEEP INTERACTION UPGRADE ---
                        # 1. Handle Dropdowns/Selects for "Location"
                        # Try to find select elements or buttons with "Select" and click them
                        try:
                            dropdowns = page.query_selector_all("select, button[aria-haspopup='true']")
                            for dd in dropdowns:
                                txt = dd.inner_text().lower()
                                if "location" in txt or "country" in txt or "select" in txt:
                                    # Just try to click to expand, might expose text
                                    dd.click(timeout=1000)
                                    time.sleep(0.5)
                        except:
                            pass
                            
                        # 2. Extract Text from Main Body
                        visible_text = page.inner_text("body")
                        
                        # 3. Extract Text from IFrames (Maps/Embedded Finders)
                        frames = page.frames
                        for frame in frames:
                            try:
                                # Skip hidden/tracking frames roughly
                                if frame.name and ("google" in frame.name or "map" in frame.name):
                                    frame_text = frame.inner_text("body")
                                    if len(frame_text) > 50:
                                        visible_text += "\n [MAP FRAME DATA] \n" + frame_text
                            except:
                                pass
                                
                        # LLM Extraction
                        addresses = self._get_llm_response(visible_text)
                        
                        if addresses:
                            for addr in addresses:
                                # Validation: Must have at least street or city
                                if addr.get("street1") or addr.get("city"):
                                    # Search refinement
                                    final_addr = self._search_missing_info(addr)
                                    final_addr["source_url"] = target
                                    extracted_data.append(final_addr)
                                    
                    except Exception as e:
                        print(f"Error visiting {target}: {e}")
                        continue
                        
            except Exception as e:
                print(f"Failed to process {url}: {e}")
            finally:
                browser.close()
                
        return extracted_data

if __name__ == "__main__":
    # Test stub
    pass
