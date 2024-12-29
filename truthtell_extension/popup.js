document.addEventListener('DOMContentLoaded', () => {
  const highlightButton = document.getElementById('highlightButton');
  const keywordsInput = document.getElementById('keywordsInput');

  highlightButton.addEventListener('click', () => {
    const keywords = keywordsInput.value.split(',').map((keyword) => keyword.trim());

    // Send the keywords to the content script
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { action: 'highlight', keywords });
    });
  });
});
