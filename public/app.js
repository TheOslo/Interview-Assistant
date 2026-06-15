const API_BASE_URL = 'http://127.0.0.1:8000/api';
const evalForm = document.getElementById('evalForm');
const problemInput = document.getElementById('problem');
const languageInput = document.getElementById('language');
const skillInput = document.getElementById('skill');
const codeInput = document.getElementById('code');
const submitBtn = document.getElementById('submitBtn');
const resultBox = document.getElementById('resultBox');
const historyContainer = document.getElementById('historyContainer');

async function fetchHistory() {
try {
const response = await fetch(`${API_BASE_URL}/history?limit=10`);
const data = await response.json();
renderHistory(data.history);
} catch (err) {}
}

function renderHistory(history) {
historyContainer.innerHTML = '';
history.forEach(item => {
const div = document.createElement('div');
div.className = 'history-item';
div.innerHTML = `
<strong>Problem:</strong> ${item.problem} <br>
<strong>Language:</strong> ${item.language} | <strong>Persona:</strong> ${item.skill_level} <br>
<details style="margin-top: 10px;">
<summary>View Code & Evaluation</summary>
<pre class="history-pre">${item.code}</pre>
<div class="history-eval">${item.ai_evaluation}</div>
</details>
`;
historyContainer.appendChild(div);
});
}

evalForm.addEventListener('submit', async (e) => {
e.preventDefault();
submitBtn.disabled = true;
submitBtn.textContent = 'Evaluating...';
resultBox.textContent = '';

const payload = {
problemDescription: problemInput.value,
programmingLanguage: languageInput.value,
skill: skillInput.value,
userCode: codeInput.value
};

try {
const response = await fetch(`${API_BASE_URL}/evaluate`, {
method: 'POST',
headers: {
'Content-Type': 'application/json'
},
body: JSON.stringify(payload)
});

const data = await response.json();
resultBox.textContent = data.evaluation || 'Error processing evaluation.';
fetchHistory();
} catch (err) {
resultBox.textContent = 'Error processing evaluation.';
} finally {
submitBtn.disabled = false;
submitBtn.textContent = 'Submit Code';
}
});

fetchHistory();