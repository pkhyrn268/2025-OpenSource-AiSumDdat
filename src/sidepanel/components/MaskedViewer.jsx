import React, { useMemo, useState } from "react";
import styled from "styled-components";

// props:
// - masked (string)           : 서버가 준 masked_prompt (예: "저는 [NAME]입니다.")
// - entities (array<{entity,label}>): 마스킹된 엔티티 목록
// - title (string) (옵션)     : 상단 타이틀
export default function MaskedViewer({ masked = "", entities = [], title = "마스킹 프롬프트" }) {
  // label별로 순서대로 소비하기 위한 큐 구성
  const pool = useMemo(() => {
    const map = new Map();
    entities.forEach((e) => {
      const key = String(e.label || "").toUpperCase();
      if (!map.has(key)) map.set(key, []);
      map.get(key).push(e.entity);
    });
    return map; // Map<label, string[]>
  }, [entities]);

  // masked 문자열을 [LABEL] 기준으로 분해하여 렌더 세그먼트 생성
  const segments = useMemo(() => {
    const out = [];
    const re = /\[([A-Z_]+)\]/g;
    let idx = 0, last = 0;
    let m;
    while ((m = re.exec(masked)) !== null) {
      if (m.index > last) out.push({ type: "text", text: masked.slice(last, m.index) });
      const label = m[1].toUpperCase();
      // 해당 레이블의 첫 번째 엔티티를 소비
      const list = pool.get(label) || [];
      const original = list.length ? list.shift() : `[${label}]`;
      out.push({ type: "mask", id: idx++, label, original });
      last = m.index + m[0].length;
    }
    if (last < masked.length) out.push({ type: "text", text: masked.slice(last) });
    return out;
    // pool은 useMemo 안에서 소비되므로 eslint 경고 무시
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [masked, entities]);

  // 각 mask id의 토글 상태 저장 (false = [LABEL], true = 원문)
  const [revealed, setRevealed] = useState(() => ({}));

  const toggle = (id) =>
    setRevealed((s) => ({ ...s, [id]: !s[id] }));

  // 현재 화면에 보이는 텍스트(복사용) 생성
  const currentText = useMemo(() => {
    return segments
      .map((seg) =>
        seg.type === "text"
          ? seg.text
          : revealed[seg.id]
          ? seg.original
          : `[${seg.label}]`
      )
      .join("");
  }, [segments, revealed]);

  const copyNow = async () => {
    try {
      await navigator.clipboard.writeText(currentText);
      alert("복사되었습니다.");
    } catch {
      alert("복사 실패. 브라우저 권한을 확인해주세요.");
    }
  };

  return (
    <Wrap>
      <Toolbar>
        <Title>{title}</Title>
        <CopyBtn onClick={copyNow}>📋 복사</CopyBtn>
      </Toolbar>

      <Body>
        {segments.map((seg, i) =>
          seg.type === "text" ? (
            <span key={`t-${i}`}>{seg.text}</span>
          ) : (
            <Mark
              key={`m-${seg.id}`}
              onClick={() => toggle(seg.id)}
              data-label={seg.label}
              title="클릭하여 원문 보기/가리기"
              revealed={!!revealed[seg.id]}
            >
              {revealed[seg.id] ? seg.original : `[${seg.label}]`}
            </Mark>
          )
        )}
      </Body>
    </Wrap>
  );
}

/* ---------- styles ---------- */
const Wrap = styled.div`
  background: #f7fbff;
  border: 1px solid #dbe7ff;
  border-radius: 12px;
  padding: 10px 10px 12px;
  box-shadow: 0 3px 10px rgba(0,0,0,.05);
`;

const Toolbar = styled.div`
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 6px;
`;

const Title = styled.div`
  font-size: 13px; color: #5b6b8a; font-weight: 600;
`;

const CopyBtn = styled.button`
  border: 1px solid #cddcff;
  background: #eef4ff;
  color: #2f5ecb;
  border-radius: 8px; padding: 6px 10px; font-size: 13px;
  cursor: pointer;
  &:hover { background: #e3ecff; }
`;

const Body = styled.div`
  font-size: 14px; line-height: 1.6; white-space: pre-wrap;
  color: #0f172a;
`;

const Mark = styled.button`
  display: inline;
  padding: 0 2px;
  margin: 0 1px;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  background: ${({ revealed }) => (revealed ? "#fff59d" : "#ffeb3b")};
  box-shadow: inset 0 -8px 0 rgba(255,235,59,0.6);
  color: #0f172a;
`;
