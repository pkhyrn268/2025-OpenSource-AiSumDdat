// src/hooks/useChat.js
import { useEffect, useMemo, useState } from "react";
import { uploadMasking } from "../lib/api.js";
import { loadSaved, saveAll } from "../lib/storage.js";

// ✅ 새 멘트 & 질문
const INTRO = [
  "안녕하세요! \n\nAI에게 더 정확한 답변을 얻을 수 있도록 최적의 프롬프트를 함께 만들어 드리는 AI 프롬프트 도우미입니다.",
  "몇 가지 질문에 답해 주시면,\n AI의 답변 퀄리티를 높이고 개인정보 유출을 방지하는 완성된 프롬프트를 만들어 드려요.\n\n자, 그럼 시작해 볼까요? ✨",
];

const QUESTIONS = [
  "이번에 AI에게 어떤 작업을 시키고 싶으신가요? \n(예시: 보고서 작성, 코드 분석, 여행 계획 세우기)",
  "AI에게 전달할 프롬프트 전문을 작성해주세요.",
  "답변은 어떤 형식으로 받고 싶으신가요? \n(리스트 / 표 / 보고서 / 코드 등 자유롭게 선택해 주세요.)",
  "답변의 길이는 어느 정도가 적당할까요? \n(간결하게 / 상세하게 / 매우 자세하게)",
  "답변의 난이도를 어느 수준에 맞출까요? \n(초등학생 / 고등학생 / 대학생 / 전문가)",
  "마지막으로, AI에게 참고할 만한 자료(PDF, 텍스트 등)가 있다면 추가해 주세요.",
];

export default function useChat() {
  const [page, setPage] = useState("chat");

  // 채팅
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState([
    { role: "bot", text: INTRO[0] },
    { role: "bot", text: INTRO[1] },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // 질문 단계/답변
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({
    question1: "", question2: "", question3: "",
    question4: "", question5: "", question6: "",
  });

  // 파일
  const [pdfFile, setPdfFile] = useState(null);

  // 저장
  const [savedList, setSavedList] = useState([]);
  useEffect(() => { loadSaved().then(setSavedList); }, []);

  // 첫 질문 표시
  useEffect(() => {
    if (!messages.some(m => m._askedFirst)) {
      setMessages(prev => [
        ...prev,
        { role: "bot", text: `【질문 1】 ${QUESTIONS[0]}`, _askedFirst: true },
        // 질문 6의 “작은 글씨” 안내는 실제 작은 글씨로 표기
      ]);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onSend = async () => {
    const text = input.trim();
    if (!text || loading) return;

    // 사용자 답변 저장
    setMessages(prev => [...prev, { role: "user", text }]);
    const key = `question${step + 1}`;
    setAnswers(prev => ({ ...prev, [key]: text }));
    setInput("");

    // 다음 질문 or 업로드
    if (step < QUESTIONS.length - 1) {
      const next = step + 1;
      setStep(next);

      const nextMsg = { role: "bot", text: `【질문 ${next + 1}】 ${QUESTIONS[next]}` };
      // 질문 6에는 작은 글씨 안내 추가
      const smallNote = (next === 5)
        ? { role: "bot", text: "※ 파일은 PDF 권장, 없으면 텍스트로 입력하셔도 좋습니다.", small: true }
        : null;

      setMessages(prev => smallNote ? [...prev, nextMsg, smallNote] : [...prev, nextMsg]);
      return;
    }

    // 모든 답변 모였으면 업로드
    try {
      setLoading(true);
      setError("");
      setMessages(prev => [
        ...prev,
        { role: "bot", text: "마스킹 처리를 진행 중입니다… (잠시만 기다려주세요)" },
      ]);

      const data = await uploadMasking(answers, pdfFile);
      const { original_prompt = "", masked_prompt = "", masked_entities = [] } = data || {};

      setMessages(prev => [
        ...prev,
        { role: "bot", text: "마스킹 처리가 완료되었습니다." },
        { role: "bot", text: `원본 프롬프트\n${original_prompt}` },
        { role: "bot", text: `마스킹 프롬프트\n${masked_prompt}` },
        masked_entities?.length
          ? { role: "bot",
              text:
                "마스킹된 엔티티 목록\n" +
                masked_entities.map(e => `- ${e.entity} (${e.label})`).join("\n")
            }
          : { role: "bot", text: "마스킹된 엔티티가 감지되지 않았습니다." },
      ]);
    } catch (e) {
      console.error(e);
      setError(e?.message || "서버 연결 실패");
      setMessages(prev => [...prev, { role: "bot", text: "처리 중 오류가 발생했습니다." }]);
    } finally {
      setLoading(false);
      // 다음 대화를 위해 초기화
      setStep(0);
      setPdfFile(null);
      setMessages(prev => [
        ...prev,
        { role: "bot", text: `【질문 1】 ${QUESTIONS[0]}` },
      ]);
    }
  };

  const deleteSaved = async (id) => {
    const next = savedList.filter(it => it.id !== id);
    setSavedList(next); await saveAll(next);
  };
  const fillFromSaved = (item) => { setPage("chat"); setInput(item.text || ""); };

  return {
    page, setPage,
    input, setInput, messages, loading, error, onSend,
    pdfFile, setPdfFile,
    savedList, deleteSaved, fillFromSaved,
  };
}
