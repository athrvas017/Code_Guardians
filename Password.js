// Password utilities for the Password Security Toolkit
// This file is loaded via a classic <script> tag and exposes a global PasswordUtils object.

(function (global) {
  /**
   * Generate a cryptographically–strong random password.
   *
   * Options:
   *  - length: total password length (default: 16)
   *  - useUpper: include A–Z
   *  - useLower: include a–z
   *  - useDigits: include 0–9
   *  - useSymbols: include common symbols
   */
  function generatePassword({
    length = 16,
    useUpper = true,
    useLower = true,
    useDigits = true,
    useSymbols = true,
  } = {}) {
    const upper = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    const lower = "abcdefghijklmnopqrstuvwxyz";
    const digits = "0123456789";
    const symbols = "!@#$%^&*()-_=+[]{};:,.<>?/";

    let alphabet = "";
    if (useUpper) alphabet += upper;
    if (useLower) alphabet += lower;
    if (useDigits) alphabet += digits;
    if (useSymbols) alphabet += symbols;

    if (!alphabet) {
      throw new Error("At least one character set must be selected");
    }

    const randomBuffer = new Uint32Array(length);
    crypto.getRandomValues(randomBuffer);

    let result = "";
    for (let i = 0; i < length; i++) {
      const index = randomBuffer[i] % alphabet.length;
      result += alphabet.charAt(index);
    }

    return result;
  }

  /**
   * Evaluate password strength.
   * Returns an object: { score: 0–4, label: string, suggestions: string[] }
   */
  function evaluatePasswordStrength(password) {
    const suggestions = [];

    if (!password || password.length === 0) {
      return { score: 0, label: "Empty", suggestions: ["Start typing a password to analyze its strength."] };
    }

    let score = 0;

    // Length
    if (password.length >= 16) {
      score += 2;
    } else if (password.length >= 12) {
      score += 1.5;
      suggestions.push("Use at least 16 characters for stronger protection.");
    } else if (password.length >= 8) {
      score += 1;
      suggestions.push("Increase length to at least 12–16 characters.");
    } else {
      suggestions.push("Very short – increase length significantly.");
    }

    // Character variety
    const hasLower = /[a-z]/.test(password);
    const hasUpper = /[A-Z]/.test(password);
    const hasDigit = /[0-9]/.test(password);
    const hasSymbol = /[^A-Za-z0-9]/.test(password);

    const varietyCount = [hasLower, hasUpper, hasDigit, hasSymbol].filter(Boolean).length;
    if (varietyCount >= 3) {
      score += 2;
    } else if (varietyCount === 2) {
      score += 1;
      suggestions.push("Mix in more character types (uppercase, lowercase, numbers, symbols).");
    } else {
      suggestions.push("Use a mix of uppercase, lowercase, numbers and symbols.");
    }

    // Penalize very common patterns
    const lowerPassword = password.toLowerCase();
    const commonPatterns = [
      "password",
      "1234",
      "qwerty",
      "admin",
      "letmein",
    ];

    if (commonPatterns.some((pat) => lowerPassword.includes(pat))) {
      score -= 2;
      suggestions.push("Avoid common words or simple patterns like 'password' or '1234'.");
    }

    if (/^(.)\1{3,}$/.test(password)) {
      // Same character repeated
      score -= 2;
      suggestions.push("Avoid repeating the same character many times.");
    }

    // Clamp score between 0 and 4
    score = Math.max(0, Math.min(4, Math.round(score)));

    let label;
    switch (score) {
      case 0:
        label = "Very Weak";
        break;
      case 1:
        label = "Weak";
        break;
      case 2:
        label = "Fair";
        break;
      case 3:
        label = "Strong";
        break;
      case 4:
      default:
        label = "Very Strong";
        break;
    }

    return { score, label, suggestions };
  }

  // Expose as a single global namespace
  global.PasswordUtils = {
    generatePassword,
    evaluatePasswordStrength,
  };
})(window);
