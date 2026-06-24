---
title: DJ's Blog
---

<style>
.post-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin: 2rem 0;
}
.post-card {
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  gap: 1.25rem;
  padding: 1.1rem 1.25rem;
  border-radius: 12px;
  background: var(--lightgray);
  text-decoration: none !important;
  transition: transform 0.15s ease, background 0.15s ease;
  color: var(--darkgray);
}
.post-card:hover {
  transform: translateY(-2px);
  background: var(--highlight);
}
.post-card-text {
  flex: 1 1 auto;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.post-card-text h3 {
  margin: 0;
  font-size: 1.15rem;
  color: var(--dark);
  font-weight: 700;
  line-height: 1.35;
}
.post-card-text p {
  margin: 0;
  font-size: 0.92rem;
  color: var(--gray);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.post-card-date {
  font-size: 0.78rem;
  color: var(--gray);
  margin-top: auto;
}
.post-card-thumb {
  flex: 0 0 110px;
  width: 110px;
  height: 110px;
  border-radius: 10px;
  overflow: hidden;
  background: var(--light);
  display: flex;
  align-items: center;
  justify-content: center;
}
.post-card-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.post-card-thumb-fallback {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--secondary);
  text-align: center;
  padding: 0.5rem;
}
@media (max-width: 600px) {
  .post-card-thumb {
    flex-basis: 80px;
    width: 80px;
    height: 80px;
  }
}
.categories {
  margin: 1rem 0 2rem;
}
</style>

안녕하세요. 임동주의 개인 블로그입니다.

기록하고 공유하고 싶은 글들을 모아둔 공간입니다.

## 카테고리

<div class="categories">

- [[🎓 대학교|🎓 대학교]] — 학교 수업 노트와 과제
- [[⭐️ 소프트웨어 마에스트로|⭐️ 소프트웨어 마에스트로]] — 소마 활동 기록
- [[🎉 컨퍼런스|🎉 컨퍼런스]] — 참석한 컨퍼런스 정리
- [[📖개인공부|📖개인공부]] — 개인 공부 기록
- [[📚유레카2기|📚유레카2기]] — 유레카 2기 활동

</div>

## 최근 글

<div class="post-grid">

<a href="./⭐️-소프트웨어-마에스트로/CS스터디/데이터베이스--1" class="post-card">
  <div class="post-card-text">
    <h3>데이터베이스 -1</h3>
    <p>데이터베이스 - 일정한 규칙으로 구조화해서 저장되는 데이터의 모음 - DBMS - Query언어를 통해서 CRUD - SQL 1. 트랜잭션 2. 동시공유 3. 권한 4. 암호화 5. 백업 복구 1. Entity -…</p>
    <span class="post-card-date">2026.06.24</span>
  </div>
  <div class="post-card-thumb"><img src="./_첨부파일/Pasted%20image%2020250303142002.png" alt=""/></div>
</a>
<a href="./📖개인공부/CS스터디/데이터베이스/3-3.-TEXT와-BLOB" class="post-card">
  <div class="post-card-text">
    <h3>3-3. TEXT와 BLOB</h3>
    <p>문자열 : TEXT - 최대 65,535개 길이의 텍스트 데이터를 저장할 수 있음. - VARCHAR 1. 행 내부에 저장 : VARCHAR(100)을 선언하면 행 내부에 400바이트가 필요함 2. 65535까지 m…</p>
    <span class="post-card-date">2026.06.24</span>
  </div>
  <div class="post-card-thumb"><img src="./_첨부파일/Pasted%20image%2020250303143629.png" alt=""/></div>
</a>
<a href="./⭐️-소프트웨어-마에스트로/무제-1" class="post-card">
  <div class="post-card-text">
    <h3>무제 1</h3>
    <p>두 가지를 정리하겠습니다. 먼저 용어 문제부터 풀고, 그 다음 단일 사실 쪽 로직을 자세히 그리겠습니다. 용어 — 혼동의 원인을 짚으면 &quot;단일 사실&quot;이 헷갈리는 이유가 명확합니다. 보고서 하나에서 사실이 여러 개 나…</p>
    <span class="post-card-date">2026.06.23</span>
  </div>
  <div class="post-card-thumb"><div class="post-card-thumb-fallback">무제</div></div>
</a>
<a href="./⭐️-소프트웨어-마에스트로/CS스터디/운영체제---2" class="post-card">
  <div class="post-card-text">
    <h3>운영체제 - 2</h3>
    <p>1. PCB와 컨텍스트 스위칭 - 프로세스 상태 - 대기, 실행 - 프로세스 번호(PID) - 프로그램 카운터(PC) - 레지스터 정보 - 메모리 제한 - 열린 파일 정보 - 해당 프로세스를 위한 파일 목록 2. 컨…</p>
    <span class="post-card-date">2026.06.23</span>
  </div>
  <div class="post-card-thumb"><img src="./_첨부파일/Pasted%20image%2020250320132946.png" alt=""/></div>
</a>
<a href="./⭐️-소프트웨어-마에스트로/특강/멘토특강---LLM,-3일만에-배우는-Langchain과-OpenAI-활용" class="post-card">
  <div class="post-card-text">
    <h3>멘토특강 - LLM, 3일만에 배우는 Langchain과 OpenAI 활용</h3>
    <p>- 사용자의 질문 - 질문을 더 확대 - 이 사람이 이걸 왜 물었을까? - 문장을 만들어내면서 == 생각을 넓히면서(Thinking) - 의도를 파악하고 - 문장을 만들어낸다. RAG - 이미 있는 데이터(pre-t…</p>
    <span class="post-card-date">2026.06.22</span>
  </div>
  <div class="post-card-thumb"><div class="post-card-thumb-fallback">멘토</div></div>
</a>
<a href="./📖개인공부/CS스터디/운영체제/4-11.-프로세스의-메모리-구조" class="post-card">
  <div class="post-card-text">
    <h3>4-11. 프로세스의 메모리 구조</h3>
    <p>- 스택 - 힙 - 데이터영역 - 코드 1. 스택 : 지역변수, 매개변수, 함수가 저장 - 컴파일 시 크기가 결정 - 재귀함수의 경우 런타임시에도 크키가 변경(==동적==) 2. 힙 : 동적 할당을 할 때 사용되며…</p>
    <span class="post-card-date">2026.06.22</span>
  </div>
  <div class="post-card-thumb"><img src="./_첨부파일/Pasted%20image%2020250319232720.png" alt=""/></div>
</a>
<a href="./⭐️-소프트웨어-마에스트로/CS스터디/운영체제---1" class="post-card">
  <div class="post-card-text">
    <h3>운영체제 - 1</h3>
    <p>- GUI(화면) - CUI(키보드만 사용 - 터미널) 운영체제의 역할 1. CPU 스케쥴링, 프로세스 관리 2. 메모리 관리 3. 디스크 파일 관리 4. 입출력 장비 관리 사실상 OS와 커널은 같은 의미로 사용된다…</p>
    <span class="post-card-date">2026.06.22</span>
  </div>
  <div class="post-card-thumb"><img src="./_첨부파일/Pasted%20image%2020260622093913.png" alt=""/></div>
</a>
<a href="./⭐️-소프트웨어-마에스트로/무제" class="post-card">
  <div class="post-card-text">
    <h3>무제</h3>
    <p>스프레드 시트 - row, column 기반의 스프레드 시트 파일 - 값으로는 텍스트, 이미지, 도형 등이 들어감 - 스프레드 시트의 종류에 따라서 이게 모든 값을 다 LLM을 타면서 읽을 필요가 있을까? -…</p>
    <span class="post-card-date">2026.06.21</span>
  </div>
  <div class="post-card-thumb"><div class="post-card-thumb-fallback">무제</div></div>
</a>
<a href="./⭐️-소프트웨어-마에스트로/Inget파이프라인" class="post-card">
  <div class="post-card-text">
    <h3>Inget파이프라인</h3>
    <p>1. 원본 수집 - 각각의 소스(github, Jira, Confluence)마다 처리 단위가 달라야함. - Git은 커밋이 아니라 PR 단위 - Jira는 이슈 단위로 코멘트/체인지로그 분리 - Confluence…</p>
    <span class="post-card-date">2026.06.21</span>
  </div>
  <div class="post-card-thumb"><div class="post-card-thumb-fallback">In</div></div>
</a>
<a href="./⭐️-소프트웨어-마에스트로/CS스터디/네트워크---5" class="post-card">
  <div class="post-card-text">
    <h3>네트워크 - 5</h3>
    <p>1. REST API - REST규칙을 지키는 API - 총 8가지의 규칙이 있음. 1. Uniform-Interface - API에서 자원들은 각각의 독립적인 인터페이스를 가짐 - URL 자원식별 - 표현을 통한…</p>
    <span class="post-card-date">2026.06.20</span>
  </div>
  <div class="post-card-thumb"><img src="./_첨부파일/Pasted%20image%2020250224130759.png" alt=""/></div>
</a>
<a href="./⭐️-소프트웨어-마에스트로/CS스터디/네트워크---4" class="post-card">
  <div class="post-card-text">
    <h3>네트워크 - 4</h3>
    <p>1. 세션 기반 인증방식 - HTTP는 무상태성(로그인을 어떻게 기억하지?) - &lt;mark style=&quot;background: FFF3A3A6;&quot;세션&lt;/mark : 서버와 클라이언트의 연결이 활성화된 상태 - &lt;mar…</p>
    <span class="post-card-date">2026.06.20</span>
  </div>
  <div class="post-card-thumb"><img src="./_첨부파일/Pasted%20image%2020250220113404.png" alt=""/></div>
</a>
<a href="./⭐️-소프트웨어-마에스트로/CS스터디/네트워크---2" class="post-card">
  <div class="post-card-text">
    <h3>네트워크 - 2</h3>
    <p>1. 라우팅 - 최적의 경로로 네트워크에서 데이터를 보내는 과정 - 라우터 라우터 - 패킷의 최적의 경로 설정 - 쏘는 것 까지 함 - &lt;mark class=&quot;hltr-yellow&quot;라우팅 테이블 기반으로 전달&lt;/ma…</p>
    <span class="post-card-date">2026.06.19</span>
  </div>
  <div class="post-card-thumb"><img src="./_첨부파일/Pasted%20image%2020250213171151.png" alt=""/></div>
</a>

</div>

## Links

- GitHub: [@djlim00](https://github.com/djlim00)
