# SCHEMA.md - 데이터 스키마 명세

위키의 모든 페이지는 이 문서의 형식을 따릅니다. LLM이 위키 페이지를
생성하거나 코드에서 frontmatter를 파싱할 때 이 스키마를 사용합니다.

zod 구현은 `lib/schema.ts`에 있습니다. 이 두 문서는 **항상 동기화**
되어야 합니다.

---

## 공통 frontmatter 필드

모든 페이지에 적용되는 필드.

```yaml
---
title: string             # 페이지 제목 (필수)
type: company | concept | source | report  # 페이지 유형 (필수)
created: YYYY-MM-DD       # 생성일 (필수)
updated: YYYY-MM-DD       # 마지막 갱신일 (필수)
tags: [string, ...]       # 태그 배열 (선택, 기본 [])
sources: [string, ...]    # 원본 파일 경로 배열 (선택)
---
```

---

## 회사 페이지 (`type: company`)

위치: `wiki/companies/<slug>.md`

```yaml
---
title: string             # 회사명, 예: "A사"
type: company
slug: string              # URL용 식별자, 예: "a-sa"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [string, ...]

# 기본 정보
business_number: string         # 사업자번호 (선택)
industry: string                # 업종, 예: "제조업"
fiscal_month: number            # 결산월, 1-12
representative: string          # 대표자명 (선택)
external_audit: boolean         # 외감 여부 (선택, 기본 false)

# 시계열 재무 데이터
financials:
  - year: number
    revenue: number             # 매출 (원 단위 또는 백만원 단위, 일관 유지)
    operating_profit: number    # 영업이익
    debt: number                # 차입금
    capital: number             # 자본금
    note: string                # 비고 (선택)

# 시계열 주주 분포
shareholders:
  - year: number
    holders:                    # 주주 → 지분율(%) 매핑
      홍길동: number
      김철수: number

# 업무 이력
work_history:
  - date: YYYY-MM-DD
    type: audit | tax | valuation | service | consulting
    title: string
    summary: string             # 한두 줄 요약
    wiki_page: string           # 관련 위키 페이지 경로 (선택)
    sources: [string, ...]      # 원본 파일 경로 배열

# 자동/수동 추출 특이사항
notable_events:
  - date: YYYY-MM-DD
    text: string                # 한 문장 요약, 예: "차입금 30% 감소"
    auto: boolean               # LLM 자동 추출 여부
    source: string              # 근거 파일 (선택)

# 관련 원본 파일 (sources 공통 필드와 별개로 회사 전체 자료)
related_files: [string, ...]
---

# (본문은 자유 마크다운)

## 회사 개요

A사는 ... [^src1]

[^src1]: raw/A사_조서_2024.pdf, p.3
```

### 검증 규칙
- `slug`는 영문 소문자·숫자·하이픈만 허용 (`/^[a-z0-9-]+$/`).
- `fiscal_month`는 1~12.
- `financials[].year`는 1900~2100.
- `shareholders[].year`의 합계는 검증하지 않음(우선주·자기주식 등으로
  100%가 안 될 수 있음).
- `work_history[].type`은 enum 고정값.

---

## 개념 페이지 (`type: concept`)

위치: `wiki/concepts/<slug>.md`

업종, 평가 방법론, 세법 항목 등 추상적 주제.

```yaml
---
title: string
type: concept
slug: string
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [string, ...]
related_companies: [string, ...]   # 이 개념이 적용되는 회사 slug 배열
sources: [string, ...]
---

# 본문 (자유)
```

---

## 원본 자료 페이지 (`type: source`)

위치: `wiki/sources/<slug>.md`

원본 파일 1개에 대한 LLM 요약·메타데이터 페이지. 원본은 `raw/`에
그대로 두고, 요약은 여기.

```yaml
---
title: string
type: source
slug: string
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [string, ...]

# 원본 파일 정보
source_file: string         # 예: "raw/A사_재무제표_2024.xlsx" (필수)
file_type: xlsx | pdf | hwp | docx | image | other
ingested_at: YYYY-MM-DD
related_company: string     # 회사 slug (선택)
---

# 본문: LLM 요약, 핵심 인용, 참조해야 할 부분
```

---

## 보고서/분석 페이지 (`type: report`)

위치: `wiki/reports/<slug>.md`

사용자가 LLM에게 질문해서 받은 분석 결과를 보존할 때.

```yaml
---
title: string
type: report
slug: string
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [string, ...]
question: string            # 원래 질문
related_companies: [string, ...]
sources: [string, ...]
---

# 본문 (분석 결과)
```

---

## 특수 페이지

### `wiki/index.md`
모든 위키 페이지의 카탈로그. frontmatter 없이 카테고리별로 페이지
목록과 한 줄 요약. LLM이 매 ingest마다 갱신.

### `wiki/log.md`
이벤트 로그. 형식:

```markdown
## [2026-04-02] ingest | A사 재무제표 2024
- 처리 파일: raw/A사_재무제표_2024.xlsx
- 갱신 페이지: companies/a-sa.md, sources/a-sa-fs-2024.md, index.md

## [2026-04-03] query | A사 vs B사 차입금 비교
- 산출 페이지: reports/a-vs-b-debt-comparison.md
```

`grep "^## \[" wiki/log.md | tail -10`으로 최근 활동 확인.

---

## 위키링크와 출처 표기 (재확인)

### 위키링크
- 페이지 간 연결: `[[페이지명]]` 또는 `[[slug|표시명]]`.
- 백링크는 `lib/wiki.ts`가 자동 계산.

### 출처
- 모든 사실 진술 끝에 각주 `[^src1]`로 표기.
- 각주 정의에 **파일 경로 + 위치 정보**(페이지·시트·셀):

  ```
  [^src1]: raw/A사_재무제표_2024.xlsx, "손익계산서" 시트
  [^src2]: raw/A사_조서_2024.pdf, p.7
  ```

- LLM 추정은 별도 표기:

  ```
  업종은 IT로 추정된다. [LLM 추정: 매출 구성 기반]
  ```

---

## 단위·표기 일관성

- 금액: **백만원 단위** (frontmatter에서 가독성 유리). 본문에는 단위
  명시.
- 날짜: ISO 8601 (`YYYY-MM-DD`).
- 지분율: 백분율 숫자 (60.5는 60.5%).
- 회사 slug: 영문 소문자·하이픈.

스키마가 변경되면 이 문서를 먼저 수정하고, `lib/schema.ts`를 업데이트
한 뒤, 기존 페이지 마이그레이션 작업을
`docs/IMPLEMENTATION_PLAN.md`에 추가하세요.
