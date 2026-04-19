def score_opportunity(profile_data: dict, domain_data: dict) -> int:
    """
    Scores the Pinterest profile + Domain opportunity.
    Max baseline score is ~100+. Higher is better.
    """
    score = 0
    
    followers = profile_data.get("followers", 0)
    views = profile_data.get("monthly_views", 0)
    domain_age = domain_data.get("age_years", 0)
    domain_status = domain_data.get("status", "")
    
    # 1. Follower Score (Up to 60 pts)
    # 1 follower = 0.05 pts
    f_score = min(followers / 1000 * 50, 60)
    score += f_score
    
    # 2. Monthly Views Score (Up to 40 pts)
    v_score = min(views / 10000 * 20, 40)
    score += v_score
    
    # 3. Domain Age Score
    if domain_age > 10:
        score += 30
    elif domain_age > 5:
        score += 20
    elif domain_age > 2:
        score += 10
        
    # 4. Status Multiplier / Filter
    if domain_status == "ACTIVE":
        score = 0
    elif domain_status == "EXPIRING_SOON":
        pass
    elif "EXPIRED" in domain_status or "AVAILABLE" in domain_status:
        # High value! Massive bonus
        score += 50
        
    return int(score)
