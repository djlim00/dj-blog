---
title: "[포트폴리오] StudyGroup - Redis 세션 고가용성 개선"
publish: true
created: 2026-08-28T13:29:32+09:00
modified: 2026-08-28T14:12:11+09:00
cover: pasted-image-20260817200812.png
---

# StudyGroup | Redis 세션 고가용성 아키텍처 개선

> StudyGroup은 스터디 개설과 선착순 신청을 제공하는 서비스입니다.
>
> 저는 스터디 비즈니스 로직, Spring Session 기반 로그인, 인프라와 배포를 담당했습니다.

| 구분 | 내용 |
| --- | --- |
| 문제 | Redis 재기동 중 인증 API 실패와 세션 유실 |
| 개선 | Redis Sentinel, HAProxy, Predictive Failover |
| 검증 | 100ms 간격 PING과 Sentinel 이벤트 비교 |

처음에는 Redis 한 대에 세션을 저장했습니다. Redis가 중단되면 인증이 필요한 API가 500을 반환했고, 재기동 후에는 메모리의 세션이 사라져 모든 사용자가 다시 로그인해야 했습니다. 그래서 고가용성의 목표를 단순히 “Redis가 다시 살아난다”가 아니라, 장애와 배포가 사용자 요청에 드러나는 시간을 줄이는 것으로 정했습니다.
![[Pasted image 20260817200812.png]]
## 1. Redis Sentinel

`Master 1 + Replica 2 + Sentinel 3`으로 구성했습니다. Replica가 세션 데이터를 복제하고, Sentinel quorum이 Master 장애를 판단하면 Replica 하나를 새 Master로 승격합니다.

```text
                 Sentinel × 3
                       ↓ 감시
애플리케이션 → Master Redis → Replica × 2
```

단일 Redis 장애로 세션 데이터가 모두 사라지는 문제는 여기서 해결했습니다. 다만 Master가 바뀐 뒤 클라이언트가 기존 연결을 끊고 새 주소를 찾는 동안, 테스트 환경에서 8~15초의 실패 구간이 남았습니다.


## 2. HAProxy

애플리케이션과 Redis 사이에 HAProxy를 두고, 애플리케이션은 고정된 endpoint만 사용하도록 했습니다. HAProxy health check는 `INFO replication` 결과가 `role:master`인 노드에만 쓰기 트래픽을 전달합니다.

```text
애플리케이션 → HAProxy(localhost:6390) → 현재 Master
                         ↑
                 Redis role health check
```

Master 주소 변경은 프록시가 처리하고, 애플리케이션은 Redis 토폴로지를 캐시하지 않게 했습니다. 강제 종료 실험에서는 Sentinel의 감지와 승격을 기다려야 하지만, 새 Master가 정해지면 HAProxy가 health check 주기 안에 경로를 바꿉니다.

## 3. Predictive Failover

배포·버전 업그레이드처럼 종료 시점을 아는 상황에서도 Redis를 먼저 내리면 Sentinel의 장애 감지 시간을 그대로 기다려야 합니다. 종료 hook에서 현재 노드가 Master인지 확인한 뒤 Sentinel에 failover를 먼저 요청하도록 순서를 바꿨습니다.

```text
기존: Master 종료 → 장애 감지 → Replica 승격 → 연결 전환
개선: Replica 승격 → 연결 전환 확인 → 기존 Master 종료
```

pre-stop은 전환 성공을 확인한 경우에만 종료를 이어갑니다. timeout이 발생하거나 Replica가 없으면 실패를 기록합니다. 계획된 종료와 갑작스러운 장애를 같은 방식으로 다루지 않은 것이 핵심입니다.

![[Pasted image 20260817200839.png]]

## 검증 결과

100ms 간격으로 HAProxy에 `PING`을 보내고, Sentinel의 `sdown`, `odown`, `switch-master` 이벤트와 함께 비교했습니다.

| 시나리오 | 전환 흐름 | 테스트 환경의 관측 결과 |
| --- | --- | --- |
| Sentinel discovery만 사용 | 장애 감지 후 클라이언트 재탐색 | 8~15초 실패 구간 |
| 강제 종료 + HAProxy | `sdown → switch-master` | 약 6초 |
| 계획 종료 + Predictive Failover | `try-failover → switch-master → stop` | PING 실패 관측 없음 |

“0초”는 모든 환경에서의 절대 보장이 아니라 이 실험의 100ms 측정 간격에서 실패가 관측되지 않았다는 뜻입니다. 네트워크 분할, quorum 상실, 복제 지연은 별도 장애 시나리오로 검증해야 합니다.

## 배운 점

Sentinel만 도입한다고 사용자 관점의 고가용성이 완성되지는 않았습니다. 장애 감지와 승격, 클라이언트 경로 전환을 따로 측정해야 실제 실패 시간을 줄일 수 있었습니다.

계획된 변경이라면 실패를 기다렸다 복구할 이유가 없습니다. 트래픽을 먼저 안전한 곳으로 옮긴 뒤 종료하면 됩니다. 이 순서는 Redis뿐 아니라 롤링 배포와 상태 저장 컴포넌트 교체에도 적용할 수 있습니다.

---

**이전 페이지** [[백엔드 포트폴리오]]
