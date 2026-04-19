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
                search_url = f"https://html.duckduckgo.com/html/?q={query}"
                page.goto(search_url, timeout=30000, wait_until="domcontentloaded")
                
                # Extract URLs
                html = page.content()
                soup = BeautifulSoup(html, "html.parser")
                for a in soup.find_all('a', class_='result__url'):
                    url = a.get('href', '')
                    if "pinterest.com" in url:
                        url = "http://" + url.strip().split('/')[-1] if not url.startswith("http") else url
                        
                        cleaned_url = url.split("?")[0] # remove query params
                        # Ensure it points to about
                        if not cleaned_url.endswith("/"):
                            cleaned_url += "/"
                        if not cleaned_url.endswith("about/"):
                            cleaned_url += "about/"
                            
                        profiles.add(cleaned_url)
                        
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
