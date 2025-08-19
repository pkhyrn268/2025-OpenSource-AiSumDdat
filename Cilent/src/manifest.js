import { defineManifest } from "@crxjs/vite-plugin";

export default defineManifest({
  manifest_version: 3,
  name: "PII Guard – Prompt Privacy (JS)",
  version: "0.0.1",
  description: "AI 프롬프트 전 개인정보를 서버에서 마스킹합니다. (클라이언트는 API 호출만)",
  icons: {
    "16": "icons/16.png",
    "32": "icons/32.png",
    "48": "icons/48.png",
    "128": "icons/128.png"
  },
  action: { default_title: "PII Guard" },
  side_panel: {
    // 사이드패널 엔트리 (CRX가 경로를 그대로 번들에 포함)
    default_path: "src/sidepanel/index.html"
  },
  background: {
    service_worker: "src/background/index.js",
    type: "module"
  },
  permissions: [
    "storage",
    "scripting",
    "activeTab",
    "contextMenus",
    "sidePanel"
  ],
  host_permissions: ["http://*/*", "https://*/*"],
  content_scripts: [
    {
      matches: ["http://*/*", "https://*/*"],
      js: ["src/content/index.js"],
      run_at: "document_idle"
    }
  ],
  options_page: "src/options/index.html"
});
