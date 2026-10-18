// UnderSec Chrome Phishing Extension Popup Script
// Communicates with FastAPI backend to run real-time XGBoost 7-feature inference

const API_ENDPOINT = 'http://localhost:8000/api/phishing/analyze';

function setScanState(loading, message = 'Analyzing...') {
    const badge = document.getElementById('status-badge');
    if (loading) {
        badge.className = 'verdict-badge badge-loading';
        badge.innerHTML = `<span class="spinner"></span> ${message}`;
        document.getElementById('score-display').textContent = '--%';
    }
}

function updateUI(data) {
    const badge = document.getElementById('status-badge');
    const scoreDisplay = document.getElementById('score-display');
    const aiBox = document.getElementById('ai-box');
    const reasonsContainer = document.getElementById('reasons-container');
    const reasonsList = document.getElementById('reasons-list');

    // Verdict Badge & Score
    scoreDisplay.textContent = `${data.score}%`;
    if (data.status === 'BLOCKED') {
        badge.className = 'verdict-badge badge-blocked';
        badge.textContent = `🛑 BLOCKED (${data.level})`;
        scoreDisplay.style.color = 'var(--accent-red)';
    } else if (data.status === 'FLAGGED') {
        badge.className = 'verdict-badge badge-flagged';
        badge.textContent = `⚠️ FLAGGED (${data.level})`;
        scoreDisplay.style.color = 'var(--accent-yellow)';
    } else {
        badge.className = 'verdict-badge badge-allowed';
        badge.textContent = `✅ ALLOWED (SAFE)`;
        scoreDisplay.style.color = 'var(--accent-green)';
    }

    // 7 Features
    if (data.features) {
        document.getElementById('f-len-url').textContent = data.features.len_url;
        document.getElementById('f-len-host').textContent = data.features.len_host;
        document.getElementById('f-digits').textContent = data.features.count_digits;
        document.getElementById('f-subs').textContent = data.features.subdomains;
        document.getElementById('f-ip').textContent = data.features.has_ip ? 'YES (1)' : 'NO (0)';
        document.getElementById('f-ip').style.color = data.features.has_ip ? 'var(--accent-red)' : 'var(--text-main)';
        document.getElementById('f-non-alnum').textContent = data.features.non_alnum;
        document.getElementById('f-entropy').textContent = data.features.path_entropy;
    }

    // AI Explanation
    aiBox.textContent = data.explanation || 'Analyzed via XGBoost 7-heuristic structural model.';

    // Reasons
    if (data.reasons && data.reasons.length > 0) {
        reasonsContainer.style.display = 'block';
        reasonsList.innerHTML = '';
        data.reasons.forEach(r => {
            const li = document.createElement('li');
            li.textContent = r;
            reasonsList.appendChild(li);
        });
    } else {
        reasonsContainer.style.display = 'none';
    }
}

async function analyzeUrl(targetUrl) {
    if (!targetUrl) return;
    setScanState(true);
    document.getElementById('url-display').textContent = targetUrl;

    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: targetUrl })
        });

        if (!response.ok) {
            throw new Error(`Gateway Error: ${response.status}`);
        }

        const data = await response.json();
        updateUI(data);
    } catch (err) {
        const badge = document.getElementById('status-badge');
        badge.className = 'verdict-badge badge-blocked';
        badge.textContent = 'GATEWAY ERROR';
        document.getElementById('ai-box').textContent = `Failed to connect to UnderSec API at ${API_ENDPOINT}: ${err.message}. Ensure FastAPI backend is running.`;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    // 1. Scan active browser tab
    if (typeof chrome !== 'undefined' && chrome.tabs && chrome.tabs.query) {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            if (tabs && tabs[0] && tabs[0].url) {
                analyzeUrl(tabs[0].url);
            } else {
                analyzeUrl('https://na.panasonic.com/us/automotive-solutions');
            }
        });
    } else {
        // Fallback demo URL
        analyzeUrl('https://na.panasonic.com/us/automotive-solutions');
    }

    // 2. Manual URL sandbox test button
    const manualBtn = document.getElementById('manual-btn');
    const manualInput = document.getElementById('manual-url');
    if (manualBtn && manualInput) {
        manualBtn.addEventListener('click', () => {
            const val = manualInput.value.trim();
            if (val) analyzeUrl(val);
        });
        manualInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                const val = manualInput.value.trim();
                if (val) analyzeUrl(val);
            }
        });
    }
});