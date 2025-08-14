import React from "react";
import styled from "styled-components";
import profileIcon from "../../assets/aiChat.svg";
import sendIcon from "../../assets/send.svg";
import MaskedViewer from "../components/MaskedViewer.jsx";


export default function ChatPage({
  input = "",
  setInput = () => {},
  messages = [],
  error = "",
  loading = false,
  onSend = () => {},
  pdfFile = null,
  setPdfFile = () => {},
}) {
  return (
    <Container>
      <MessagesContainer>
        {Array.isArray(messages) &&
          messages.map((m, i) => (
            <MessageRow key={i} isUser={m.role === "user"}>
              {m.role === "bot" && <ProfileImg src={profileIcon} alt="AI" />}
             {m.type === "maskedView" ? (
               <MaskedViewer
                 masked={m.masked}
                 entities={m.entities}
                 title="마스킹 결과"
               />
             ) : (
               <MessageBubble isUser={m.role === "user"} small={m.small}>
                 {m.text}
              </MessageBubble>
             )}
            </MessageRow>
          ))}
        {error && <ErrorText>⚠ {error}</ErrorText>}
        {loading && <LoadingText>처리 중…</LoadingText>}
      </MessagesContainer>

      <InputBar>
        <FileLabel title="PDF 첨부">
          <HiddenFile
            type="file"
            accept="application/pdf"
            onChange={(e) => setPdfFile(e.target.files?.[0] || null)}
          />
          📎
        </FileLabel>
        {pdfFile && <FileBadge>{pdfFile.name}</FileBadge>}

        <Input
          placeholder="답변을 입력해주세요."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); onSend(); }
          }}
        />
        <SendButton onClick={onSend} disabled={loading || !input.trim()}>
          <img src={sendIcon} alt="보내기" />
        </SendButton>
      </InputBar>
    </Container>
  );
}

const Container = styled.main`
  background: linear-gradient(180deg, #f0f0f0 0%, #d2e0fa 100%);
  width: 100%; height: calc(100vh - 70px);
  display: flex; flex-direction: column;
`;
const MessagesContainer = styled.div`
  flex: 1; padding: 16px; overflow-y: auto;
  display: flex; flex-direction: column; gap: 8px;
`;
const MessageRow = styled.div`
  display: flex; align-items: flex-start; gap: 1px;
  justify-content: ${(p) => (p.isUser ? "flex-end" : "flex-start")};
`;
const ProfileImg = styled.img`
  width: 40px; height: 40px; flex-shrink: 0;
`;
const MessageBubble = styled.div`
  max-width: 80%;
  padding: ${(p) => (p.small ? "8px 10px" : "12px 14px")};
  border-radius: 12px;
  background: ${(p) => (p.isUser ? "#E3F2FD" : "#F5F5F5")};
  color: ${(p) => (p.small ? "#6b7280" : "#000")};
  font-size: ${(p) => (p.small ? "12px" : "14px")};
  line-height: 1.5;
  white-space: pre-line;
`;
const ErrorText = styled.div` color: #b42318; font-size: 12px; `;
const LoadingText = styled.div` color: #6b7280; font-size: 12px; `;

const InputBar = styled.div`
  display: flex; align-items: center; gap: 8px;
  padding: 8px 12px; background: #fff; border-top: 1px solid #e5e7eb;
`;
const HiddenFile = styled.input` display: none; `;
const FileLabel = styled.label`
  display: inline-flex; align-items: center; justify-content: center;
  width: 34px; height: 34px; border-radius: 50%;
  border: 1px solid #d0d8ee; background: #f5f7ff; cursor: pointer;
`;
const FileBadge = styled.span`
  max-width: 160px; overflow: hidden; white-space: nowrap; text-overflow: ellipsis;
  font-size: 12px; color: #173b6c; background: #eef2ff; border: 1px solid #d6e0ff;
  padding: 4px 8px; border-radius: 999px;
`;
const Input = styled.input`
  flex: 1; border: none; outline: none;
  background: #f7f7f7; padding: 10px 14px; border-radius: 20px; font-size: 14px;
`;
const SendButton = styled.button`
  background: #4a90e2; border: none; padding: 8px; border-radius: 50%; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  img { width: 20px; height: 20px; }
  &:disabled { background: #cbd5e1; cursor: not-allowed; }
`;
