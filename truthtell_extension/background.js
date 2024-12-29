// background.js

// Placeholder for future functionality
console.log('TruthTell background script initialized');

// Listen for popup interactions and manage state
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.action === 'log') {
    console.log(message.text);
  }
});
