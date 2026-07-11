// This MUST point to your live FastAPI backend
const API_ENDPOINT = 'http://localhost:8000/api/phishing/analyze'; 

document.addEventListener('DOMContentLoaded', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        if (!tabs || tabs.length === 0) {
            // ... (error handling for no tab)
            return;
        }
        const url = tabs[0].url;
        if (!url || url.startsWith('chrome://')) {
            // ... (error handling for chrome pages)
            return;
        }

        document.getElementById('url-display').textContent = url.substring(0, 70) + (url.length > 70 ? '...' : '');

        // 2. Call the ML Prediction API
        fetch(API_ENDPOINT, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`API error: ${response.status} ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            const statusDiv = document.getElementById('status');
            const resultDiv = document.getElementById('result');
            const spinner = resultDiv.querySelector('.spinner');
            if (spinner) spinner.remove();

            const mlLabel = data.level || 'N/A';
            const mlConf = data.score || 0;
            const reasons = data.reasons || []; 

            statusDiv.textContent = `${mlLabel} (${mlConf}%)`;
            
            if (data.status === 'BLOCKED' || data.status === 'FLAGGED') {
                statusDiv.className = 'phishing';
            } else if (data.status === 'ALLOWED') {
                statusDiv.className = 'legitimate';
            } else {
                 statusDiv.className = 'loading';
            }

            if (reasons.length > 0) {
                let featuresHTML = '<div class="confidence"><b>Analysis:</b><ul style="margin: 4px 0; padding-left: 18px; font-size: 0.9em;">';
                reasons.forEach((reason) => {
                    featuresHTML += `<li>${reason}</li>`;
                });
                featuresHTML += '</ul></div>';
                
                if (data.explanation) {
                    featuresHTML += `<div style="margin-top: 10px; font-size: 0.8em; color: #555;"><i>GenAI: ${data.explanation}</i></div>`;
                }
                
                resultDiv.insertAdjacentHTML('beforeend', featuresHTML);
            }
        })
        .catch(error => {
            console.error('Prediction failed:', error);
            const statusDiv = document.getElementById('status');
            // --- THIS IS THE NEW, BETTER ERROR ---
            // This will display the exact error in the popup
            statusDiv.textContent = `API Failed: ${error.message}`; 
            statusDiv.className = 'loading';
            const spinner = document.getElementById('result').querySelector('.spinner');
            if (spinner) spinner.remove();
        });
    });
});