// Password utilities for the Password Security Toolkit
import word_list from "./word_list.js";

const wordlist = word_list; 

/* =========================
   PASSWORD GENERATOR
   ========================= */
export function generatePassword({ wordCount = 6, separator = "-" } = {}) {
  if (wordCount < 4 || wordCount > 16) {
    throw new Error("wordCount must be between 4 and 16");
  }

  const passwordWords = [];
  const randomBuffer = new Uint32Array(wordCount);

  // Secure random number generation
  crypto.getRandomValues(randomBuffer);

  for (let i = 0; i < wordCount; i++) {
    const index = randomBuffer[i] % wordlist.length;
    passwordWords.push(wordlist[index]);
  }

  return passwordWords.join(separator);
}

/* =========================
   STRENGTH CHECKER (ENTROPY)
   ========================= */
export function evaluatePasswordStrength(password, options = {}) {
  const {
    separator = "-",
    isGenerated = false,
    wordlistSize = wordlist.length
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

  /* =========================
     PASS PHRASE (SAFE MODE)
     ========================= */
  if (isGenerated && password.includes(separator)) {
    const words = password.split(separator).filter(Boolean);
    entropy = Math.log2(wordlistSize) * words.length;

    if (words.length < 6) {
      suggestions.push("Use at least 6 randomly generated words.");
    }

  } else {
    /* =========================
       CHARACTER PASSWORD MODE
       ========================= */
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

  /* =========================
     COMMON PENALTIES
     ========================= */
  if (/^(.)\1+$/.test(password)) entropy *= 0.5;
  if (/123|password|qwerty|admin/i.test(password)) entropy *= 0.4;

  entropy = Math.round(entropy);

  /* =========================
     SCORING (REALISTIC)
     ========================= */
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


export async function checkPasswordBreach(password) {
  if (!password || password.length < 4) {
    return {
      status: "invalid",
      message: "🤨 That’s not even a password. Try harder."
    };
  }

  // Safety check: subtle crypto requires HTTPS or localhost
  if (!crypto.subtle) {
    throw new Error("Crypto API not available. Ensure you are using HTTPS or localhost.");
  }

  const hashBuffer = await crypto.subtle.digest(
    "SHA-1",
    new TextEncoder().encode(password)
  );

  const hash = Array.from(new Uint8Array(hashBuffer))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("")
    .toUpperCase();

  const prefix = hash.slice(0, 5);
  const suffix = hash.slice(5);

  const response = await fetch(
    `https://api.pwnedpasswords.com/range/${prefix}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch from breach database.");
  }

  const text = await response.text();
  
  // FIX: Split using a regex that handles both \n and \r\n
  const lines = text.split(/\r?\n/);
  const match = lines.find(line => line.startsWith(suffix));

  const count = match ? parseInt(match.split(":")[1], 10) : 0;

  /* ==========================
      FUN RESPONSE MAPPING
     ========================== */
  if (count === 0) {
    return {
      status: "safe",
      count,
      emoji: "🟢",
      message: "This password is a ghost 👻 — no breaches found!"
    };
  }

  if (count <= 10) {
    return {
      status: "exposed",
      count,
      emoji: "🟡",
      message: `Seen ${count} times. Not terrible… but not great either.`
    };
  }

  if (count <= 1000) {
    return {
      status: "danger",
      count,
      emoji: "🟠",
      message: `Uh-oh 😬 This password appeared ${count} times in breaches.`
    };
  }

  return {
    status: "compromised",
    count,
    emoji: "🔴",
    message: `ABORT 🚨 This password is burned (${count} breaches).`
  };
}