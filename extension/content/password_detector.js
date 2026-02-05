// NetShield Extension - Password Field Detection Content Script

(function () {
    'use strict';

    // Styles for the password popup
    const POPUP_STYLES = `
    .netshield-password-popup {
      position: absolute;
      z-index: 2147483647;
      background: linear-gradient(135deg, #1e293b, #0f172a);
      border: 1px solid rgba(34, 211, 238, 0.3);
      border-radius: 12px;
      padding: 12px;
      box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
      font-family: 'Segoe UI', system-ui, sans-serif;
      min-width: 280px;
      animation: netshield-fadeIn 0.2s ease;
    }

    @keyframes netshield-fadeIn {
      from { opacity: 0; transform: translateY(-8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .netshield-popup-header {
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 10px;
      padding-bottom: 8px;
      border-bottom: 1px solid rgba(148, 163, 184, 0.2);
    }

    .netshield-popup-logo {
      font-size: 1.1rem;
    }

    .netshield-popup-title {
      font-size: 0.85rem;
      font-weight: 600;
      color: #f1f5f9;
    }

    .netshield-popup-title span {
      color: #22d3ee;
    }

    .netshield-popup-close {
      margin-left: auto;
      background: none;
      border: none;
      color: #94a3b8;
      cursor: pointer;
      font-size: 1.2rem;
      padding: 0;
      line-height: 1;
    }

    .netshield-popup-close:hover {
      color: #f1f5f9;
    }

    .netshield-generated-password {
      background: rgba(34, 197, 94, 0.1);
      border: 1px solid rgba(34, 197, 94, 0.3);
      border-radius: 8px;
      padding: 10px;
      font-family: 'SF Mono', 'Consolas', monospace;
      font-size: 0.85rem;
      color: #22c55e;
      word-break: break-all;
      margin-bottom: 10px;
    }

    .netshield-btn-group {
      display: flex;
      gap: 8px;
    }

    .netshield-btn {
      flex: 1;
      padding: 8px 12px;
      border: none;
      border-radius: 6px;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
    }

    .netshield-btn-primary {
      background: linear-gradient(135deg, #6366f1, #4f46e5);
      color: white;
    }

    .netshield-btn-primary:hover {
      transform: translateY(-1px);
      box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }

    .netshield-btn-secondary {
      background: #334155;
      color: #f1f5f9;
    }

    .netshield-btn-secondary:hover {
      background: #475569;
    }

    .netshield-generate-icon {
      position: absolute;
      right: 8px;
      top: 50%;
      transform: translateY(-50%);
      background: linear-gradient(135deg, #22d3ee, #6366f1);
      border: none;
      border-radius: 6px;
      padding: 6px 10px;
      cursor: pointer;
      font-size: 0.75rem;
      color: white;
      font-weight: 600;
      z-index: 2147483646;
      transition: all 0.2s ease;
    }

    .netshield-generate-icon:hover {
      transform: translateY(-50%) scale(1.05);
      box-shadow: 0 4px 15px rgba(34, 211, 238, 0.4);
    }
  `;

    // Word list for password generation (compact version)
    const WORD_LIST = [
        "apple", "banana", "cherry", "dragon", "eagle", "falcon", "garden", "harbor",
        "island", "jungle", "knight", "legend", "meteor", "nebula", "oracle", "phoenix",
        "quartz", "ranger", "sunset", "thunder", "ultra", "valley", "winter", "zenith",
        "anchor", "beacon", "castle", "diamond", "empire", "forest", "galaxy", "horizon",
        "cosmic", "delta", "ember", "frost", "glacier", "hunter", "ivory", "jasper",
        "karma", "lunar", "magnet", "ninja", "oxygen", "plasma", "quest", "rocket"
    ];

    let currentPopup = null;
    let currentPasswordField = null;

    // Inject styles
    function injectStyles() {
        if (document.getElementById('netshield-styles')) return;

        const styleEl = document.createElement('style');
        styleEl.id = 'netshield-styles';
        styleEl.textContent = POPUP_STYLES;
        document.head.appendChild(styleEl);
    }

    // Generate secure password
    function generatePassword(wordCount = 4) {
        const words = [];
        const randomBuffer = new Uint32Array(wordCount);
        crypto.getRandomValues(randomBuffer);

        for (let i = 0; i < wordCount; i++) {
            const index = randomBuffer[i] % WORD_LIST.length;
            const word = WORD_LIST[index];
            words.push(word.charAt(0).toUpperCase() + word.slice(1));
        }

        return words.join('-');
    }

    // Create password popup
    function createPopup(passwordField) {
        removePopup();

        const password = generatePassword(4);
        const rect = passwordField.getBoundingClientRect();

        const popup = document.createElement('div');
        popup.className = 'netshield-password-popup';
        popup.innerHTML = `
      <div class="netshield-popup-header">
        <span class="netshield-popup-logo">🛡️</span>
        <span class="netshield-popup-title">Net<span>Shield</span></span>
        <button class="netshield-popup-close" title="Close">×</button>
      </div>
      <div class="netshield-generated-password">${password}</div>
      <div class="netshield-btn-group">
        <button class="netshield-btn netshield-btn-primary" data-action="use">Use Password</button>
        <button class="netshield-btn netshield-btn-secondary" data-action="regenerate">🔄 New</button>
      </div>
    `;

        // Position popup below the input field
        popup.style.top = `${rect.bottom + window.scrollY + 5}px`;
        popup.style.left = `${rect.left + window.scrollX}px`;

        document.body.appendChild(popup);
        currentPopup = popup;
        currentPasswordField = passwordField;

        // Event listeners
        popup.querySelector('.netshield-popup-close').addEventListener('click', removePopup);

        popup.querySelector('[data-action="use"]').addEventListener('click', () => {
            const passwordText = popup.querySelector('.netshield-generated-password').textContent;
            passwordField.value = passwordText;
            passwordField.dispatchEvent(new Event('input', { bubbles: true }));

            // Also fill confirm password if present
            const form = passwordField.closest('form');
            if (form) {
                const confirmField = form.querySelector('input[type="password"]:not([data-netshield])');
                if (confirmField && confirmField !== passwordField) {
                    confirmField.value = passwordText;
                    confirmField.dispatchEvent(new Event('input', { bubbles: true }));
                }
            }

            removePopup();
        });

        popup.querySelector('[data-action="regenerate"]').addEventListener('click', () => {
            const newPassword = generatePassword(4);
            popup.querySelector('.netshield-generated-password').textContent = newPassword;
        });

        // Close on outside click
        setTimeout(() => {
            document.addEventListener('click', handleOutsideClick);
        }, 100);
    }

    function handleOutsideClick(e) {
        if (currentPopup && !currentPopup.contains(e.target) && e.target !== currentPasswordField) {
            removePopup();
        }
    }

    function removePopup() {
        if (currentPopup) {
            currentPopup.remove();
            currentPopup = null;
            document.removeEventListener('click', handleOutsideClick);
        }
    }

    // Add generate button to password fields
    function enhancePasswordField(field) {
        if (field.dataset.netshieldEnhanced) return;
        field.dataset.netshieldEnhanced = 'true';

        // Wrap if not already wrapped
        const wrapper = field.parentElement;
        if (!wrapper.style.position || wrapper.style.position === 'static') {
            wrapper.style.position = 'relative';
        }

        // Create generate button
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'netshield-generate-icon';
        btn.textContent = '🛡️ Generate';
        btn.title = 'Generate secure password';

        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            createPopup(field);
        });

        // Position relative to the field
        field.parentElement.appendChild(btn);
    }

    // Find and enhance password fields
    function findPasswordFields() {
        const passwordInputs = document.querySelectorAll('input[type="password"]');
        passwordInputs.forEach(enhancePasswordField);
    }

    // Initialize
    function init() {
        injectStyles();
        findPasswordFields();

        // Watch for dynamically added password fields
        const observer = new MutationObserver((mutations) => {
            for (const mutation of mutations) {
                for (const node of mutation.addedNodes) {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.matches && node.matches('input[type="password"]')) {
                            enhancePasswordField(node);
                        }
                        const passwordInputs = node.querySelectorAll?.('input[type="password"]');
                        passwordInputs?.forEach(enhancePasswordField);
                    }
                }
            }
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }

    // Listen for messages from popup
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.action === 'scanEmail') {
            // Try to extract email content from the page
            const emailContent = extractEmailContent();
            sendResponse({ content: emailContent });
        }
        return true;
    });

    // Extract email content from common email providers
    function extractEmailContent() {
        let content = '';

        // Gmail
        const gmailBody = document.querySelector('[data-message-id] .a3s.aiL');
        if (gmailBody) {
            content = gmailBody.innerText;
        }

        // Outlook Web
        const outlookBody = document.querySelector('[aria-label="Message body"]');
        if (outlookBody) {
            content = outlookBody.innerText;
        }

        // Yahoo Mail
        const yahooBody = document.querySelector('.msg-body');
        if (yahooBody) {
            content = yahooBody.innerText;
        }

        // Generic fallback - look for common email content containers
        if (!content) {
            const genericSelectors = [
                '.email-content',
                '.message-body',
                '.mail-content',
                '[role="main"] article',
                '.ReadMsgBody'
            ];

            for (const selector of genericSelectors) {
                const el = document.querySelector(selector);
                if (el) {
                    content = el.innerText;
                    break;
                }
            }
        }

        return content.trim();
    }

    // Run when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
