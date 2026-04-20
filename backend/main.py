from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load .env file at the very top level
load_dotenv()

# Import our custom modules
from modules.discovery import discover_profiles, discover_domains_from_pins
from modules.extractor import extract_profile_data
from modules.checker import check_domain_status
from modules.scorer import score_opportunity

app = FastAPI(title="Pinterest Hunter API")

# Add CORS so Vercel can access it
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SearchRequest(BaseModel):
    niche: str
    max_results: int = 20
    mode: str = "profiles" # 'profiles' or 'pins'
    min_followers: int = 0

class Opportunity(BaseModel):
    profile_url: str
    linked_website: str
    domain_status: str
    dns_dead: bool
    followers: int
    monthly_views: int
    domain_age: float
    score: int

class SearchResponse(BaseModel):
    status: str
    results: List[Opportunity]
    message: Optional[str] = None

@app.get("/")
def read_root():
    return {"status": "Pinterest Hunter Backend is Running", "version": "2.0-Multisource"}

@app.post("/api/search", response_model=SearchResponse)
def run_search(request: SearchRequest):
    print(f"[*] Starting API search for niche: {request.niche} [Mode: {request.mode}]")
    
    # Mode 1: Search Profiles (Google Dorking)
    if request.mode == "profiles" or request.mode == "both":
        raw_targets = [{"url": p, "domain": None} for p in discover_profiles(request.niche, max_results=request.max_results)]
    # Mode 2: Search Pin Links (Native Pinterest)
    else:
        # returns list of {'domain': str, 'profile_url': str}
        raw_targets = [{"url": t['profile_url'], "domain": t['domain']} for t in discover_domains_from_pins(request.niche, max_results=request.max_results)]
    
    if not raw_targets:
        return SearchResponse(status="success", results=[], message="No results found.")

    valid_opportunities = []

    for target in raw_targets:
        profile_url = target["url"]
        
        # 1. Extraction (Scrape Pinterest Profile)
        profile_data = extract_profile_data(profile_url)
        
        # Apply min_followers filter
        if profile_data.get("followers", 0) < request.min_followers:
            print(f"  [>] Skipping {profile_url}: Too few followers ({profile_data.get('followers')})")
            continue

        # Determine target website
        # If we came from Pin-Mode, we already have the domain. If not, extract it.
        website = target.get("domain") or profile_data.get("website")
        
        if not website:
            continue
            
        # 2. Check & Score
        domain_data = check_domain_status(website)
        score = score_opportunity(profile_data, domain_data)
        
        # Filter: ONLY keep if DNS is dead or status is specifically EXPIRED/AVAILABLE
        is_expired = domain_data.get("dns_dead", False) or domain_data.get("status") in ["EXPIRED", "POTENTIALLY_AVAILABLE", "EXPIRING_SOON"]
        is_live = domain_data.get("is_live", False)
        
        if is_expired and not is_live:
            opp = Opportunity(
                profile_url=profile_url,
                linked_website=domain_data.get("domain", website),
                domain_status=domain_data.get("status", "UNKNOWN"),
                dns_dead=domain_data.get("dns_dead", False),
                followers=profile_data.get("followers", 0),
                monthly_views=profile_data.get("monthly_views", 0),
                domain_age=domain_data.get("age_years", 0),
                score=score
            )
            valid_opportunities.append(opp)
            
    # Sort strictly by score highest to lowest
    valid_opportunities.sort(key=lambda x: x.score, reverse=True)
    
    return SearchResponse(
        status="success",
        results=valid_opportunities,
        message=f"Found {len(valid_opportunities)} high-value opportunities."
    )

if __name__ == "__main__":
    import uvicorn
    # Vercel & Render use PORT env var
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
