document.getElementById('checkHistory').addEventListener('click', () => {
  let historyDiv = document.getElementById('historyDiv');
  chrome.storage.local.get('history', function(result) {
      const history = result.history || [];
      historyDiv.innerHTML = history.length > 0 ? 
          history.map(item => `<button class="historyButton">${item.title}</button>`).join('') : 
          '<p>No history available</p>';
  });
});
