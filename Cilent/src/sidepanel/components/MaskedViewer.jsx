// MaskedViewer.jsx
import React, { useEffect, useMemo, useState } from "react";
import styled from "styled-components";

/**
 * props:
 * - masked (string)   : 서버 masked_prompt (예: "안녕 저는 [이름]입니다. [주소/지역] ...")
 * - entities (array)  : [{ entity: string, label: string }, ...]
 * - original (string) : 서버 original_prompt (원문 전체)
 * - title (string)    : 상단 타이틀
 *
 * 동작:
 * - original이 있으면: original을 베이스로, [레이블] 위치의 실제 값(entity)을 찾아 마스킹 pill로 감쌈
 * - original이 없으면: masked만으로 [레이블]을 파싱해 pill 생성(폴백)
 */
export default function MaskedViewer({
  masked = "",
  entities = [],
  original = "",
  title = "마스킹 프롬프트",
}) {
  // 레이블별 엔티티 배열 (순서 유지)
  const byLabel = useMemo(() => {
    const map = new Map();
    for (const e of entities) {
      const label = String(e.label ?? "");
      const val = String(e.entity ?? "");
      if (!map.has(label)) map.set(label, []);
      map.get(label).push(val);
    }
    return map; // Map<label, string[]>
  }, [entities]);

  const segments = useMemo(() => {
    const out = [];
    const tokenRe = /\[([^\]]+)\]/gu;

    // ---------- 폴백: original이 없을 때도 pill 생성 ----------
    if (!original) {
      const labelCursor = Object.create(null);
      let last = 0, mm;
      while ((mm = tokenRe.exec(masked)) !== null) {
        if (mm.index > last) out.push({ type: "text", text: masked.slice(last, mm.index) });
        const label = mm[1];
        const list = byLabel.get(label) ?? [];
        const cur = labelCursor[label] ?? 0;
        const value = list[cur] ?? `[${label}]`;
        labelCursor[label] = cur + 1;
        out.push({ type: "mask", label, text: value });
        last = mm.index + mm[0].length;
      }
      if (last < masked.length) out.push({ type: "text", text: masked.slice(last) });
      return out;
    }

    // ---------- 정상 경로: original을 기준으로 래핑 ----------
    let maskedIdx = 0;  // masked 문자열 커서
    let origIdx = 0;    // original 문자열 커서
    let m;

    const labelCursor = Object.create(null);

    const pushPlainFromOriginal = (plain) => {
      if (!plain) return;
      const pos = original.indexOf(plain, origIdx);
      if (pos === -1) {
        out.push({ type: "text", text: plain }); // 불일치 시 안전한 출력
        return;
      }
      if (pos > origIdx) out.push({ type: "text", text: original.slice(origIdx, pos) });
      out.push({ type: "text", text: plain });
      origIdx = pos + plain.length;
    };

    while ((m = tokenRe.exec(masked)) !== null) {
      const before = masked.slice(maskedIdx, m.index);
      pushPlainFromOriginal(before);

      const label = m[1];
      const list = byLabel.get(label) ?? [];
      const cur = labelCursor[label] ?? 0;
      const value = list[cur];

      if (typeof value === "string" && value.length) {
        const pos = original.indexOf(value, origIdx);
        if (pos !== -1) {
          if (pos > origIdx) out.push({ type: "text", text: original.slice(origIdx, pos) });
          out.push({ type: "mask", label, text: value, start: pos, end: pos + value.length });
          origIdx = pos + value.length;
          labelCursor[label] = cur + 1;
        } else {
          out.push({ type: "mask", label, text: value }); // 못 찾을 때 안전 출력
          labelCursor[label] = cur + 1;
        }
      } else {
        out.push({ type: "mask", label, text: `[${label}]` });
      }
      maskedIdx = m.index + m[0].length;
    }

    const tailPlain = masked.slice(maskedIdx);
    pushPlainFromOriginal(tailPlain);

    if (origIdx < original.length) out.push({ type: "text", text: original.slice(origIdx) });

    return out;
  }, [masked, original, byLabel]);

  // 토글 상태
  const [revealed, setRevealed] = useState({});
  useEffect(() => setRevealed({}), [masked, original, entities]);

  const toggle = (i) => setRevealed((s) => ({ ...s, [i]: !s[i] }));

  // 복사용 텍스트(현재 보이는 그대로)
  const currentText = useMemo(() => {
    return segments
      .map((seg, i) =>
        seg.type === "text" ? seg.text : revealed[i] ? seg.text : `[${seg.label}]`
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
        <CopyBtn onClick={copyNow}>복사</CopyBtn>
      </Toolbar>

      <Body>
        {segments.map((seg, i) =>
          seg.type === "text" ? (
            <span key={`t-${i}`}>{seg.text}</span>
          ) : (
            <Mark
              key={`m-${i}`}
              revealed={!!revealed[i]}
              onClick={() => toggle(i)}
              title="클릭하여 원문 보기/가리기"
            >
              {revealed[i] ? seg.text : `[${seg.label}]`}
            </Mark>
          )
        )}
      </Body>
    </Wrap>
  );
}

/* ---------- styles ---------- */
const Wrap = styled.div`
  background: #BBB8E6B5;
  border: 1px solid #dbe7ff;
  border-radius: 12px;
  padding: 10px 10px 12px;
  box-shadow: 0 3px 10px rgba(0,0,0,.05);
`;
const Toolbar = styled.div`
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 8px;
`;
const Title = styled.div`
  font-size: 12px; color: #6b7280; font-weight: 400;
`;
const CopyBtn = styled.button`
  border: 0.3px solid #6b7280;
  background: transparent; color: #6b7280;
  border-radius: 6px; padding: 4px 10px;
  font-size: 12px; font-weight: 400; cursor: pointer;
  transition: background .2s, color .2s;
  &:hover { background: rgba(107,114,128,.05); }
`;
const Body = styled.div`
  font-size: 14px; line-height: 1.6; white-space: pre-wrap; color: #0f172a;
`;
const Mark = styled.button`
  display: inline;
  padding: 0 3px; margin: 0 1px;
  border: none; border-radius: 4px;
  cursor: pointer; font-weight: 500;
  background: ${({ revealed }) => (revealed ? "#b39ddb" : "#ede7f6")};
  color: #1a1a2e; transition: background .2s;
  &:hover { background: ${({ revealed }) => (revealed ? "#c5b3e6" : "#b39ddb")}; }
`;
