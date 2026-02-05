// NetShield Extension - Popup Logic
import { generatePassword, evaluatePasswordStrength, WORD_LIST } from '../utils/password_generator.js';
import { analyzePhishing, extractUrls } from '../utils/phishing_analyzer.js';

// DOM Elements
const tabBtns = document.querySelectorAll('.tab-btn');
const tabContents = document.querySelectorAll('.tab-content');

// Password Tab Elements
const wordCountSlider = document.getElementById('word-count');
const wordCountDisplay = document.getElementById('word-count-display');
const separatorSelect = document.getElementById('separator');
const generateBtn = document.getElementById('generate-btn');
const passwordOutput = document.getElementById('password-output');
const generatedPasswordEl = document.getElementById('generated-password');
const copyBtn = document.getElementById('copy-btn');
const strengthSection = document.getElementById('strength-meter');
const strengthBar = document.getElementById('strength-bar');
const strengthLabel = document.getElementById('strength-label');
const entropyInfo = document.getElementById('entropy-info');

// Phishing Tab Elements
const emailContent = document.getElementById('email-content');
const scanBtn = document.getElementById('scan-btn');
const scanPageBtn = document.getElementById('scan-page-btn');
const scanResult = document.getElementById('scan-result');
const resultIcon = document.getElementById('result-icon');
const resultText = document.getElementById('result-text');
const resultDetails = document.getElementById('result-details');
const urlResults = document.getElementById('url-results');
const urlList = document.getElementById('url-list');

// Tab Navigation
tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
        const tabId = btn.dataset.tab;

        // Update buttons
        tabBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        // Update content
        tabContents.forEach(content => {
            content.classList.remove('active');
            if (content.id === `${tabId}-tab`) {
                content.classList.add('active');
            }
        });
    });
});

// Word Count Slider
wordCountSlider.addEventListener('input', (e) => {
    wordCountDisplay.textContent = e.target.value;
});

// Generate Password
generateBtn.addEventListener('click', () => {
    const wordCount = parseInt(wordCountSlider.value);
    const separator = separatorSelect.value;

    try {
        const password = generatePassword({ wordCount, separator });
        generatedPasswordEl.textContent = password;
        passwordOutput.classList.remove('hidden');

        // Evaluate strength
        const strength = evaluatePasswordStrength(password, {
            separator,
            isGenerated: true,
            wordlistSize: WORD_LIST.length
        });

        updateStrengthMeter(strength);
        strengthSection.classList.remove('hidden');

    } catch (error) {
        generatedPasswordEl.textContent = `Error: ${error.message}`;
        passwordOutput.classList.remove('hidden');
    }
});

// Copy to Clipboard
copyBtn.addEventListener('click', async () => {
    const password = generatedPasswordEl.textContent;
    try {
        await navigator.clipboard.writeText(password);
        copyBtn.textContent = '✅';
        setTimeout(() => {
            copyBtn.textContent = '📋';
        }, 1500);
    } catch (err) {
        console.error('Failed to copy:', err);
    }
});

// Update Strength Meter
function updateStrengthMeter(strength) {
    // Remove all strength classes
    strengthBar.className = 'strength-bar';

    if (strength.score <= 1) {
        strengthBar.classList.add('weak');
        strengthLabel.textContent = '⚠️ ' + strength.label;
        strengthLabel.style.color = '#ef4444';
    } else if (strength.score === 2) {
        strengthBar.classList.add('fair');
        strengthLabel.textContent = '🟡 ' + strength.label;
        strengthLabel.style.color = '#f59e0b';
    } else if (strength.score === 3) {
        strengthBar.classList.add('good');
        strengthLabel.textContent = '✅ ' + strength.label;
        strengthLabel.style.color = '#84cc16';
    } else {
        strengthBar.classList.add('strong');
        strengthLabel.textContent = '🛡️ ' + strength.label;
        strengthLabel.style.color = '#22c55e';
    }

    entropyInfo.textContent = `Entropy: ~${strength.entropy} bits`;
}

// Scan Email Content
scanBtn.addEventListener('click', () => {
    const text = emailContent.value.trim();
    if (!text) {
        alert('Please paste email content to analyze.');
        return;
    }

    analyzeContent(text);
});

// Scan Current Page
scanPageBtn.addEventListener('click', async () => {
    try {
        // Request content from the active tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        chrome.tabs.sendMessage(tab.id, { action: 'scanEmail' }, (response) => {
            if (chrome.runtime.lastError) {
                alert('Could not scan this page. Make sure you are on an email page.');
                return;
            }

            if (response && response.content) {
                emailContent.value = response.content;
                analyzeContent(response.content);
            } else {
                alert('No email content found on this page.');
            }
        });
    } catch (error) {
        console.error('Scan error:', error);
        alert('Failed to scan page.');
    }
});

// Analyze Content for Phishing
function analyzeContent(text) {
    const result = analyzePhishing(text);
    const urls = extractUrls(text);

    // Show result
    scanResult.classList.remove('hidden', 'safe', 'danger');

    if (result.isPhishing) {
        scanResult.classList.add('danger');
        resultIcon.textContent = '🚨';
        resultText.textContent = 'Potential Phishing Detected!';
        resultDetails.innerHTML = `
      <p><strong>Risk Level:</strong> ${result.riskLevel}</p>
      <p><strong>Warning Signs:</strong></p>
      <ul style="padding-left: 16px; margin-top: 4px;">
        ${result.indicators.map(i => `<li>${i}</li>`).join('')}
      </ul>
    `;
    } else {
        scanResult.classList.add('safe');
        resultIcon.textContent = '✅';
        resultText.textContent = 'No Phishing Indicators Found';
        resultDetails.innerHTML = '<p>This message appears to be safe, but always exercise caution with links and attachments.</p>';
    }

    // Show URLs if found
    if (urls.length > 0) {
        urlResults.classList.remove('hidden');
        urlList.innerHTML = urls.map(url => `
      <li>
        <span class="url-status">🔗</span>
        <span class="url-text">${truncateUrl(url)}</span>
      </li>
    `).join('');
    } else {
        urlResults.classList.add('hidden');
    }
}

function truncateUrl(url, maxLength = 35) {
    if (url.length <= maxLength) return url;
    return url.substring(0, maxLength) + '...';
}
