// NetShield Extension - Password Generator Utility

// Wordlist for passphrase generation (subset for extension size)
export const WORD_LIST = [
    "apple", "banana", "cherry", "dragon", "eagle", "falcon", "garden", "harbor",
    "island", "jungle", "knight", "legend", "meteor", "nebula", "oracle", "phoenix",
    "quartz", "ranger", "sunset", "thunder", "ultra", "valley", "winter", "xenon",
    "yellow", "zenith", "anchor", "beacon", "castle", "diamond", "empire", "forest",
    "galaxy", "horizon", "impulse", "justice", "kingdom", "liberty", "marble", "nature",
    "ocean", "palace", "quantum", "rainbow", "silver", "temple", "unity", "venture",
    "wisdom", "express", "arctic", "blazer", "cosmic", "delta", "ember", "frost",
    "glacier", "hunter", "ivory", "jasper", "karma", "lunar", "magnet", "ninja",
    "oxygen", "plasma", "quest", "rocket", "shadow", "titan", "vertex", "warrior",
    "cipher", "dynamo", "enigma", "flare", "prism", "spark", "storm", "swift",
    "chrome", "azure", "bronze", "coral", "crimson", "golden", "indigo", "jade",
    "obsidian", "ruby", "sapphire", "scarlet", "violet", "amber", "copper", "emerald",
    "cobalt", "slate", "onyx", "pearl", "turquoise", "maroon", "teal", "navy"
];

/**
 * Generate a secure passphrase password
 * @param {Object} options - Generation options
 * @param {number} options.wordCount - Number of words (4-10)
 * @param {string} options.separator - Word separator
 * @returns {string} Generated password
 */
export function generatePassword({ wordCount = 6, separator = "-" } = {}) {
    if (wordCount < 4 || wordCount > 10) {
        throw new Error("Word count must be between 4 and 10");
    }

    const passwordWords = [];
    const randomBuffer = new Uint32Array(wordCount);

    // Secure random number generation
    crypto.getRandomValues(randomBuffer);

    for (let i = 0; i < wordCount; i++) {
        const index = randomBuffer[i] % WORD_LIST.length;
        // Capitalize first letter for better readability
        const word = WORD_LIST[index];
        passwordWords.push(word.charAt(0).toUpperCase() + word.slice(1));
    }

    return passwordWords.join(separator);
}

/**
 * Evaluate password strength using entropy calculation
 * @param {string} password - Password to evaluate
 * @param {Object} options - Evaluation options
 * @returns {Object} Strength evaluation result
 */
export function evaluatePasswordStrength(password, options = {}) {
    const {
        separator = "-",
        isGenerated = false,
        wordlistSize = WORD_LIST.length
    } = options;

    if (!password || password.trim().length === 0) {
        return {
            score: 0,
            label: "Empty",
            entropy: 0,
            suggestions: ["Enter or generate a password."]
        };
    }

    let entropy = 0;
    const suggestions = [];

    // Passphrase mode
    if (isGenerated && password.includes(separator)) {
        const words = password.split(separator).filter(Boolean);
        entropy = Math.log2(wordlistSize) * words.length;

        if (words.length < 6) {
            suggestions.push("Use at least 6 randomly generated words.");
        }
    } else {
        // Character password mode
        let pool = 0;
        if (/[a-z]/.test(password)) pool += 26;
        if (/[A-Z]/.test(password)) pool += 26;
        if (/[0-9]/.test(password)) pool += 10;
        if (/[^A-Za-z0-9]/.test(password)) pool += 32;

        entropy = Math.log2(pool || 1) * password.length;

        if (password.length < 12) {
            suggestions.push("Use at least 12 characters.");
        }
    }

    // Common pattern penalties
    if (/^(.)\1+$/.test(password)) entropy *= 0.5;
    if (/123|password|qwerty|admin/i.test(password)) entropy *= 0.4;

    entropy = Math.round(entropy);

    // Scoring
    let score, label;

    if (entropy < 28) {
        score = 1;
        label = "Very Weak";
    } else if (entropy < 36) {
        score = 2;
        label = "Weak";
    } else if (entropy < 60) {
        score = 3;
        label = "Good";
    } else {
        score = 4;
        label = "Very Strong";
    }

    return {
        score,
        label,
        entropy,
        suggestions
    };
}
