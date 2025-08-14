// background → content → sidepanel로 메시지 브릿지
chrome.runtime.onMessage.addListener((msg, _sender, _sendResponse) => {
  if (msg?.type === "SELECTION_TO_PANEL") {
    chrome.runtime.sendMessage({
      type: "OPEN_IN_PANEL",
      payload: msg.payload
    });
  }
});
