---
title: "[studygroup] 고가용성을 위한 개선들"
publish: true
created: 2026-08-05T19:52:42+09:00
modified: 2026-08-05T20:36:42+09:00
---
## Prologue

이 글은 "이 프로젝트가 뭐 하는 서비스냐"가 아니라, **Redis를 쓰는 서비스에서 어떻게 고가용성(HA)을 확보했는가**만 이야기합니다.

세 단계로 나눠서 왔습니다.

1. **Redis Sentinel** — Redis 하나가 죽어도 서비스가 살아남는 구조
2. **HAProxy sidecar** — Sentinel만으로는 앱이 여전히 몇 초 멈추는 문제 해결
3. **Predictive Failover** — 배포와 같이 계획된 재시작 시엔 다운타임 없게 하자..

---

## Part 1. 처음: Redis 하나

```
   앱 ──── Redis 하나 (6379)
```

- <mark class="hltr-yellow">Redis 하나가 죽으면 → 앱 전체 다운</mark>
- 세션이 다 Redis에 있으니 → 사용자가 전부 로그아웃
- 재시작해도 세션 데이터 다 사라짐(메모리)

---

## Part 2. Redis Sentinel 도입

Redis를 **1대 → 3대(master 1 + replica 2)** 로 늘리고, 감시자 역할의 **Sentinel 3대**를 추가했습니다.

```
  앱
   ↓ "지금 master 누구?"
  Sentinel 3대  ─────감시──▶  master(6379)
                                  ↓ 복제
                              replica 1 (6380)
                              replica 2 (6381)
```

Sentinel 3대가 master를 감시하다가 **master가 죽으면 replica 중 하나를 새 master로 자동 승격**(페일오버)

- **해결**: master 죽어도 replica가 자동 승격 → 서비스 계속됨
- **결과**: **"단일 장애점(SPOF)"** 제거

### 실측

- `docker kill sg-redis-master` 로 강제 종료
- 5~10초 안에 replica 하나가 새 master로 승격
- 세션 데이터도 replica에 복제돼 있어서 **로그인 유지됨**


<mark class="hltr-yellow">**하지만 여전히 페일오버가 진행되는 5~10초 동안 사용자는 500 에러를 봄**</mark>

앱 관점에서 자세히 보면:

1. 앱이 "master는 6379" 라고 캐싱하고 있음
2. master 죽음 → 앱은 계속 6379로 요청 시도 → 계속 실패
3. Redis 클라이언트가 "어? 계속 실패하네" 하고 Sentinel에 다시 물어봄
4. 새 master 주소 받고 재연결

**4번까지 총 8~15초**. 그동안 사용자는 로그인 안 되고, 신청도 안 되고, 500 에러만 뜹니다.

이 문제를 해결하기 위해서 HAProxy계층을 추가했습니다.

---

## Part 3.  HAProxy sidecar 도입

우선 앱과 Redis 사이에 프록시 계층을 하나 추가.


```
  앱 ──"localhost:6390 이 주소만 알면 돼"──▶  HAProxy
                                                ↓ 매초 role check
                                              master (지금은 6379)
                                              replica-1 (6380)
                                              replica-2 (6381)
```

HAProxy가 매초 각 Redis 노드에 `INFO replication` 명령을 날려서 **"role:master" 응답이 오는 놈**에만 트래픽을 보냄.

### 개선
- **문제**: 앱이 "지금 master-replica 구조"를 알아야 해서, 지도가 바뀌면 앱이 헷갈림 → 5~10초 다운타임
- **해결**: <mark class="hltr-yellow">HAProxy가 topology를 대신 알고 있음. 앱은 `localhost:6390` 하나만 봄. master가 누구든 앱은 몰라도 됨.</mark>
- **결과**: **RTO 8~15초 → 1~3초**

**개선된 시나리오**:
- master(6379) 죽음
- HAProxy가 다음 초 check에서 "PING 응답 없음" → DOWN 처리
- Sentinel이 replica-1을 승격 → replica-1이 이제 role:master 응답
- HAProxy가 다음 초 check에서 replica-1을 UP 처리 → 즉시 트래픽 전환

**앱은 그냥 계속 `localhost:6390`으로 요청 던지면 HAProxy가 알아서 처리.**

#### 아이디어 출처

**Facebook mcrouter** 라는 memcached 프록시가 원조. 페이스북/인스타그램이 캐시 서버 수천 대를 이 방식으로 관리함.
- 각 앱 서버마다 mcrouter 프로세스를 **sidecar(같은 머신에서 함께 실행)** 로 둠
- 앱은 `localhost` 로만 붙고, mcrouter가 뒤에서 sharding·failover 다 처리
- 우리는 프로토콜만 다름(memcached → Redis). 구조는 동일. HAProxy가 mcrouter 역할.


#### 여전히 개선사항이 있음!!

<mark class="hltr-yellow">**계획된 종료(배포, 재시작)에도 여전히 1~3초 다운타임이 생김**</mark>

실제 운영 시에 페일오버가 왜 일어나는 이유를 보면
- 90% 이상이 **planned** — 배포, 서버 교체, 스팟 인스턴스 회수, 재시작
- 10% 미만이 **unplanned** — 하드웨어 fault, OOM 등

**예측할 수 있는 배포 상황에에서 1~3초 다운타임이 생기는건 너무 손해**라고 생각했습니다. 어차피 내가 계획해서 죽이는 건데, 왜 감지 대기를 해야 하나..?

---

## Part 4. 3단계 - Predictive Failover 도입

master 컨테이너가 **죽기 전에**, 스스로 sentinel에 "지금 failover 시켜" 요청하는 스크립트를 넣으면,,

```
  docker stop sg-redis-master
     ↓ SIGTERM
  master 컨테이너의 preStop 스크립트 실행
     ↓
  "나 master니까 sentinel에 failover 요청할게"
     ↓
  sentinel: "OK, replica-1을 승격"
     ↓
  master는 자기가 slave로 확정된 뒤에 종료
```

이러면 **죽는 순간 이미 replica가 되어 있음*  ->  Sentinel이 "master 죽음"을 감지하고 해야할 이유가 없음

- **문제**: 계획된 종료(배포)에도 sentinel이 "master 죽음" 감지하는 5초 대기가 발생
- **해결**: <mark class="hltr-yellow">죽기 전에 스스로 미리 페일오버 시켜서 감지 대기 자체를 없앰</mark>
- **결과**: **planned 종료 시 다운타임 거의 없음 (0~1초)**


#### 아이디어 출처

**Kubernetes의 Redis Operator들** 이 pod 종료 시 사용하는 표준 방식.
- [spotahome/redis-operator](https://github.com/spotahome/redis-operator)
- Redis Enterprise 공식 오퍼레이터


---

## Part 5. 도입 효과

| 시나리오                  | 이전 (Sentinel만) | +HAProxy | +HAProxy +Predictive |
| --------------------- | -------------- | -------- | -------------------- |
| 강제 종료 (`docker kill`) | 8~15초          | **1~3초** | 1~3초                 |
| 계획 종료 (`docker stop`) | 8~15초          | 1~3초     | **관측 불가**            |

- 아키텍처 개선(HAProxy, preStop)을 통해서 "페일오버 시간 자체를 줄이는 것이 아니라, 페일오버 이벤트를 사용자가 볼 수 없게 한다!"

---

## Part 6.  생각해볼만한 점들

### 1. HAProxy 자체가 SPOF 아닌가?

로컬 실습에서는 HAProxy 하나만 뜸. 이게 죽으면 앱 전체 다운.

**두 가지 완화**:
- **sidecar 배포**: 앱 인스턴스가 여러 대라면 각각에 HAProxy 하나씩 → 자연스럽게 이중화됨. Facebook mcrouter가 이 방식.
- **keepalived + HAProxy 2대**: 프로덕션 방식. VIP를 두 HAProxy가 공유. 하나 죽으면 자동 인계.

### 2. AWS에서는 어떻게 해야 하나?

**AWS ElastiCache**가 위의 문제를 그냥 해결해버림
- Configuration Endpoint(고정 주소) 제공해주고
- 뒤에서 master가 바뀌어도 AWS가 알아서 라우팅해줌
- 앱은 항상 같은 endpoint 하나만 보면 됨

### 3. 더 발전할 수 있는 부분들
- **Redis Cluster로 확장** — 여러 마스터를 샤딩해보기.
- **Circuit Breaker (Resilience4j)** — 극단적 상황(HAProxy까지 죽음)에서도 앱이 캐스케이드로 다운되지 않게 방어하는 로직을 추가해보기.
