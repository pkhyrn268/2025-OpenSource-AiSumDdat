const API_BASE = "https://chat.grer.tes.co";

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

  // 서버 명세서에 맞춰 파싱
  const body = await res.json().catch(() => ({}));
  if (!res.ok || body?.status >= 400) {
    const msg =
      body?.message ||
      `API 오류 (${res.status})`;
    throw new Error(msg);
  }

  // 성공: {status, message, data:{ original_prompt, masked_prompt, masked_entities[] }}
  return body?.data || {
    original_prompt: "",
    masked_prompt: "",
    masked_entities: [],
  };
}
