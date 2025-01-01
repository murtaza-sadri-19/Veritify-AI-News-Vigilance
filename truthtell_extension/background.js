chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({
    id: "analyzeSelectedText",
    title: "VerifyIt Selected Text",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "analyzeSelectedText") {
    chrome.tabs.sendMessage(tab.id, {
      action: "analyzeSelectedText",
      selectedText: info.selectionText
    });
  }
});
