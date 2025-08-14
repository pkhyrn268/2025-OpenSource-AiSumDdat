const KEY = "pii_saved_prompts";

export async function loadSaved() {
  const d = await chrome.storage.local.get(KEY);
  return d[KEY] || [];
}

export async function saveAll(list) {
  await chrome.storage.local.set({ [KEY]: list });
}
