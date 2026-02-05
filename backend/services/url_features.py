import re
from urllib.parse import parse_qs, urlparse

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix, hstack
from sklearn.feature_extraction.text import TfidfVectorizer


# -------------------------
# URL feature engineering
# -------------------------
SUSPICIOUS_KEYWORDS = [
    "login", "verify", "secure", "account", "update", "free", "bonus", "win",
    "bank", "password", "signin", "support", "security", "confirm"
]

UNUSUAL_TLDS = {
    "xyz", "top", "tk", "gq", "ml", "ga", "cf", "ru", "cn", "icu", "biz", "info"
}

KNOWN_LEGIT_DOMAINS = {
    "google.com", "facebook.com", "amazon.com", "amazon.in",
    "youtube.com", "drive.google.com", "microsoft.com", "paypal.com"
}

BRAND_DOMAINS = [
    "google", "facebook", "amazon", "microsoft", "paypal", "youtube"
]


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            ins = curr[j - 1] + 1
            dele = prev[j] + 1
            sub = prev[j - 1] + (0 if ca == cb else 1)
            curr.append(min(ins, dele, sub))
        prev = curr
    return prev[-1]


def _extract_domain_parts(hostname: str) -> tuple[str, str, int]:
    parts = [p for p in hostname.split(".") if p]
    if len(parts) >= 2:
        sld = parts[-2]
        tld = parts[-1]
        subdomains = max(0, len(parts) - 2)
        return sld, tld, subdomains
    return hostname, "", 0


def _is_ip_address(hostname: str) -> int:
    if not hostname:
        return 0
    return 1 if re.fullmatch(r"(?:\d{1,3}\.){3}\d{1,3}", hostname) else 0


def _keyword_count(text: str) -> int:
    lowered = text.lower()
    return sum(1 for kw in SUSPICIOUS_KEYWORDS if kw in lowered)


def _brand_similarity(sld: str) -> tuple[float, int]:
    if not sld:
        return 1.0, 0
    min_norm = 1.0
    for brand in BRAND_DOMAINS:
        dist = _levenshtein(sld, brand)
        norm = dist / max(len(sld), len(brand))
        if norm < min_norm:
            min_norm = norm
    return min_norm, 1 if min_norm <= 0.25 else 0


def _url_features(url: str) -> list[float]:
    parsed = urlparse(url if "://" in url else f"http://{url}")
    hostname = (parsed.hostname or "").lower()
    sld, tld, subdomains = _extract_domain_parts(hostname)

    url_len = len(url)
    num_dots = url.count(".")
    num_hyphens = url.count("-")
    num_digits = sum(ch.isdigit() for ch in url)
    num_letters = sum(ch.isalpha() for ch in url)
    digit_letter_ratio = num_digits / max(1, num_letters)

    path = parsed.path or ""
    query = parsed.query or ""
    num_params = len(parse_qs(query))
    num_subdirs = len([p for p in path.split("/") if p])

    has_https = 1 if parsed.scheme.lower() == "https" else 0
    has_ip = _is_ip_address(hostname)
    keyword_hits = _keyword_count(url)

    tld_is_unusual = 1 if tld in UNUSUAL_TLDS else 0
    tld_len = len(tld)

    is_known_legit = 1 if hostname in KNOWN_LEGIT_DOMAINS else 0

    brand_min_norm, brand_close = _brand_similarity(sld)

    return [
        url_len,
        num_dots,
        num_hyphens,
        num_digits,
        num_letters,
        digit_letter_ratio,
        subdomains,
        len(path),
        len(query),
        num_params,
        num_subdirs,
        has_https,
        has_ip,
        keyword_hits,
        tld_is_unusual,
        tld_len,
        is_known_legit,
        brand_min_norm,
        brand_close,
    ]


def build_feature_matrix(urls: pd.Series, vectorizer: TfidfVectorizer):
    text_features = vectorizer.transform(urls)
    numeric_features = np.array([_url_features(u) for u in urls], dtype=np.float32)
    numeric_sparse = csr_matrix(numeric_features)
    return hstack([text_features, numeric_sparse])
