# LLM Wiki for Accountants

회계사·세무사를 위한 로컬 지식베이스. 회사별 영구조서를 시계열로
누적 관리하는 Next.js 앱과, Claude Code가 마크다운 위키를 유지보수
하는 시스템.

## 개발 방식

이 프로젝트는 [Ralph Wiggum 방법론](https://github.com/ghuntley/how-to-ralph-wiggum)
으로 개발됩니다. Claude Code에게 `PROMPT.md`를 반복 입력해 한
iteration마다 한 작업씩 처리하게 합니다.

## 디렉토리 구조

```
.
├── PROMPT.md              # Ralph 루프 진입점
├── CLAUDE.md              # Claude Code 프로젝트 컨텍스트
├── README.md              # 이 파일
├── docs/
│   ├── SPECS.md           # acceptance criteria
│   ├── IMPLEMENTATION_PLAN.md  # 작업 목록
│   ├── PROGRESS.md        # 완료 기록
│   ├── QUESTIONS.md       # 사용자 결정 대기
│   ├── DOMAIN.md          # 회계 도메인 지식
│   ├── SCHEMA.md          # 데이터 스키마
│   ├── MVP.md             # MVP 정의 (원본)
│   └── INTERVIEW.md       # 인터뷰 원본
├── raw/                   # 원본 자료 (READ-ONLY)
├── wiki/                  # LLM 생성 마크다운 위키
├── app/                   # Next.js
├── components/
├── lib/
└── scripts/
    └── ralph.sh           # Ralph 루프 실행 스크립트
```

## Ralph 루프 실행

### 한 번에 한 iteration (수동)

Claude Code 터미널을 열고:

```
> Read PROMPT.md and follow the procedure.
```

작업이 끝나면 종료. 다시 돌리려면 같은 명령 반복.

### 자동 루프 (셸 스크립트)

`scripts/ralph.sh`:

```bash
#!/usr/bin/env bash
set -e
MAX_ITER=${1:-50}
for i in $(seq 1 "$MAX_ITER"); do
  echo "=== Iteration $i ==="
  cat PROMPT.md | claude --print --continue
  if grep -q "MVP_P0_DONE" docs/PROGRESS.md 2>/dev/null; then
    echo "All P0 tasks complete."
    break
  fi
done
```

> 위 스크립트는 예시입니다. Claude Code의 실제 CLI 옵션에 맞춰
> 수정하세요. `--print` 대신 비대화형 모드, 또는 Anthropic 공식
> [ralph-loop 플러그인](https://awesomeclaude.ai/ralph-wiggum)
> 사용을 권장합니다.

## 어떻게 시작하는가

1. 이 디렉토리를 git 저장소로 초기화: `git init && git add . && git commit -m "init"`.
2. `raw/`에 원본 자료를 넣습니다 (이 디렉토리는 .gitignore로 커밋 제외).
3. Claude Code를 실행하고 `PROMPT.md`를 입력해 첫 iteration 시작.
4. 매 iteration마다 git commit이 1개씩 쌓이고 `docs/PROGRESS.md`에
   기록이 남습니다.
5. `<promise>MVP_P0_DONE</promise>`이 나오면 MVP 완성.

## 운영 원칙

- `raw/`는 절대 LLM이 수정하지 않습니다.
- `wiki/`는 LLM이 소유합니다. 사람이 수정해도 되지만 `SCHEMA.md`를
  지켜야 합니다.
- 의문이 생기면 `docs/QUESTIONS.md`에 추가하고 사용자가 답할 때까지
  대기.
- 백프레셔(typecheck/lint/build/test) 실패 시 commit 금지.

## 기술 스택

- Next.js 15 (App Router) + TypeScript strict + Tailwind CSS
- gray-matter, react-markdown, remark-gfm
- Recharts, zod, React Query
- Vitest

## 라이선스

(선택)
