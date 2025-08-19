chrome.runtime.onInstalled.addListener(async () => {
  try {
    // Chrome 114+ 사이드패널: 액션 클릭 시 열기
    await chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true });
  } catch (e) {}

  chrome.contextMenus.create({
    id: "pii-guard-mask-selection",
    title: "PII 마스킹 요청(서버) → 사이드패널로",
    contexts: ["selection"]
  });
});

chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === "pii-guard-mask-selection" && tab?.id) {
    const selectionText = info.selectionText ?? "";
    chrome.tabs.sendMessage(tab.id, {
      type: "SELECTION_TO_PANEL",
      payload: selectionText
    });
    try {
      await chrome.sidePanel.open({ tabId: tab.id });
    } catch (e) {}
  }
});

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg?.type === "PING_BG") {
    sendResponse({ ok: true, at: Date.now() });
    return true;
  }
  return false;
});
