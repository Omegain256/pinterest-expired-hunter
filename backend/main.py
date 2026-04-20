from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os

# Import our custom modules
from modules.discovery import discover_profiles
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
    max_results: int = 10

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
    return {"status": "Pinterest Hunter Backend is Running", "version": "1.0"}

@app.post("/api/search", response_model=SearchResponse)
def run_search(request: SearchRequest):
    print(f"[*] Starting API search for niche: {request.niche}")
    
    profiles = discover_profiles(request.niche, max_results=request.max_results)
    
    if not profiles:
        return SearchResponse(status="success", results=[], message="No profiles found.")

    valid_opportunities = []

    for profile in profiles:
        profile_data = extract_profile_data(profile)
        website = profile_data.get("website")
        
        if not website:
            continue
            
        domain_data = check_domain_status(website)
        score = score_opportunity(profile_data, domain_data)
        
        # Keep targets that have dead DNS or Score >= 0 to ensure the user sees results
        is_viable = score >= 0 or domain_data.get('dns_dead', False)
        
        if is_viable:
            opp = Opportunity(
                profile_url=profile,
                linked_website=website,
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
