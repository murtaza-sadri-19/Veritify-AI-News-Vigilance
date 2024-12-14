document.addEventListener('DOMContentLoaded', function() {
    const appContainer = document.querySelector('.app-container');
    const sidebar = document.querySelector('.sidebar');
    const chatContainer = document.querySelector('.chat-container');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const chatMessages = document.getElementById('chatMessages');
    const chatInput = document.getElementById('chatInput');
    const chatForm = document.getElementById('chatForm');
    const typingIndicator = document.getElementById('typingIndicator');
    const themeToggle = document.getElementById('themeToggle');
    const fileDropZone = document.getElementById('fileDropZone');
    const exportButton = document.getElementById('exportButton');
    const clearButton = document.getElementById('clearButton');
    let messageCount = 0;
    let wordCount = 0;
    let charCount = 0;

    // Theme toggle
    document.body.classList.add('dark-mode');
        themeToggle.textContent = '☀️';
    themeToggle.addEventListener('click', function() {
        document.body.classList.toggle('dark-mode');
        themeToggle.textContent = document.body.classList.contains('dark-mode') ? '☀️' : '🌓';
    });


    let sidebarOpen = true;

    sidebarToggle.addEventListener('click', function() {
        sidebarOpen = !sidebarOpen;
        sidebar.classList.toggle('hidden', !sidebarOpen);
    });

    // Chat form submission
    chatForm.addEventListener('submit', function(event) {
        event.preventDefault();
        sendContent();
    });





function sendMessage(text) {
    const messageElement = createMessageElement(text, 'user-message');
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    addToChatHistory(text, 'user');
}

function displayResponse(message) {
    const messageElement = createMessageElement(message, 'bot-message');
    chatMessages.appendChild(messageElement);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    addToChatHistory(message, 'bot');
    updateChatStatistics(message);
}

function createMessageElement(text, messageType) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('chat-message', messageType);

    const textElement = document.createElement('div');
    textElement.innerHTML = marked.parse(text);

    

    messageElement.appendChild(textElement);
    return messageElement;
}



  // Export chat history
  function exportChatHistory() {
    const chatHistory = Array.from(chatMessages.querySelectorAll('.chat-message'))
        .map(msg => `${msg.classList.contains('user-message') ? 'User' : 'Bot'}: ${msg.textContent.trim()}`) // Trim whitespace for cleaner output
        .join('\n\n'); // Add double line breaks between messages

    const blob = new Blob([chatHistory], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'chat_history.txt';
    a.click(); // This simulates a click to trigger the download
    URL.revokeObjectURL(url);
}

// Clear chat history
function clearChatHistory() {
    if (confirm('Are you sure you want to clear the chat history?')) {
        chatMessages.innerHTML = ''; // Clears the chat messages display
        document.getElementById('chatHistory').innerHTML = ''; // Clears the sidebar history (assuming you have an element with this ID)
        messageCount = 0;
        wordCount = 0;
        charCount = 0;
        updateChatStatistics(''); // Reset the chat statistics
    }
}

// Add to chat history sidebar
function addToChatHistory(message, sender) {
    const historyItem = document.createElement('li');
    historyItem.textContent = `${sender}: ${message.substring(0, 30)}${message.length > 30 ? '...' : ''}`;
    document.getElementById('chatHistory').appendChild(historyItem);
}


// Event listeners for export and clear buttons
exportButton.addEventListener('click', exportChatHistory); 
clearButton.addEventListener('click', clearChatHistory); 




});