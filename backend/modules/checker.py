import socket
import whois
import dns.resolver
from datetime import datetime
from urllib.parse import urlparse

def clean_domain(url: str) -> str:
    """Extracts the base domain from a full URL."""
    try:
        if not url.startswith("http"):
            url = "http://" + url
        parsed = urlparse(url)
        domain = parsed.netloc
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.lower()
    except:
        return ""

def check_dns(domain: str) -> bool:
    """Returns True if the domain appears to have dead DNS / does not resolve."""
    try:
        # Check A record
        dns.resolver.resolve(domain, 'A')
        return False  # DNS is alive
    except:
        pass
    
    try:
        # Fallback to standard socket resolution
        socket.gethostbyname(domain)
        return False
    except:
        return True  # Truly dead DNS

def check_whois(domain: str) -> dict:
    """
    Returns domain status and age.
    If exact expiry can't be fetched, relies heavily on DNS.
    """
    result = {
        "domain": domain,
        "status": "UNKNOWN",
        "days_left": None,
        "age_years": 0
    }
    
    try:
        w = whois.whois(domain)
        
        # Calculate Age
        creation_date = w.creation_date
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
            
        if isinstance(creation_date, datetime):
            age_days = (datetime.now() - creation_date).days
            result["age_years"] = round(age_days / 365.25, 1)

        # Calculate Expiry
        exp_date = w.expiration_date
        if isinstance(exp_date, list):
            exp_date = exp_date[0]
            
        if isinstance(exp_date, datetime):
            days_left = (exp_date - datetime.now()).days
            result["days_left"] = days_left
            
            if days_left < 0:
                result["status"] = "EXPIRED"
            elif days_left < 30:
                result["status"] = "EXPIRING_SOON"
            else:
                result["status"] = "ACTIVE"
        else:
            # If we couldn't parse expiration, and DNS is dead, it MIGHT be available
            if check_dns(domain):
                result["status"] = "POTENTIALLY_AVAILABLE (Dead DNS)"
            
    except Exception as e:
        print(f"  [!] WHOIS lookup failed for {domain}: {e}")
        if check_dns(domain):
            result["status"] = "POTENTIALLY_AVAILABLE (Dead DNS)"

    return result

def check_domain_status(url: str) -> dict:
    """Facade function for the full checking pipeline."""
    domain = clean_domain(url)
    if not domain:
        return {"domain": "", "status": "INVALID", "days_left": None, "age_years": 0, "dns_dead": True}
        
    dns_dead = check_dns(domain)
    whois_data = check_whois(domain)
    
    whois_data["dns_dead"] = dns_dead
    
    # Override status if DNS is completely dead and Whois is ambiguous
    if dns_dead and whois_data["status"] == "UNKNOWN":
        whois_data["status"] = "POTENTIALLY_AVAILABLE"

    return whois_data

if __name__ == "__main__":
    print(check_domain_status("https://thiswebsitedoesnotexist99923812.com"))
