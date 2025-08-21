const API_BASE = "http://210.94.179.19:9814/";

// POST /api/masking (multipart/form-data)
// promptJson: { question1..6 }, pdfFile: File|undefined
export async function uploadMasking(promptJson, pdfFile) {
  const fd = new FormData();
  fd.append("prompt_json", JSON.stringify(promptJson));
  if (pdfFile) fd.append("pdf_file", pdfFile);

  const res = await fetch(`${API_BASE}/api/masking`, {
    method: "POST",
    body: fd,
  });

  const body = await res.json().catch(() => ({}));
  if (!res.ok || body?.status >= 400) {
    throw new Error(body?.message || `API 오류 (${res.status})`);
  }

  const data = body?.data || { original_prompt: "", masked_prompt: "", masked_entities: [] };

  // 👉 인덱스 달기
  const tokenRe = /\[([^\]]+)\]/gu;
  let idx = 0;
  const entitiesWithIndex = data.masked_entities.map((e) => ({ ...e, index: -1 }));

  // masked_prompt를 순회하며 토큰 순서에 맞게 index 매핑
  let m;
  while ((m = tokenRe.exec(data.masked_prompt)) !== null) {
    const label = m[1];
    const ent = entitiesWithIndex.find((e) => e.label === label && e.index === -1);
    if (ent) {
      ent.index = idx++;
    }
  }

  return {
    ...data,
    masked_entities: entitiesWithIndex,
  };
}
