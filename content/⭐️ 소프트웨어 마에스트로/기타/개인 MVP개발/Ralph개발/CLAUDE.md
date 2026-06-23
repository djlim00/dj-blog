# CLAUDE.md

이 파일은 Claude Code가 매 세션 시작 시 자동으로 읽는 프로젝트 컨텍스트입니다.

## 프로젝트 개요

**이름**: LLM Wiki for Accountants (가칭)

**목적**: 회계사·세무사가 누적한 자료(재무제표, 조서, 보고서, 인터뷰
메모 등)를 LLM이 읽고 마크다운 위키로 정리·유지보수하는 로컬 도구.
RAG처럼 매 질의마다 검색하지 않고, 위키를 영속적 산출물로 키워간다.

**핵심 차별점**:
- 위키는 한 번 만들고 끝이 아니라 새 자료가 들어올 때마다 갱신된다.
- 회사별 대시보드(영구조서)가 시계열로 누적된다.
- 모든 답변은 원본 출처를 명시한다.

## 기술 스택

- **프론트엔드**: Next.js 15 (App Router), TypeScript strict, Tailwind CSS
- **상태 관리**: React Query (서버 상태)
- **마크다운**: gray-matter (frontmatter), react-markdown 또는 mdx
- **차트**: Recharts
- **데이터 저장**: 로컬 파일 시스템 (raw/, wiki/) + 필요 시 SQLite (인덱스)
- **LLM**: Claude Code 자체 (별도 API 호출 없음, 사용자 비용 절감)

쓰지 않는 것: Spring Boot, Docker, 외부 DB, 임베딩 벡터스토어,
인증·권한 시스템 (1인 로컬 사용 가정).

## 디렉토리 구조

```
.
├── PROMPT.md              # Ralph 루프 진입점
├── CLAUDE.md              # 이 파일
├── README.md
├── docs/
│   ├── SPECS.md           # 완성 기준
│   ├── IMPLEMENTATION_PLAN.md  # 작업 목록
│   ├── PROGRESS.md        # 완료 기록 (append-only)
│   ├── QUESTIONS.md       # 사용자 결정 대기 항목
│   ├── DOMAIN.md          # 회계 도메인 지식
│   ├── SCHEMA.md          # 데이터 스키마 명세
│   ├── MVP.md             # 원본 MVP 기능 정의
│   └── INTERVIEW.md       # 인터뷰 원본
├── raw/                   # 원본 자료 (READ-ONLY, 사용자 자산)
│   └── (사용자가 넣는 PDF, 엑셀, 한글 등)
├── wiki/                  # LLM이 생성·유지하는 위키 (LLM이 소유)
│   ├── index.md
│   ├── log.md
│   ├── companies/
│   ├── concepts/
│   └── sources/
├── app/                   # Next.js App Router 페이지
├── components/
├── lib/                   # 마크다운 파싱, 검색 등
└── scripts/               # Ralph 루프 셸 스크립트
```

## 코딩 규칙

### TypeScript
- `strict: true` 유지. `any` 금지 (불가피하면 주석으로 사유 명시).
- 외부 데이터(frontmatter, 사용자 입력)는 zod로 검증.
- 컴포넌트 props는 명시적 인터페이스로 정의.

### 컴포넌트
- 서버 컴포넌트가 기본. `'use client'`는 인터랙션 필요 시에만.
- 파일명: PascalCase (`CompanyDashboard.tsx`).
- 한 파일 한 컴포넌트 원칙.

### 스타일
- Tailwind 유틸리티 우선. 커스텀 CSS는 최후 수단.
- 색상은 Tailwind palette 또는 CSS 변수 사용. 하드코딩 hex 금지.

### 파일 I/O
- raw/ 읽기는 가능하지만 수정·삭제 금지.
- wiki/ 쓰기는 반드시 `docs/SCHEMA.md`의 형식을 따른다.
- frontmatter 필수 필드 누락 금지. zod로 검증 후 저장.

### 한글 도메인 용어
- 코드 식별자는 영문(`company`, `audit`, `taxFiling`).
- UI 텍스트와 위키 본문은 한글.
- 주석은 한글 허용.

## 위키 작성 규칙

### Frontmatter
모든 위키 페이지는 YAML frontmatter로 시작합니다. 필수 필드는
`docs/SCHEMA.md`를 참조하세요.

### 위키링크
페이지 간 연결은 `[[페이지명]]` 형식. Obsidian 호환.

### 출처 표기
모든 사실 주장 끝에 출처를 명시합니다.

```
A사의 2024년 매출은 100억이다. [^src1]

[^src1]: raw/A사_재무제표_2024.xlsx, "손익계산서" 시트
```

LLM 추정인 경우:

```
A사는 IT 업종으로 추정된다. [LLM 추정: raw/A사_조서_2024.pdf의 매출
구성 분석 기반]
```

### index.md와 log.md
- `wiki/index.md`: 모든 위키 페이지 카탈로그. 매 ingest마다 갱신.
- `wiki/log.md`: 무슨 일이 언제 일어났는지의 append-only 기록.
  형식: `## [YYYY-MM-DD] ingest|query|lint | <제목>`

## Ralph 루프 작업 방식

이 프로젝트는 [Ralph Wiggum 방법론](https://github.com/ghuntley/how-to-ralph-wiggum)으로
개발됩니다. 핵심 원칙:

1. **각 iteration은 fresh context**로 시작한다. 이전 작업은 파일에만
   남는다.
2. **한 iteration = 한 작업 = 한 commit**.
3. **백프레셔로 수렴한다**: 잘못된 코드는 typecheck/lint/build가 거부.
4. **진행 상황은 PROGRESS.md와 git log에 있다**.

상세 절차는 `PROMPT.md`를 참조하세요.

## 참조 문서

- 도메인 이해 → `docs/DOMAIN.md`, `docs/INTERVIEW.md`
- 무엇을 만드는가 → `docs/MVP.md`, `docs/SPECS.md`
- 다음에 뭘 하는가 → `docs/IMPLEMENTATION_PLAN.md`
- 어떤 형식으로 → `docs/SCHEMA.md`
- 지금까지 한 것 → `docs/PROGRESS.md`, `git log`
