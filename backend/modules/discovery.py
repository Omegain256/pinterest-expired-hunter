import os
from apify_client import ApifyClient
from dotenv import load_dotenv
from urllib.parse import urlparse

def get_apify_client():
    load_dotenv()
    api_token = os.getenv("APIFY_TOKEN")
    if not api_token or api_token == "MISSING":
        print("[!] ERROR: APIFY_TOKEN missing in .env")
        return None
    return ApifyClient(api_token)

def discover_profiles(niche: str, max_results: int = 50) -> list[str]:
    """
    Search Google via Apify to find Pinterest profiles.
    """
    profiles = set()
    client = get_apify_client()
    if not client: return []

    print(f"[*] [GOOGLE-GSS] Discovering Pinterest profiles for: '{niche}'")

    try:
        dork_query = f'site:pinterest.com "about" "website" "{niche}"'
        run = client.actor("apify/google-search-scraper").call(
            run_input={
                "queries": dork_query,
                "maxPagesPerQuery": (max_results // 10) + 1,
                "resultsPerPage": min(100, max_results + 10)
            }
        )
        
        items = client.dataset(run["defaultDatasetId"]).list_items().items
        # Organic results are often inside items[0]
        result_set = items[0].get("organicResults", []) if items else []
        
        for item in result_set:
            url = item.get("url", "")
            if "pinterest.com/" in url:
                try:
                    parts = url.split("pinterest.com/")[1].split("/")
                    username = parts[0]
                    if username in ["pin", "ideas", "search", "explore", "business"]:
                        continue
                    
                    cleaned_url = f"https://www.pinterest.com/{username}/"
                    profiles.add(cleaned_url)
                except: continue
                    
            if len(profiles) >= max_results: break
                
    except Exception as e:
        print(f"[!] Apify Google Search Error: {e}")

    profile_list = list(profiles)
    print(f"[*] Found {len(profile_list)} unique profiles.")
    return profile_list

def discover_domains_from_pins(niche: str, max_results: int = 50) -> list[dict]:
    """
    Search Pinterest Pins via Apify and extract unique destination domains.
    Returns a list of dicts: {'domain': str, 'profile_url': str}
    """
    client = get_apify_client()
    if not client: return []

    print(f"[*] [PINTEREST-NATIVE] Discovering Pins for: '{niche}'")
    domains_found = {} # domain -> profile_url

    try:
        # Use apify/pinterest-scraper for native search
        run = client.actor("apify/pinterest-scraper").call(
            run_input={
                "searchKeywords": niche,
                "maxPins": max_results * 2, # Scrape more pins because many share domains
                "proxyConfiguration": {"useApifyProxy": True}
            }
        )
        
        items = client.dataset(run["defaultDatasetId"]).list_items().items
        
        for item in items:
            link = item.get("link") or item.get("destinationUrl")
            if not link or "pinterest.com" in link: continue
            
            # Extract domain
            try:
                parsed = urlparse(link)
                domain = parsed.netloc.replace("www.", "").lower()
                if domain and domain not in domains_found:
                    domains_found[domain] = item.get("link") or f"https://www.pinterest.com/pin/{item.get('id')}/"
                    print(f" New Domain found from Pin: {domain}")
            except: continue
            
            if len(domains_found) >= max_results: break
            
    except Exception as e:
        print(f"[!] Apify Pinterest Search Error: {e}")

    # Convert to the expected format for main.py
    return [{"domain": d, "profile_url": p} for d, p in domains_found.items()]
