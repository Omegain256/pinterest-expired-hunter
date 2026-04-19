import re
import json
import time
import random
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

def extract_profile_data(profile_url: str) -> dict:
    """
    Given a Pinterest about page URL, use Playwright to extract:
    - website domain (external URL)
    - follower count
    - monthly views
    """
    print(f"[*] Extracting data for: {profile_url}")
    result = {
        "profile_url": profile_url,
        "website": None,
        "followers": 0,
        "monthly_views": 0
    }

    try:
        with sync_playwright() as p:
            # Stealth flags
            args = [
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-setuid-sandbox'
            ]
            browser = p.chromium.launch(headless=True, args=args)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={"width": 1280, "height": 800},
                java_script_enabled=True,
                bypass_csp=True,
            )
            # Override navigator.webdriver
            context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            page = context.new_page()
            # Random delay before hitting Pinterest
            time.sleep(random.uniform(1.0, 3.0))
            
            page.goto(profile_url, timeout=30000, wait_until="domcontentloaded")
            
            # Allow some dynamic content to render
            page.wait_for_timeout(3000)
            
            html = page.content()
            browser.close()

            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, "html.parser")

            # Strategy 1: Find JSON data blobs (often contains detailed profile info)
            scripts = soup.find_all("script", {"id": "__PWS_DATA__"})
            found_website = None
            found_followers = 0
            found_views = 0
            
            if scripts:
                try:
                    data = json.loads(scripts[0].string)
                    # Deep dive into the dict structure - usually under props.initialReduxState.users or similar
                    # Since we don't know exact tree structure offhand, we can convert dict to string and use regex,
                    # or do a recursive search. Let's do a regex on the raw string for resilience.
                    raw_data_str = scripts[0].string
                    
                    # Followers regex: "follower_count": 1234
                    f_match = re.search(r'"follower_count"\s*:\s*(\d+)', raw_data_str)
                    if f_match:
                        found_followers = int(f_match.group(1))
                        
                    # Monthly views regex: "monthly_views": 12345
                    v_match = re.search(r'"monthly_views"\s*:\s*(\d+)', raw_data_str)
                    if v_match:
                        found_views = int(v_match.group(1))
                        
                except Exception as e:
                    print(f"  [!] JSON blob extraction error: {e}")

            # Strategy 2: Extract all external URLs to find the linked website
            # Oftentimes, the user's website is in an 'a' tag with rel="nofollow", or inside the JSON
            # We look for all http/https links that do NOT have pinterest.com
            urls = []
            for link in soup.find_all("a", href=True):
                href = link['href']
                if href.startswith("http") and "pinterest.com" not in href:
                    urls.append(href)
                    
            if not urls:
                # Also check meta tags or scripts if pure a tags are missing
                json_ld_scripts = soup.find_all("script", type="application/ld+json")
                for script in json_ld_scripts:
                    text = script.string or ""
                    extracted_urls = re.findall(r'https?://(?:www\.)?(?!pinterest\.com)[^\s"\'<>\\]+', text)
                    if extracted_urls:
                        urls.extend(extracted_urls)

            # Pick the most likely website link (first external)
            if urls:
                found_website = urls[0]
            
            result["website"] = found_website
            result["followers"] = found_followers
            result["monthly_views"] = found_views

    except Exception as e:
        print(f"[!] Extraction Error for {profile_url}: {e}")

    return result

if __name__ == "__main__":
    # Test
    data = extract_profile_data("https://www.pinterest.com/tasty/about/")
    print(data)
