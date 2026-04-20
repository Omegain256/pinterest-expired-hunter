from apify_client import ApifyClient
from dotenv import load_dotenv

def discover_profiles(niche: str, max_results: int = 50) -> list[str]:
    """
    Search Google via Apify to find Pinterest profiles.
    """
    profiles = set()
    import os
    
    # Load environment variables from .env
    load_dotenv()
    api_token = os.getenv("APIFY_TOKEN")
    
    print(f"[*] [APIFY-v2] Discovering Pinterest profiles for: '{niche}'")
    
    if not api_token or api_token == "MISSING":
        print("[!] ERROR: APIFY_TOKEN environment variable is missing in .env. Search will fail.")
        return []

    try:
        client = ApifyClient(api_token)
        dork_query = f'site:pinterest.com "about" "website" "{niche}"'
        print(f"[*] [APIFY-v2] Executing Scraper: {dork_query}")
        
        run = client.actor("apify/google-search-scraper").call(
            run_input={
                "queries": dork_query,
                "maxPagesPerQuery": (max_results // 10) + 1,
                "resultsPerPage": min(100, max_results + 10)
            }
        )
        
        items = client.dataset(run["defaultDatasetId"]).list_items().items
        urls = [item.get("url") for item in items[0].get("organicResults", [])] if items else []
        
        for url in urls:
            if "pinterest.com/" in url:
                # Standardize to just the profile root URL
                # e.g., 'https://www.pinterest.com/cattydot/fitness-website/' -> 'cattydot'
                try:
                    username = url.split("pinterest.com/")[1].split("/")[0]
                    if username in ["pin", "ideas", "search", "explore"]:
                        continue # Ignore system pages
                    
                    cleaned_url = f"https://www.pinterest.com/{username}/"
                    profiles.add(cleaned_url)
                    print(f" Found Profile: {cleaned_url}")
                except Exception:
                    continue
                    
            if len(profiles) >= max_results:
                break
                
    except Exception as e:
        print(f"[!] Apify API Error: {e}")

    profile_list = list(profiles)
    print(f"[*] Found {len(profile_list)} authentic Pinterest profiles to check.")
    return profile_list

if __name__ == "__main__":
    found = discover_profiles("fitness", max_results=10)
    for p in found:
        print(p)
