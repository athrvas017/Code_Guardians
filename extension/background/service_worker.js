// NetShield Extension - Background Service Worker

// Context menu for phishing analysis
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: 'netshield-analyze',
        title: 'Analyze with NetShield',
        contexts: ['selection']
    });
});

// Handle context menu clicks
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'netshield-analyze') {
        const selectedText = info.selectionText;

        // Store selected text for popup to use
        chrome.storage.local.set({
            analyzedText: selectedText,
            timestamp: Date.now()
        });

        // Open popup
        chrome.action.openPopup();
    }
});

// Handle messages from content scripts
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'checkUrl') {
        // Could integrate with Safe Browsing API here
        sendResponse({ safe: true });
    }
    return true;
});
