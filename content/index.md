---
title: Dong-Log
---

Hey there 👋

저는 **임동준**입니다. 백엔드 개발과 시스템 설계에 관심이 많고, 다양한 곳들에서 배운 것·기록하고 싶은 것을 이 공간에 모으고 있어요.

옵시디언으로 정리하는 것이 취미입니다.

**읽고, 정리하고, 공유합니다. 천천히, 그러나 꾸준히!**

<!-- AUTO-GENERATED BELOW: managed by scripts/build-index.py -->

<aside id="homepage-categories-widget" hidden>
<div class="cat-widget-title">카테고리</div>
<nav class="cat-grid"><a class="cat-chip" href="./대규모시스템설계1/"><span class="cat-chip-name">대규모시스템설계1</span><span class="cat-chip-count">6</span></a><a class="cat-chip" href="./카프카/"><span class="cat-chip-name">카프카</span><span class="cat-chip-count">6</span></a><a class="cat-chip" href="./studygroup-프로젝트/"><span class="cat-chip-name">StudyGroup 프로젝트</span><span class="cat-chip-count">2</span></a><a class="cat-chip" href="./bytebytego-아티클/"><span class="cat-chip-name">ByteByteGo 아티클</span><span class="cat-chip-count">1</span></a><a class="cat-chip" href="./uhyu프로젝트/"><span class="cat-chip-name">Uhyu프로젝트</span><span class="cat-chip-count">1</span></a><a class="cat-chip" href="./대규모시스템설계2/"><span class="cat-chip-name">대규모시스템설계2</span><span class="cat-chip-count">1</span></a></nav>
</aside>
<script>
(function () {
  function moveCategoriesToSidebar() {
    var widget = document.getElementById('homepage-categories-widget');
    var sidebar = document.querySelector('.sidebar.right');
    if (!widget || !sidebar) return;
    if (widget.parentElement !== sidebar) {
      sidebar.appendChild(widget);
    }
    widget.hidden = false;
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', moveCategoriesToSidebar);
  } else {
    moveCategoriesToSidebar();
  }
  document.addEventListener('nav', moveCategoriesToSidebar);
})();
</script>

## 최근 게시물

<div class="post-stream">

<article class="post-card">
  <h2 class="post-card-title"><a href="./bytebytego-아티클/9.-bytebytego--ai-에이전트는-어떻게-기억을-관리하고-망각을-피하는가">[ByteByteGo] AI 에이전트는 어떻게 기억을 관리하고 망각을 피하는가</a></h2>
  <p class="post-card-meta">
    <span class="post-card-date">2026-07-05</span>
    <span class="post-card-author">작성자 djlim00</span>
    <a class="post-card-category" href="./bytebytego-아티클/">🏷 ByteByteGo 아티클</a>
  </p>
  <div class="post-card-prologue">
    <h3>Prologue</h3>
    <ul class="post-card-bullets"><li>AI 에이전트는 어떻게 세션을 넘어 &quot;기억&quot;하는가?</li><li>모델의 무상태성부터 검색까지, 메모리 아키텍처 전반</li></ul>
  </div>
  <p class="post-card-readall"><a href="./bytebytego-아티클/9.-bytebytego--ai-에이전트는-어떻게-기억을-관리하고-망각을-피하는가">📖 Read All →</a></p>
</article>

<article class="post-card">
  <h2 class="post-card-title"><a href="./studygroup-프로젝트/선착순-마감-구현">[studygroup] 선착순 마감 구현</a></h2>
  <p class="post-card-meta">
    <span class="post-card-date">2026-07-03</span>
    <span class="post-card-author">작성자 djlim00</span>
    <a class="post-card-category" href="./studygroup-프로젝트/">🏷 StudyGroup 프로젝트</a>
  </p>
  <div class="post-card-prologue">
    <h3>Prologue</h3>
    <ul class="post-card-bullets"><li>Redis Lua 스크립트로 선착순 정원 마감 구현</li><li>동시성 검증과 놓치기 쉬운 것들</li></ul>
  </div>
  <p class="post-card-readall"><a href="./studygroup-프로젝트/선착순-마감-구현">📖 Read All →</a></p>
</article>

<article class="post-card">
  <h2 class="post-card-title"><a href="./studygroup-프로젝트/redis-session으로-로그인-만들기">[studygroup] 1. Redis Session으로 로그인 만들기</a></h2>
  <p class="post-card-meta">
    <span class="post-card-date">2026-07-03</span>
    <span class="post-card-author">작성자 djlim00</span>
    <a class="post-card-category" href="./studygroup-프로젝트/">🏷 StudyGroup 프로젝트</a>
  </p>
  <div class="post-card-prologue">
    <h3>Prologue</h3>
    <ul class="post-card-bullets"><li>Redis를 통한 로그인 구현</li><li>Redis 세션 사용시 설정 주의점</li></ul>
  </div>
  <p class="post-card-readall"><a href="./studygroup-프로젝트/redis-session으로-로그인-만들기">📖 Read All →</a></p>
</article>

<article class="post-card">
  <h2 class="post-card-title"><a href="./카프카/5.-apache-kafka-클러스터를-운영하는-방법">[카프카] 5. Apache Kafka 클러스터를 운영하는 방법</a></h2>
  <p class="post-card-meta">
    <span class="post-card-date">2026-07-03</span>
    <span class="post-card-author">작성자 djlim00</span>
    <a class="post-card-category" href="./카프카/">🏷 카프카</a>
  </p>
  <div class="post-card-prologue">
    <h3>Prologue</h3>
    <ul class="post-card-bullets"><li>Apache Kafka를 운영? SaaS? 온프레미스?</li><li>SaaS를 썼을 때 어떤 점이 좋을까?</li></ul>
  </div>
  <p class="post-card-readall"><a href="./카프카/5.-apache-kafka-클러스터를-운영하는-방법">📖 Read All →</a></p>
</article>

<article class="post-card">
  <h2 class="post-card-title"><a href="./카프카/4.-카프카---토픽,-파티션,-레코드">[카프카] 4. 토픽, 파티션, 레코드</a></h2>
  <p class="post-card-meta">
    <span class="post-card-date">2026-07-02</span>
    <span class="post-card-author">작성자 djlim00</span>
    <a class="post-card-category" href="./카프카/">🏷 카프카</a>
  </p>
  <div class="post-card-prologue">
    <h3>Prologue</h3>
    <ul class="post-card-bullets"><li>토픽/파티션/세그먼트/레코드는 어떤 구조일까?</li><li>레코드에는 어떤 값들이 있을까?</li></ul>
  </div>
  <p class="post-card-readall"><a href="./카프카/4.-카프카---토픽,-파티션,-레코드">📖 Read All →</a></p>
</article>

</div>

