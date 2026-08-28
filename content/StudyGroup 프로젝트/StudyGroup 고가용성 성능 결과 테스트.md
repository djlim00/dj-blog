---
title: 무제
publish: false
created: 2026-08-17T15:16:35+09:00
modified: 2026-08-17T17:28:36+09:00
---
# 1. 배포 상황(예정된 master 재시작)

#### Sentinel 이벤트 로그
```
djlim00@DJs-MacBook-Pro studygroup % docker logs sg-sentinel-1 2>&1 | grep -E "try-failover|switch-master|sdown|odown" | tail -5

1:X 17 Aug 2026 06:18:26.817 # +try-failover master mymaster host.docker.internal 6379

1:X 17 Aug 2026 06:18:32.786 # +sdown master mymaster host.docker.internal 6379

1:X 17 Aug 2026 06:18:33.202 # +switch-master mymaster host.docker.internal 6379 host.docker.internal 6380

1:X 17 Aug 2026 06:18:38.247 # +sdown slave host.docker.internal:6379 host.docker.internal 6379 @ mymaster host.docker.internal 6380
```

#### 
```
djlim00@DJs-MacBook-Pro studygroup % docker logs sg-redis-master 2>&1 | grep '\[prestop\]'

[prestop] redis-server started, pid=8

[prestop] SIGTERM received, current role=master, my announce-port=6379

[prestop] planned shutdown of master → predictive failover

[prestop] failover requested via sentinel-1: OK

[prestop] sentinel now reports new master on port=6380 (was 6379)

[prestop] propagating SIGTERM to redis-server 
pid=8
```

#### 실패 개수 - 단 한번
```
djlim00@DJs-MacBook-Pro studygroup % echo "FAIL 개수: $(grep -c FAIL /tmp/ha-predictive.log)"
grep FAIL /tmp/ha-predictive.log
FAIL 개수: 1
15:18:27 FAIL Error: Server closed the connection
```

#### 새로운 마스터 확인
```
djlim00@DJs-MacBook-Pro studygroup % docker exec sg-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
host.docker.internal
6380
```


#### 
  🔴 이유 1: "왜 Lettuce인가?" 답할 수 있어야 함

  면접에서 "왜 Jedis 안 쓰고 Lettuce 썼어요?" 물어봤을 때, "Spring Boot 기본이라서요"는 감점. "Netty 기반 non-blocking으로 커넥션 하나에 요청 다중화가 돼서 리소스 효율이 좋고, Sentinel/Cluster의 topology refresh 지원이 성숙해서요" — 이런 대답이 되려면 3개를 비교해봐야 함.

  🔴 이유 2: Redisson의 분산 락은 면접 단골

  "MSA에서 재고 차감을 여러 서버가 동시에 하는데 어떻게 정합성 지키죠?"
  → 답: "Redis 기반 분산 락 (Redlock)". 대부분 Redisson으로 구현.

  지금 우리 선착순은 Lua 스크립트로 원자성을 확보하는 방식. 이건 카운터 스타일. 락 기반 방식(Redisson RLock)으로도 같은 문제를 풀 수 있고,
  두 방식의 트레이드오프를 설명할 수 있어야 이력서에 두께가 생김.   

____
# 2. 서버가 다운된 경우

#### Sentinel 이벤트 로그
```
djlim00@DJs-MacBook-Pro studygroup % docker logs sg-sentinel-1 2>&1 | grep -E "sdown|odown|switch-master" | tail -10

1:X 17 Aug 2026 06:48:11.076 # +sdown master mymaster host.docker.internal 6380

1:X 17 Aug 2026 06:48:11.177 # +odown master mymaster host.docker.internal 6380 #quorum 2/2

1:X 17 Aug 2026 06:48:12.266 # +switch-master mymaster host.docker.internal 6380 host.docker.internal 6381

1:X 17 Aug 2026 06:48:17.300 # +sdown slave host.docker.internal:6380 host.docker.internal 6380 @ mymaster host.docker.internal 6381
```

#### HAProxy 상태
```
djlim00@DJs-MacBook-Pro studygroup % curl -s 'http://localhost:8404/;csv' | awk -F, '$1=="redis_master_back" && $2!="BACKEND" {printf "%-10s %s\n", $2, $18}'
node1      DOWN
node2      DOWN
node3      UP
```

####  다운타임
```
djlim00@DJs-MacBook-Pro studygroup % echo "FAIL 개수: $(grep -c FAIL /tmp/ha-kill.log)"
grep FAIL /tmp/ha-kill.log | head -5
FAIL 개수: 1
15:48:06 FAIL Error: Server closed the connection
```


### 로그를 보면 결론적으로..
- `15:48:06 FAIL Error: Server closed the connection` 이때 내가 kill 명령어를 통해서 master를 죽임
- `2026 06:48:11.076 # +sdown master mymaster host.docker.internal 6380`  이걸 보면 6초 ~ 11초 즉 5000ms(5초)동안 masterㄷ가 응답이 없다고 판단함
- `2026 06:48:11.177 # +odown master mymaster host.docker.internal 6380 #quorum 2/2` 다른 sentinel 2개가 master가 죽었다는 것에 동의 -> DOWN이 확정
- `06:48:12.266 # +switch-master mymaster host.docker.internal 6380 host.docker.internal 6381` 기존의 master인 6380에서 새로운 master인 6381로 switch
- HAProxy에서 node3(6381)이 UP(master)
- 6초 ~ 12초 정도 즉 6~7초만에 트래픽이 정상적으로 재개됨.

## 주요성과 
### 쿼리 성능 77% 개선
- 매일 배치 작업을 진행하는 CRON 서버에서 병목 발생
- AWS 성능 개선 도우미를 확인한 결과 특정 쿼리의 평균 지연 시간이 4.9초 • 쿼리 실행 계획을 확인한 결과 배치 작업에서 30개 레코드 조회할 때마다 조건 테이블의 9,000,000개 데이터를 Sequential Scan
- NOT IN 방식을 LEFT JOIN 방식으로 변경 후, Index Only Scan 방식 도입
- 결과적으로 배치당 평균 조회시간을 1,615.21ms에서 368.1ms로 개선
- 이 과정을 통해 MySQL과 PostgreSQL의 인덱스 구조와 쿼리 실행 계획에 대해서 학습하였음

## 학과 온라인 선거 시스템 재구축 프로젝트 •
### ▼ 어려웠던 점
- 선거 종류(단선, 경선)에 따라 선거 로직이 달라야 함
- API URI를 두 개로 만드는 것을 고려했으나, 클라이언트에서 선거 종류를 알고 있어야 하는 방식의 문제와 Open-Closed Principle 측면에서 고민
- 전략 패턴 사용을 고려했으나, 변경돼야하는 선거 로직의 범위가 너무 컸고 각 전략 역시 선거에 맞게 선택해줘야했음 
- VotingService 인터페이스를 설계하고 선거 타입 검증 책임 위임
- 각 선거 룰에 따라 VotingService를 구현
- Spring IoC 컨테이너의 도움을 받아 모든 투표 서비스 컴포넌트 주입
- 선거 타입에 맞는 VotingService 사용