import React, { useState } from "react";
import styled from "styled-components";
import menuIcon from "../../assets/menu.svg";
import notificationIcon from "../../assets/bell.png";   // png 사용
import logoImage from "../../assets/logoImage.png";     // png 사용
import logoText from "../../assets/logoText.svg";       // 텍스트 로고

export default function Header({ onNavigate }) {
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
        }}
      />
    </>
  );
}

/* ---------------- Drawer ---------------- */

function MenuDrawer({ open, onClose, onNavigate }) {
  return (
    <DrawerContainer className={open ? "open" : ""} role="dialog" aria-label="사이드 메뉴">
      <DrawerHeader>
        <DrawerTitle>Menu</DrawerTitle>
        <CloseButton onClick={onClose}>✕</CloseButton>
      </DrawerHeader>

      <DividerLine />

      <DrawerNav>
        {/* 모양만, 클릭 비활성 */}
        <DrawerItem disabled>
          <Emoji aria-hidden>📄</Emoji>
          <Label>AI 채팅 기록</Label>
        </DrawerItem>

        <DrawerItem disabled>
          <Emoji aria-hidden>🔍</Emoji>
          <Label>AI 채팅 검색</Label>
        </DrawerItem>

        <DrawerItem disabled accent>
          <Emoji aria-hidden>✍️</Emoji>
          <Label>프롬프트 생성하기</Label>
        </DrawerItem>

        {/* 저장된 프롬프트만 동작 */}
        <DrawerItem onClick={() => onNavigate("saved")}>
          <Emoji aria-hidden>⭐</Emoji>
          <Label>저장한 프롬프트</Label>
        </DrawerItem>

        <DrawerItem disabled>
          <Emoji aria-hidden>🤝</Emoji>
          <Label>프롬프트 공유하기</Label>
        </DrawerItem>

        <DrawerItem disabled>
          <Emoji aria-hidden>ℹ️</Emoji>
          <Label>도움말</Label>
        </DrawerItem>

        <DrawerItem disabled>
          <Emoji aria-hidden>🗑️</Emoji>
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
  /* 디자인처럼 그림자 강화 */
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
  /* 디자인 네이비 톤 */
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
  font-weight: 700;
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
  color: ${({ disabled }) => (disabled ? "rgba(231,238,252,.75)" : "#ffffff")};
  cursor: ${({ disabled }) => (disabled ? "default" : "pointer")};
  border-radius: 12px;
  text-align: left;

  ${({ accent }) => accent && `
    color: #bcd4ff;
  `}

  &:not(:disabled):hover {
    background: rgba(255,255,255,.07);
  }
`;

const Emoji = styled.span`
  width: 22px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  font-size: 18px;
`;

const Label = styled.span`
  font-size: 14px;
  letter-spacing: .1px;
`;
