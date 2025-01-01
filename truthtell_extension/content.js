chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "analyzeSelectedText") {
    analyzeContent(request.selectedText);
  }
});

function analyzeContent(query) {
  const loadingOverlay = createLoadingOverlay();
  
  fetch('http://127.0.0.1:5000/analyze', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ query: query })
  })
  .then(response => response.json())
  .then(data => {
    createResultOverlay(data, loadingOverlay);
  })
  .catch(error => {
    console.error('Analysis error:', error);
    loadingOverlay.remove();
  });
}

function createLoadingOverlay() {
  const popup = document.createElement('div');
  popup.innerHTML = `
    <div class="loading-spinner"></div>
    <p>Loading...</p>
  `;
  document.body.appendChild(popup);
  return popup;
}

function createResultOverlay(data, loadingOverlay) {
  loadingOverlay.remove();
  const overlay = document.createElement('div');
  overlay.innerHTML = `
    <div class="result-overlay">
      <h2>Fact Check Results</h2>
      <p>${data.concl}</p>
      <button id="close-overlay">Close</button>
    </div>
  `;
  overlay.querySelector('#close-overlay').addEventListener('click', () => {
    document.body.removeChild(overlay);
  });
  document.body.appendChild(overlay);
}
