import React from "react";
import styled from "styled-components";

export default function SavedPage({ savedList = [], deleteSaved = () => {}, fillFromSaved = () => {} }) {
  return (
    <Wrap>
      <Search placeholder="저장된 프롬프트 검색" />
      <List>
        {savedList.length === 0 && <Empty>저장된 프롬프트가 없습니다.</Empty>}
        {savedList.map(item => (
          <Item key={item.id}>
            <Meta>
              <Title>{item.title}</Title>
              <Date>{item.date}</Date>
            </Meta>
            <Actions>
              <Btn onClick={() => fillFromSaved(item)}>불러오기</Btn>
              <Btn onClick={() => navigator.clipboard.writeText(item.text)}>복사</Btn>
              <Btn danger onClick={() => deleteSaved(item.id)}>삭제</Btn>
            </Actions>
          </Item>
        ))}
      </List>
    </Wrap>
  );
}

const Wrap = styled.div`
  padding: 12px; display: grid; gap: 10px;
`;
const Search = styled.input`
  width: 100%; padding: 10px 12px; border-radius: 10px; border: 1px solid #dbe2f0;
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
