import time
import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def discover_profiles(niche: str, max_results: int = 50) -> list[str]:
    """
    Search DuckDuckGo using Playwright to bypass API blocks.
    """
    profiles = set()
    queries = [
        f'site:pinterest.com "about" "website" "{niche}"',
    ]
    
    print(f"[*] Discovering Pinterest profiles for niche: '{niche}' using Playwright (DDG)...")
    
    from googlesearch import search
    import time
    
    try:
        # Use native Google Dorking
        dork_query = f'site:pinterest.com "about" "website" "{niche}"'
        print(f"[*] Executing Google Search: {dork_query}")
        
        # We grab roughly 15 items by default to prevent instant IP ban from Google Captchas
        for url in search(dork_query, num_results=max_results, sleep_interval=3):
            if "pinterest.com" in url:
                url = "http://" + url.strip().split('/')[-1] if not url.startswith("http") else url
                cleaned_url = url.split("?")[0]
                if not cleaned_url.endswith("/"):
                    cleaned_url += "/"
                    
                profiles.add(cleaned_url)
                print(f" Found Profile: {cleaned_url}")
                
            if len(profiles) >= max_results:
                break
                
    except Exception as e:
        print(f"[!] Google Search Error: {e}")

    profile_list = list(profiles)
    print(f"[*] Found {len(profile_list)} authentic Pinterest profiles to check.")
    return profile_list

if __name__ == "__main__":
    found = discover_profiles("fitness", max_results=10)
    for p in found:
        print(p)
