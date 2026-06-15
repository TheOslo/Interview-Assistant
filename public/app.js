const API_BASE_URL = 'http://localhost:8000'; // Must match your FastAPI server

// DOM Elements
const form = document.getElementById('evaluation-form');
const submitBtn = document.getElementById('submit-btn');
const btnText = document.getElementById('btn-text');
const btnSpinner = document.getElementById('btn-spinner');
const statusBanner = document.getElementById('status-banner');
const resultContainer = document.getElementById('result-container');
const resultOutput = document.getElementById('result-output');

// State Machine Functions
function setUIState(isProcessing) {
    submitBtn.disabled = isProcessing;
    if (isProcessing) {
        btnText.textContent = 'Evaluating... (This may take up to 25s)';
        btnSpinner.classList.remove('hidden');
        statusBanner.classList.add('hidden');
        resultContainer.classList.add('hidden');
    } else {
        btnText.textContent = 'Evaluate Code';
        btnSpinner.classList.add('hidden');
    }
}

function displayError(message) {
    statusBanner.className = 'banner-error'; // Overwrite classes, keep it visible
    statusBanner.textContent = message;
    statusBanner.classList.remove('hidden');
}

function displayResult(markdownText) {
    // In a real app, you'd use a markdown parser library like 'marked' here.
    // For now, we inject it into a <pre> tag which preserves formatting.
    resultOutput.textContent = markdownText;
    resultContainer.classList.remove('hidden');
}

// Core API Call (Defensive Fetch Wrapper)
async function submitCodeForEvaluation(payload) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/evaluate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload),
        });

        // Handle specific status codes defined in our FastAPI architecture
        if (!response.ok) {
            let errorDetail = 'An unexpected server error occurred.';
            try {
                const errorData = await response.json();
                errorDetail = errorData.detail || errorDetail;
            } catch (e) { /* Ignore JSON parse errors on crash */ }

            switch (response.status) {
                case 422: throw new Error(`Validation Error: ${errorDetail}`);
                case 504: throw new Error('Gateway Timeout: The AI took too long to respond. Please try again.');
                case 503: throw new Error('Service Unavailable: The AI evaluation queue is offline.');
                default: throw new Error(`Server Error (${response.status}): ${errorDetail}`);
            }
        }

        const data = await response.json();
        return data.evaluation;

    } catch (error) {
        // This catches network drops, CORS blocks, or the custom errors thrown above
        console.error("Evaluation Failed:", error);
        throw error;
    }
}

// Form Submission Event Listener
form.addEventListener('submit', async (e) => {
    e.preventDefault(); // Stop browser from reloading the page

    // 1. Gather Data
    const payload = {
        problemDescription: document.getElementById('problem').value.trim(),
        programmingLanguage: document.getElementById('language').value,
        userCode: document.getElementById('code').value.trim(),
        skill: 'interviewer'
    };

    // 2. Lock UI
    setUIState(true);

    // 3. Execute
    try {
        const evaluationResult = await submitCodeForEvaluation(payload);
        displayResult(evaluationResult);
    } catch (error) {
        displayError(error.message);
    } finally {
        // 4. Release UI (Always runs, even on error)
        setUIState(false);
    }
});