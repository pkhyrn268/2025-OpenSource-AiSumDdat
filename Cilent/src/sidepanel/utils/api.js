const SETTINGS_KEY = "pii_guard_api_settings";

export async function loadSettings() {
  const data = await chrome.storage.sync.get(SETTINGS_KEY);
  return data[SETTINGS_KEY] || { apiBase: "", apiKey: "" };
}

export async function saveSettings(s) {
  await chrome.storage.sync.set({ [SETTINGS_KEY]: s });
}

export async function maskViaAPI({ apiBase, apiKey, text }) {
  if (!apiBase) throw new Error("API Base URL이 필요합니다.");
  const url = apiBase.replace(/\/$/, "") + "/mask";
  const res = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(apiKey ? { Authorization: "Bearer " + apiKey } : {})
    },
    body: JSON.stringify({ text })
  });
  if (!res.ok) {
    const t = await res.text().catch(() => "");
    throw new Error("API 오류: " + res.status + " " + t);
  }
  return await res.json();
}
