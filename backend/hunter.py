import argparse
import pandas as pd
from modules.discovery import discover_profiles
from modules.extractor import extract_profile_data
from modules.checker import check_domain_status
from modules.scorer import score_opportunity

def execute_pipeline(niche: str, max_results: int, output_file: str):
    print(f"\n{'='*50}")
    print(f"PINTEREST EXPIRED HUNTER - NICHE: {niche.upper()}")
    print(f"{'='*50}\n")
    
    # Phase 1: Discovery
    profiles = discover_profiles(niche, max_results=max_results)
    if not profiles:
        print("[!] No profiles found. Exiting.")
        return

    results = []

    # Phase 2-5: Extraction, Checking, Scoring
    for profile in profiles:
        print(f"\n[-] Processing: {profile}")
        
        # Phase 2: Extraction
        profile_data = extract_profile_data(profile)
        website = profile_data.get("website")
        
        if not website:
            print("  [>] No external website found. Skipping.")
            continue
            
        print(f"  [>] Extracted Website: {website}")
        print(f"  [>] Followers: {profile_data.get('followers')} | Views: {profile_data.get('monthly_views')}")

        # Phase 3 & 4: Checker (WHOIS + DNS)
        domain_data = check_domain_status(website)
        print(f"  [>] Domain Status: {domain_data.get('status')}")
        print(f"  [>] DNS Dead: {domain_data.get('dns_dead')}")
        
        # Phase 5: Scoring
        score = score_opportunity(profile_data, domain_data)
        print(f"  [>] Opportunity Score: {score}")

        # Accumulate
        results.append({
            "Profile URL": profile,
            "Linked Website": website,
            "Domain Status": domain_data.get("status"),
            "DNS Dead": domain_data.get("dns_dead"),
            "Followers": profile_data.get("followers"),
            "Monthly Views": profile_data.get("monthly_views"),
            "Domain Age (Yrs)": domain_data.get("age_years"),
            "Score": score
        })
        
    if results:
        # Sort by score descending
        df = pd.DataFrame(results)
        df = df.sort_values(by="Score", ascending=False)
        
        df.to_csv(output_file, index=False)
        print(f"\n{'='*50}")
        print(f"[SUCCESS] Exported {len(df)} records to {output_file}")
        print(f"{'='*50}\n")
    else:
        print("\n[!] No valid opportunities found to export.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pinterest Expired Domain Hunter")
    parser.add_argument("--niche", type=str, required=True, help="Niche keyword to search for (e.g., 'fitness', 'cooking')")
    parser.add_argument("--max", type=int, default=20, help="Max profiles to attempt to discover")
    parser.add_argument("--out", type=str, default="opportunities.csv", help="Output CSV filename")
    
    args = parser.parse_args()
    
    execute_pipeline(args.niche, args.max, args.out)
