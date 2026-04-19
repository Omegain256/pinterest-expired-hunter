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
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            page = context.new_page()

            for query in queries:
                print(f"[*] Executing query: {query}")
                # Use DuckDuckGo Lite (no js required, heavily text based)
                import urllib.parse
                encoded_query = urllib.parse.quote_plus(query)
                search_url = f"https://lite.duckduckgo.com/lite/?q={encoded_query}"
                page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
                
                # Allow minor delay to simulate human load
                page.wait_for_timeout(2000)
                
                # Extract URLs
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                
                # Check for rate limiting
                if "duckduckgo.com" not in page.url and "lite" not in html:
                    print("  [!] Possible DDG Rate Limit hit.")
                    
                for a in soup.find_all('a', class_='result-url'):
                    url = a.get('href', '')
                    if "pinterest.com" in url:
                        url = "http://" + url.strip().split('/')[-1] if not url.startswith("http") else url
                        
                        cleaned_url = url.split("?")[0] # remove query params
                        if not cleaned_url.endswith("/"):
                            cleaned_url += "/"
                            
                        profiles.add(cleaned_url)
                        print(f" Found Profile: {cleaned_url}")
                        
                        if len(profiles) >= max_results:
                            break
                            
                time.sleep(random.uniform(2.0, 4.0))

            browser.close()
            
    except Exception as e:
        print(f"[!] DDG Playwright Search Error: {e}")

    profile_list = list(profiles)
        
    print(f"[*] Found {len(profile_list)} unique Pinterest profiles to check.")
    return profile_list

if __name__ == "__main__":
    found = discover_profiles("fitness", max_results=10)
    for p in found:
        print(p)
