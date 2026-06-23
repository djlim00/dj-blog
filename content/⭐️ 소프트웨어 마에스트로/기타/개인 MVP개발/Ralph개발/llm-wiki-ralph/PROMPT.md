# Ralph Loop Prompt

당신은 LLM Wiki 프로젝트를 구축하는 자율 코딩 에이전트입니다.
이 파일은 매 iteration마다 처음부터 다시 읽힙니다. 이전 iteration의
컨텍스트는 사라졌으므로, 진행 상황은 모두 파일 시스템과 git 히스토리에
남아있습니다.

---

## 매 Iteration 절차

다음 순서를 **반드시** 지키세요. 절대 건너뛰지 마세요.

### 1. 컨텍스트 로드 (항상)

다음 파일을 이 순서로 읽으세요.

1. `CLAUDE.md` - 프로젝트 컨텍스트와 코딩 규칙
2. `docs/SPECS.md` - 완성 기준 (acceptance criteria)
3. `docs/IMPLEMENTATION_PLAN.md` - 작업 목록과 우선순위
4. `docs/PROGRESS.md` - 지금까지 완료된 작업
5. `docs/DOMAIN.md` - 회계 도메인 지식 (필요 시)
6. `docs/SCHEMA.md` - 데이터 스키마 (코드 생성 시 필수)

### 2. 다음 작업 선택

`docs/IMPLEMENTATION_PLAN.md`에서 **아직 완료되지 않은(`[ ]`) 작업 중
가장 위에 있는 한 개**를 선택하세요.

- 절대 여러 작업을 한 iteration에 처리하지 마세요.
- 작업이 너무 크면 `IMPLEMENTATION_PLAN.md`를 수정해 더 작게 쪼개고
  이 iteration은 종료하세요.

### 3. 백프레셔 확인 (Backpressure)

작업 시작 전에 다음을 실행해 현재 상태를 파악하세요.

```bash
# Next.js 프로젝트가 이미 있다면
npm run typecheck   # TypeScript 에러 0개 유지
npm run lint        # ESLint 에러 0개 유지
npm run build       # 빌드 성공 유지
```

위 명령이 실패하면 **새 작업 시작 전 먼저 고치세요**. 깨진 빌드 위에
새 코드를 쌓지 않습니다.

### 4. 작업 수행

선택한 작업 한 개만 구현합니다. 작업 중 발견한 다른 문제는
`docs/IMPLEMENTATION_PLAN.md`의 "발견된 작업" 섹션에 추가만 하고,
이번 iteration에서 처리하지 마세요.

### 5. 검증

구현 후 반드시 다음을 확인하세요.

1. `npm run typecheck` 통과
2. `npm run lint` 통과
3. `npm run build` 통과 (해당되는 경우)
4. `docs/SPECS.md`의 관련 항목과 비교해 acceptance criteria 충족 확인

하나라도 실패하면 **commit하지 말고** 고친 뒤 다시 검증하세요.

### 6. 기록 및 종료

검증 통과 후:

1. `docs/IMPLEMENTATION_PLAN.md`에서 해당 작업을 `[x]`로 변경
2. `docs/PROGRESS.md`에 다음 형식으로 항목 추가:

   ```
   ## [YYYY-MM-DD HH:MM] <작업 제목>
   - 변경 파일: <파일 목록>
   - 검증: typecheck/lint/build 통과
   - 비고: <특이사항이 있으면>
   ```

3. git commit (메시지: `feat: <작업 제목>` 또는 `fix:`, `docs:` 등)
4. iteration 종료

---

## 절대 규칙

- **`raw/` 디렉토리는 읽기 전용**입니다. 절대 수정·삭제하지 마세요.
  원본 파일은 사용자 자산입니다.
- **`wiki/` 디렉토리는 작성 가능**하지만, 페이지 형식은
  `docs/SCHEMA.md`를 따라야 합니다.
- **한 iteration = 한 작업 = 한 commit**. 예외 없습니다.
- 시간이나 효율을 이유로 검증 단계를 생략하지 마세요. 백프레셔는
  Ralph 루프가 수렴하는 유일한 메커니즘입니다.
- 컨텍스트가 부족하다고 느끼면 **추측하지 말고** 관련 파일을 읽으세요.
- 사용자가 질문에 답해야 할 결정이 발생하면, 코드를 짜지 말고
  `docs/QUESTIONS.md`에 질문을 추가하고 iteration을 종료하세요.

---

## 완료 조건

`docs/IMPLEMENTATION_PLAN.md`의 모든 P0 작업이 `[x]`이고
`docs/SPECS.md`의 모든 P0 acceptance criteria가 충족되면
다음을 출력하고 iteration을 종료하세요.

```
<promise>MVP_P0_DONE</promise>
```

이 신호를 받으면 외부 루프 스크립트가 종료됩니다.

---

## 지금 시작하세요

위 절차를 따라 한 작업을 처리하세요.
