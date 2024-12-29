// content.js

// Function to highlight specific words on the page
function highlightKeywords(keywords) {
  const bodyText = document.body.innerHTML;

  // Create a regex for all keywords
  const regex = new RegExp(`\\b(${keywords.join('|')})\\b`, 'gi');

  // Replace matches with highlighted spans
  document.body.innerHTML = bodyText.replace(
    regex,
    '<span style="background-color: yellow; color: red;">$&</span>'
  );
}

// Listen for messages from other scripts
chrome.runtime.onMessage.addListener((message) => {
  if (message.action === 'highlight') {
    highlightKeywords(message.keywords || []);
  }
});
