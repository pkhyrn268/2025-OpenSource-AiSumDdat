
# 📖 Repository Guide

## 📌 브랜치 전략

```
main         ← 배포용 (최종 안정화 코드)
└─ develop   ← 통합 개발 브랜치
   ├─ ai      ← AI 기능 개발
   ├─ server  ← 백엔드 개발
   └─ client  ← 프론트엔드 개발
```

* **main**: 실제 서비스/배포되는 안정화된 코드만 머지됩니다.
* **develop**: 기능별 브랜치를 통합하는 개발용 브랜치입니다.
* **ai/server/client**: 각 영역별 기능 개발을 위한 브랜치입니다.

---

## 📌 작업 방식

1. **작업 시작**

   * `ai`, `server`, `client` 브랜치에서 **기능 단위 브랜치** 생성
   * 브랜치 네이밍 규칙:

     ```
     ai/feature-로그인
     server/fix-api-auth
     client/refactor-header
     ```

2. **커밋 규칙 (Conventional Commits)**

   ```
   feat: 새로운 기능 추가
   fix: 버그 수정
   refactor: 코드 리팩토링 (기능 변화 없음)
   style: 코드 스타일 변경 (포맷팅, 세미콜론 등)
   docs: 문서 수정
   chore: 빌드/설정/기타 변경
   test: 테스트 코드 추가/수정
   ```

   👉 예시

   ```
   feat: 로그인 API 연동
   fix: 대기열 카운트 오류 수정
   refactor: 부스 좋아요 기능 훅 분리
   ```

3. **PR 생성**

   * 작업 완료 시 `ai/server/client` → `develop` 으로 PR 생성
   * PR 템플릿을 활용해 **작업 내용 / 체크리스트 / 관련 이슈** 기입
   * 최소 1명 이상의 리뷰 후 머지

4. **머지 방식**

   * `develop` ← `main` 머지는 **릴리즈 단위**로 진행
   * `squash merge` 또는 `rebase`를 활용해 커밋 히스토리를 깔끔하게 유지

---

## 📌 폴더 구조

```
.github/                   # 이슈 & PR 템플릿
ai/                        # AI 관련 코드
server/                    # 백엔드 코드
client/                    # 프론트엔드 코드
README.md                  # 리포지토리 가이드
```

---

## 📌 협업 규칙

* **작업 시작 전**: 항상 최신 `develop` 브랜치 기준으로 rebase
* **커밋 단위**: 기능/버그별로 작게 쪼개기
* **코드 리뷰**: 모든 PR은 최소 1명 이상 리뷰 후 머지
* **이슈 관리**: 작업 시작 전 반드시 Issue 발행 후 브랜치 연결 (`Close #이슈번호`)


