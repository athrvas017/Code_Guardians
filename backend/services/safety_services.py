import requests
import validators

BLACKLIST = [
    "phishing-site.com",
    "fakebank.xyz",
    "malware-test.net"
]

def blacklist_check(url):
    return any(site in url for site in BLACKLIST)

def google_safe_browsing(url, api_key):
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

    response = requests.post(api_url, json=payload)
    return response.json() != {}

def check_url_safety(url, google_key):
    if not validators.url(url):
        return "Invalid URL"

    if blacklist_check(url):
        return "Blacklisted URL"

    if google_safe_browsing(url, google_key):
        return "Malicious (Google Safe Browsing)"

    return "Safe"

def check_url_Safety(url, api_key):
    if not validators.url(url):
        return "Invalid URL"

    api_url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"

    payload = {
        "client": {"clientId": "phishing-app", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }

    r = requests.post(api_url, json=payload)
    return "Unsafe" if r.json() else "Safe"