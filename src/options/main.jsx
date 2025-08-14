import React from "react";
import { createRoot } from "react-dom/client";

function Options() {
  return (
    <div style={{ padding: 16 }}>
      <h2>PII Guard 옵션</h2>
      <p>사이드패널에서 API Base URL과 키를 설정하세요.</p>
    </div>
  );
}

createRoot(document.getElementById("root")).render(<Options />);
