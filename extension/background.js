// UnderSec Chrome Phishing Extension - Background Service Worker
// Real-time tab URL interception and threat scoring via FastAPI / XGBoost model

const API_ENDPOINT = 'http://localhost:8000/api/phishing/analyze';

async function evaluateUrl(tabId, url) {
    if (!url || url.startsWith('chrome://') || url.startsWith('chrome-extension://') || url.startsWith('edge://')) {
        chrome.action.setBadgeText({ tabId, text: '' });
        return;
    }

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        });

        if (!response.ok) return;

        const data = await response.json();

        if (data.status === 'BLOCKED') {
            chrome.action.setBadgeText({ tabId, text: 'DROP' });
            chrome.action.setBadgeBackgroundColor({ tabId, color: '#ef4444' });
        } else if (data.status === 'FLAGGED') {
            chrome.action.setBadgeText({ tabId, text: 'WARN' });
            chrome.action.setBadgeBackgroundColor({ tabId, color: '#f59e0b' });
        } else {
            chrome.action.setBadgeText({ tabId, text: 'OK' });
            chrome.action.setBadgeBackgroundColor({ tabId, color: '#22c55e' });
        }
    } catch (e) {
        // Gateway offline or unreachable
        chrome.action.setBadgeText({ tabId, text: '' });
    }
}

// Intercept tab updates
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        evaluateUrl(tabId, tab.url);
    }
});

// Intercept tab switches
chrome.tabs.onActivated.addListener(async (activeInfo) => {
    try {
        const tab = await chrome.tabs.get(activeInfo.tabId);
        if (tab && tab.url) {
            evaluateUrl(activeInfo.tabId, tab.url);
        }
    } catch (e) {}
});
