// NetShield Extension - Phishing Analyzer Utility

// Common phishing keywords and phrases
const PHISHING_KEYWORDS = [
    // Urgency
    "urgent", "immediately", "action required", "act now", "expires today",
    "limited time", "final notice", "last chance", "deadline",

    // Account threats
    "verify your account", "confirm your identity", "update your information",
    "unusual activity", "suspicious activity", "security alert", "account suspended",
    "account locked", "password expired", "verify immediately",

    // Money/Prizes
    "you have won", "congratulations", "claim your prize", "lottery winner",
    "inheritance", "million dollars", "free gift", "exclusive offer",

    // Credentials
    "enter your password", "login credentials", "social security",
    "bank account", "credit card", "pin number",

    // Authority impersonation
    "irs", "internal revenue", "microsoft support", "apple support",
    "amazon security", "paypal team", "netflix billing",

    // Generic threats
    "click here now", "click below", "click link", "verify now",
    "confirm now", "update now", "respond immediately"
];

// Suspicious sender patterns
const SUSPICIOUS_PATTERNS = [
    /no-?reply@/i,
    /support\d+@/i,
    /security[.-]?alert/i,
    /account[.-]?verify/i,
    /@.*\.xyz$/i,
    /@.*\.tk$/i,
    /@.*\.ml$/i,
    /\d{4,}@/i
];

// URL patterns that are often suspicious
const SUSPICIOUS_URL_PATTERNS = [
    /bit\.ly/i,
    /tinyurl/i,
    /t\.co/i,
    /goo\.gl/i,
    /\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/,  // IP addresses
    /-login\./i,
    /-verify\./i,
    /-secure\./i,
    /\.tk$/i,
    /\.ml$/i,
    /\.xyz$/i,
    /signin.*(?!google|microsoft|apple)/i
];

/**
 * Extract URLs from text
 * @param {string} text - Text to scan
 * @returns {string[]} Array of found URLs
 */
export function extractUrls(text) {
    const urlRegex = /https?:\/\/[^\s<>"{}|\\^`\[\]]+/gi;
    return text.match(urlRegex) || [];
}

/**
 * Analyze text for phishing indicators
 * @param {string} text - Email/message content
 * @returns {Object} Analysis result
 */
export function analyzePhishing(text) {
    const indicators = [];
    let riskScore = 0;
    const lowerText = text.toLowerCase();

    // Check for phishing keywords
    const foundKeywords = [];
    for (const keyword of PHISHING_KEYWORDS) {
        if (lowerText.includes(keyword.toLowerCase())) {
            foundKeywords.push(keyword);
            riskScore += 10;
        }
    }

    if (foundKeywords.length > 0) {
        indicators.push(`Suspicious phrases: "${foundKeywords.slice(0, 3).join('", "')}"`);
    }

    // Check for suspicious URL patterns
    const urls = extractUrls(text);
    const suspiciousUrls = [];

    for (const url of urls) {
        for (const pattern of SUSPICIOUS_URL_PATTERNS) {
            if (pattern.test(url)) {
                suspiciousUrls.push(url);
                riskScore += 20;
                break;
            }
        }
    }

    if (suspiciousUrls.length > 0) {
        indicators.push(`Suspicious URLs detected (${suspiciousUrls.length})`);
    }

    // Check for urgency language
    const urgencyWords = ["urgent", "immediately", "now", "asap", "quickly"];
    const urgencyCount = urgencyWords.filter(w => lowerText.includes(w)).length;
    if (urgencyCount >= 2) {
        indicators.push("High urgency language detected");
        riskScore += 15;
    }

    // Check for request for credentials
    const credentialWords = ["password", "login", "credentials", "ssn", "social security", "credit card", "bank account"];
    const credentialMatches = credentialWords.filter(w => lowerText.includes(w));
    if (credentialMatches.length > 0) {
        indicators.push("Requests for sensitive information detected");
        riskScore += 25;
    }

    // Check for threat/fear tactics
    if (lowerText.includes("suspend") || lowerText.includes("locked") ||
        lowerText.includes("terminated") || lowerText.includes("deleted")) {
        indicators.push("Account threat language detected");
        riskScore += 15;
    }

    // Check for impersonation
    const brands = ["microsoft", "apple", "google", "amazon", "paypal", "netflix", "facebook", "instagram"];
    const mentionedBrands = brands.filter(b => lowerText.includes(b));
    if (mentionedBrands.length > 0 && riskScore > 20) {
        indicators.push(`Possible brand impersonation (${mentionedBrands.join(", ")})`);
        riskScore += 10;
    }

    // Check for poor grammar indicators (simplified)
    const grammarIssues = [
        /\s{2,}/g,  // Multiple spaces
        /[!]{2,}/g,  // Multiple exclamation marks
        /dear\s+(customer|user|member|client)\b/i  // Generic greeting
    ];

    for (const pattern of grammarIssues) {
        if (pattern.test(text)) {
            indicators.push("Poor formatting or generic greeting detected");
            riskScore += 5;
            break;
        }
    }

    // Determine risk level
    let riskLevel;
    if (riskScore >= 50) {
        riskLevel = "High";
    } else if (riskScore >= 25) {
        riskLevel = "Medium";
    } else if (riskScore > 0) {
        riskLevel = "Low";
    } else {
        riskLevel = "None";
    }

    return {
        isPhishing: riskScore >= 25,
        riskScore,
        riskLevel,
        indicators,
        urlCount: urls.length,
        suspiciousUrlCount: suspiciousUrls.length
    };
}

/**
 * Quick check if URL looks suspicious
 * @param {string} url - URL to check
 * @returns {Object} Check result
 */
export function checkUrlSafety(url) {
    const issues = [];

    for (const pattern of SUSPICIOUS_URL_PATTERNS) {
        if (pattern.test(url)) {
            issues.push("Matches suspicious URL pattern");
            break;
        }
    }

    // Check for IP address instead of domain
    if (/\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/.test(url)) {
        issues.push("Uses IP address instead of domain name");
    }

    // Check for punycode/IDN homograph
    if (/xn--/.test(url)) {
        issues.push("Contains internationalized domain name (potential homograph)");
    }

    // Check for excessive subdomains
    const domainMatch = url.match(/https?:\/\/([^\/]+)/);
    if (domainMatch) {
        const domain = domainMatch[1];
        const subdomainCount = (domain.match(/\./g) || []).length;
        if (subdomainCount > 3) {
            issues.push("Excessive subdomains");
        }
    }

    return {
        isSuspicious: issues.length > 0,
        issues
    };
}
