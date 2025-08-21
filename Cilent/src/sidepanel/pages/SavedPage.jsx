import React from "react";
import styled from "styled-components";

export default function SavedPage({ savedList = [], deleteSaved = () => {}, fillFromSaved = () => {} }) {
  return (
    <Wrap>
      <List>
        {savedList.length === 0 && <Empty>저장된 프롬프트가 없습니다.</Empty>}
        {savedList.map(item => (
          <Item key={item.id}>
            <Meta>
              <Title>{item.title}</Title>
              <Date>{item.date}</Date>
            </Meta>
            
            <MaskedPreview>
              {item.masked || "결과가 없습니다."}
            </MaskedPreview>

            <Actions>
              <Btn onClick={() => fillFromSaved(item)}>불러오기</Btn>
              <Btn onClick={() => navigator.clipboard.writeText(item.masked || "")}>복사</Btn>
              <Btn danger onClick={() => deleteSaved(item.id)}>삭제</Btn>
            </Actions>
          </Item>
        ))}
      </List>
    </Wrap>
  );
}

const MaskedPreview = styled.pre`
  background: #f8fafc;
  padding: 8px;
  border-radius: 6px;
  font-size: 13px;
  color: #1e293b;
  max-height: 120px;
  overflow-y: auto;
  white-space: pre-wrap;
`;

const Wrap = styled.div`
  padding: 12px; display: grid; gap: 10px;
`;
const List = styled.div` display: grid; gap: 8px; `;
const Empty = styled.div` color: #6b7280; font-size: 14px; padding: 8px; `;
const Item = styled.div`
  background: #fff; border: 1px solid #e5e7eb; border-radius: 10px; padding: 10px; display: grid; gap: 8px;
`;
const Meta = styled.div` display: flex; justify-content: space-between; align-items: center; `;
const Title = styled.div` font-weight: 600; `;
const Date = styled.div` font-size: 12px; color: #6b7280; `;
const Actions = styled.div` display: flex; gap: 6px; `;
const Btn = styled.button`
  border: 0; border-radius: 8px; padding: 8px 10px; cursor: pointer;
  background: ${p => p.danger ? "#e35168" : "#eef2ff"};
  color: ${p => p.danger ? "#fff" : "#173b6c"};
`;
