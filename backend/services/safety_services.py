import requests
import validators
from .url_ml_service import check_url_ml

BLACKLIST = [
    "phishing-site.com",
    "fakebank.xyz",
    "malware-test.net"
]

def blacklist_check(url):
    return any(site in url for site in BLACKLIST)

def google_safe_browsing(url, api_key):
    if not api_key:
        return False
        
    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"

    payload = {
        "client": {
            "clientId": "url-project",
            "clientVersion": "1.0"
        },
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    try:
        response = requests.post(api_url, json=payload)
        return response.json() != {}
    except:
        return False

def check_url_safety(url, google_key):
    
    if not validators.url(url):
        return "❌ Invalid URL"

    if blacklist_check(url):
        return "⛔ Blacklisted URL"

    ml_result = check_url_ml(url)
    
    api_result = "✅ Safe (Google API)"
    if google_key:
        if google_safe_browsing(url, google_key):
            api_result = "🚨 Unsafe (Google Safe Browsing)"
    else:
        api_result = "⚠️ Google API Key Missing"

    if "Phishing" in ml_result or "Unsafe" in api_result or "Blacklisted" in ml_result:
        return f"{ml_result} | {api_result}"
    
    return "✅ Safe URL (Verified by ML & Google API)"

def check_url_Safety(url, api_key):
   
    if not validators.url(url):
        return "Invalid URL"
        
    ml_result = check_url_ml(url)
    if "Phishing" in ml_result:
        return "Unsafe"

    if api_key and google_safe_browsing(url, api_key):
        return "Unsafe"

    return "Safe"
