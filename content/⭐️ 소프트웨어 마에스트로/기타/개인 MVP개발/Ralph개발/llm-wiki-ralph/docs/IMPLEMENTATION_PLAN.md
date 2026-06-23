# IMPLEMENTATION_PLAN.md

Ralph 루프는 매 iteration마다 이 파일에서 **체크되지 않은(`[ ]`) 작업
중 가장 위에 있는 한 개**를 선택해 처리합니다. 완료 후 `[x]`로 변경하고
종료합니다.

작업은 **작게** 쪼개야 합니다. 한 iteration에서 완수 가능한 단위
(보통 30분~2시간 분량)여야 합니다.

---

## Phase 0: 프로젝트 부트스트랩

- [ ] **0.1** Next.js 15 프로젝트 초기화 (`create-next-app`,
  TypeScript strict, Tailwind, App Router 옵션 모두 켜기).
- [ ] **0.2** 의존성 설치: `gray-matter`, `react-markdown`,
  `remark-gfm`, `recharts`, `zod`, `@tanstack/react-query`.
- [ ] **0.3** ESLint, Prettier 설정 + `package.json`에 `typecheck`,
  `lint`, `format`, `test` 스크립트 추가.
- [ ] **0.4** Vitest 설치 및 샘플 테스트 1개 작성, `npm test` 통과 확인.
- [ ] **0.5** `.gitignore`에 `node_modules`, `.next`, `raw/`(개인 자료
  보호) 추가.

## Phase 1: 위키 데이터 레이어

- [ ] **1.1** `lib/schema.ts`에 회사 페이지 frontmatter zod 스키마
  정의 (`docs/SCHEMA.md` 참조).
- [ ] **1.2** `lib/wiki.ts`에 `wiki/` 디렉토리를 재귀 탐색해 페이지
  목록을 반환하는 `listPages()` 함수 작성.
- [ ] **1.3** `lib/wiki.ts`에 단일 페이지를 읽어 frontmatter + body를
  반환하는 `readPage(path)` 함수 작성.
- [ ] **1.4** `lib/wiki.ts`에 잘못된 frontmatter 페이지는 콘솔 경고
  후 스킵하는 로직 추가, 단위 테스트 작성.
- [ ] **1.5** `wiki/companies/샘플회사.md` 샘플 페이지 1개 작성하고
  스키마 통과 확인.

## Phase 2: 회사 대시보드 (가장 중요)

- [ ] **2.1** 라우트 `/companies/[slug]/page.tsx` 생성, 샘플 회사
  데이터를 읽어 회사명만 표시.
- [ ] **2.2** 회사 기본정보 헤더 컴포넌트(`CompanyHeader.tsx`) 작성:
  업종, 결산월, 사업자번호, 대표자.
- [ ] **2.3** 재무 추세 차트 컴포넌트(`FinancialChart.tsx`) 작성:
  Recharts LineChart로 매출/영업이익/차입금/자본금 연도별.
- [ ] **2.4** 주주 분포 테이블 컴포넌트(`ShareholderTable.tsx`) 작성:
  연도를 행, 주주를 열로.
- [ ] **2.5** 업무 이력 타임라인(`WorkTimeline.tsx`) 작성: 시간순,
  업무 유형 색상 구분.
- [ ] **2.6** 특이사항 누적 영역(`NotableEvents.tsx`) 작성.
- [ ] **2.7** 관련 원본 파일 링크 목록(`SourceLinks.tsx`) 작성.
- [ ] **2.8** 데이터 누락 시 fallback UI 추가 및 회사 대시보드 통합.

## Phase 3: 메인 대시보드

- [ ] **3.1** 라우트 `/page.tsx`에 회사 목록 카드 그리드 작성.
- [ ] **3.2** 최근 업데이트된 위키 페이지 5개 섹션 추가
  (mtime 기준 정렬).
- [ ] **3.3** 전체 통계 위젯(회사 수, 업무 유형별 건수) 추가.
- [ ] **3.4** 빈 상태 UI 추가 및 시각적 정돈.

## Phase 4: 위키 페이지 뷰어

- [ ] **4.1** 라우트 `/wiki/[...path]/page.tsx` 생성, 마크다운
  렌더링(react-markdown + remark-gfm).
- [ ] **4.2** 좌측 사이드바: `wiki/` 디렉토리 트리 컴포넌트 작성.
- [ ] **4.3** 위키링크 `[[페이지명]]`을 `<a>`로 변환하는
  remark/rehype 플러그인 작성.
- [ ] **4.4** 백링크 계산 함수: 모든 페이지를 스캔해 현재 페이지를
  가리키는 페이지 목록 반환.
- [ ] **4.5** 우측 사이드바: 백링크 + 출처 파일 링크 표시.

## Phase 5: 통합 검색

- [ ] **5.1** `lib/search.ts`에 단순 키워드 매칭 검색 함수 작성
  (frontmatter + 본문).
- [ ] **5.2** 라우트 `/search/page.tsx` 작성, 입력창과 결과 영역.
- [ ] **5.3** 결과 영역을 위키 페이지/원본 파일/회사 세 카테고리로
  분리.
- [ ] **5.4** 태그 필터 UI 추가 (연도, 회사, 업무 유형).

## Phase 6: 마무리

- [ ] **6.1** `wiki/index.md` 자동 생성 스크립트 작성.
- [ ] **6.2** 글로벌 네비게이션 바 (홈/검색/위키) 추가.
- [ ] **6.3** README.md 업데이트: 실행 방법, 디렉토리 구조.
- [ ] **6.4** 모든 P0 acceptance criteria 재확인 → `<promise>MVP_P0_DONE</promise>`.

---

## 발견된 작업 (작업 중 추가)

이 섹션에는 작업하다 발견했지만 이번 iteration에서 처리하지 않을
항목을 추가합니다. 다음 iteration에서 우선순위에 맞게 위 목록으로
편입됩니다.

(아직 없음)

---

## 작업 추가·수정 규칙

- 작업이 너무 크면 더 작게 쪼개세요.
- 작업이 막히면 `docs/QUESTIONS.md`에 질문을 남기고 다음 작업으로
  넘어가세요.
- P1, P2는 P0 완료 전까지 손대지 않습니다.
