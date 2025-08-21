import React, { useState } from "react";
import styled from "styled-components";

import menuIcon from "../../assets/menu.svg";
import notificationIcon from "../../assets/bell.png";   
import logoImage from "../../assets/logoImage.png";     
import logoText from "../../assets/logoText.svg";       

import trashIcon from "../../assets/trash.png";
import infoIcon from "../../assets/info.png";
import compareIcon from "../../assets/compare.png";
import bookmarkIcon from "../../assets/bookmark.png";
import copyIcon from "../../assets/copy.png";
import searchIcon from "../../assets/search.png";

export default function Header({ onNavigate, activePage }) {
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);

  return (
    <>
      <HeaderContainer>
        <LogoWrapper>
          <img src={logoImage} alt="로고" className="logo-icon" />
          <img src={logoText} alt="AITEACHER" className="logo-text" />
        </LogoWrapper>
        <IconsWrapper>
          <IconButton aria-label="알림">
            <img src={notificationIcon} alt="알림" />
          </IconButton>
          <IconButton aria-label="메뉴" onClick={() => setIsDrawerOpen(true)}>
            <img src={menuIcon} alt="메뉴" />
          </IconButton>
        </IconsWrapper>
      </HeaderContainer>

      <MenuDrawer
        open={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        onNavigate={(page) => {
          onNavigate(page);
          setIsDrawerOpen(false);
           if (page === "chat") {
            onNewChat();   
          }
        }}
        activePage={activePage}
      />
    </>
  );
}

/* ---------------- Drawer ---------------- */

function MenuDrawer({ open, onClose, onNavigate, activePage }) {
  return (
    <DrawerContainer className={open ? "open" : ""} role="dialog" aria-label="사이드 메뉴">
      <DrawerHeader>
        <DrawerTitle>Menu</DrawerTitle>
        <CloseButton onClick={onClose}>✕</CloseButton>
      </DrawerHeader>

      <DividerLine />

      <DrawerNav>
        <DrawerItem disabled>
          <IconImg src={copyIcon} alt="AI 채팅 기록" />
          <Label>AI 채팅 기록</Label>
        </DrawerItem>

        <DrawerItem disabled>
          <IconImg src={searchIcon} alt="AI 채팅 검색" />
          <Label>AI 채팅 검색</Label>
        </DrawerItem>

        <DrawerItem
          onClick={() => onNavigate("chat")}
          active={activePage === "chat"}
        >
          <IconImg src={compareIcon} alt="프롬프트 생성하기" />
          <Label>프롬프트 생성하기</Label>
        </DrawerItem>

        <DrawerItem
          onClick={() => onNavigate("saved")}
          active={activePage === "saved"}
        >
          <IconImg src={bookmarkIcon} alt="저장한 프롬프트" />
          <Label>저장한 프롬프트</Label>
        </DrawerItem>

        <DrawerItem disabled>
          <IconImg src={infoIcon} alt="도움말" />
          <Label>도움말</Label>
        </DrawerItem>

        <DrawerItem disabled>
          <IconImg src={trashIcon} alt="휴지통" />
          <Label>휴지통</Label>
        </DrawerItem>
      </DrawerNav>
    </DrawerContainer>
  );
}

/* ---------------- Styled Components ---------------- */

const HeaderContainer = styled.header`
  width: 100%;
  height: 70px;
  background: #ffffff;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.14);
`;

const LogoWrapper = styled.div`
  display: flex;
  align-items: center;
  gap: 6px;

  .logo-icon { height: 32px; }
  .logo-text { height: 18px; }
`;

const IconsWrapper = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-right: 30px;
`;

const IconButton = styled.button`
  background: none;
  border: none;
  padding: 4px;
  cursor: pointer;
  img { height: 24px; width: 24px; }
`;

/* Drawer base */
const DrawerContainer = styled.aside`
  position: fixed;
  top: 0;
  right: -280px;
  width: 280px;
  height: 100%;
  background: linear-gradient(180deg, #12315a 0%, #14365f 40%, #0e2b52 100%);
  color: #e7eefc;
  box-shadow: -12px 0 28px rgba(0, 0, 0, 0.35);
  transition: right 0.28s ease-in-out;
  z-index: 1000;

  &.open { right: 0; }
`;

const DrawerHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 58px;
  padding: 0 14px 0 16px;
`;

const DrawerTitle = styled.h2`
  font-size: 18px;
  margin: 0;
  font-weight: 500;
  letter-spacing: .2px;
  color: #f0f5ff;
  opacity: .95;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 20px;
  color: #c9d8ff;
  cursor: pointer;
`;

const DividerLine = styled.div`
  height: 1px;
  background: rgba(255,255,255,.2);
  margin: 0 0 6px 0;
`;

const DrawerNav = styled.nav`
  display: flex;
  flex-direction: column;
  padding: 8px;
  gap: 4px;
`;

const DrawerItem = styled.button.attrs(p => ({
  disabled: p.disabled || false
}))`
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  border: none;
  background: transparent;
  border-radius: 12px;
  text-align: left;

  /* 색상 규칙: 기본 흰색, active면 파랑 */
  color: ${({ active }) => (active ? "#4a90e2" : "#ffffff")};

  cursor: ${({ disabled }) => (disabled ? "default" : "pointer")};

  &:not(:disabled):hover {
    background: rgba(255,255,255,.07);
  }
`;


const IconImg = styled.img`
  width: 22px;
  height: 22px;
  flex-shrink: 0;
`;

const Label = styled.span`
  font-size: 14px;
  letter-spacing: .1px;
`;
