# 1. 원본 수집
- 각각의 소스(github, Jira, Confluence)마다 처리 단위가 달라야함.
	- Git은 커밋이 아니라 PR 단위
	- Jira는 이슈 단위로 코멘트/체인지로그 분리
	- Confluence는 페이지 버전 단위
	- Slack은 메시지가 아니라 스레드 단위
	- Drive는 파일 리비전 단위, 로컬 파일은 경로+콘텐츠 해시 기준

# 2. 멱등성
- 같은 파일인지 결정할 수 있어야함.
	- 파일 수정 vs 같은 파일 재처리

# 3. STT, OCR
- 과정에서 생기는 오류처리
	- confidence를 낮게 잡기.
	- 추출 신뢰도가 낮은 소스는 Async Lint 대상
