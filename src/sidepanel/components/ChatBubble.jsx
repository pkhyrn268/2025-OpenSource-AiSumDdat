import React from "react";

export default function ChatBubble({ role, text, hits = [] }) {
  if (role === "user") {
    return (
      <div className="bubble-row right">
        <div className="bubble user">{text}</div>
      </div>
    );
  }
  if (role === "masked") {
    return (
      <div className="bubble-row left">
        <div className="bubble masked">
          <div className="masked-label">마스킹 결과</div>
          <pre className="masked-pre">{text}</pre>
          {hits.length > 0 && (
            <details className="hits">
              <summary>감지 상세 ({hits.length})</summary>
              <ul>
                {hits.map((h, i) => (
                  <li key={i}><code>{h.type || "unknown"}</code> — {h.sample || ""}</li>
                ))}
              </ul>
            </details>
          )}
        </div>
      </div>
    );
  }
  // bot
  return (
    <div className="bubble-row left">
      <div className="bubble bot">{text}</div>
    </div>
  );
}
