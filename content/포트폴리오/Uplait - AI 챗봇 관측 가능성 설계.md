---
title: "[포트폴리오] Uplait - AI 챗봇 관측 가능성 설계"
publish: true
created: 2026-08-28T13:29:32+09:00
modified: 2026-08-28T14:12:11+09:00
---
# Uplait | AI 챗봇 관측 가능성 및 알림 체계 구축

> Uplait의 챗봇 요청은 `Spring Boot → FastAPI(LangChain) → OpenAI API → pgvector`를 거칩니다.
>
> 응답이 느리거나 실패했을 때 기존에는 SSH로 접속해 로그를 따라가야 했고, 어느 구간이 병목인지 분리해 볼 수 없었습니다.

| 구분 | 내용 |
| --- | --- |
| 관측 | Prometheus·Grafana 기반 기술·도메인 지표 |
| 알림 | Alertmanager 연동 알림 콘솔 |
| POC | Prometheus HA와 장기 저장을 위한 Thanos 구성 |

기본 시스템 지표만으로는 이 문제를 설명할 수 없었습니다. 챗봇의 사용자 경험과 직접 연결되는 도메인 지표와 대응 흐름을 설계했고, Prometheus·Grafana 기반 수집과 Alertmanager 연동 알림 콘솔을 구성했습니다. Prometheus HA와 장기 저장을 위한 Thanos 구성은 로컬에서 POC했습니다.

## 1. 요청 구간별 지표

전체 응답 시간만으로는 원인을 구분하기 어렵습니다. 요청 체인의 각 구간을 timer와 counter로 나눠 보기로 했습니다.

| 관측 대상 | 핵심 지표 | 이 지표가 필요한 이유 |
| --- | --- | --- |
| Spring API | 요청 수, p95/p99, 5xx | 사용자가 경험한 최종 품질 확인 |
| Spring ↔ FastAPI | 호출 지연, timeout, 실패율 | 서비스 간 통신 문제 분리 |
| OpenAI API | 지연, 오류, 재시도 | 외부 모델 의존 구간 식별 |
| pgvector | 검색 지연, 결과 수 | 검색 병목과 빈 결과 탐지 |
| 재추천 파이프라인 | 재시도 수, 최종 실패, 이벤트 지연 | 기본 JVM 지표에 안 보이는 기능 실패 탐지 |
| 인프라 | CPU, memory, connection pool | 자원 포화와 애플리케이션 증상의 상관관계 확인 |

Prometheus가 Spring Actuator·Micrometer, FastAPI metrics, postgres-exporter의 시계열을 수집하도록 구성했습니다. Grafana에서는 한 요청의 흐름에 맞춰 지표를 함께 볼 수 있습니다. 알림은 CPU 같은 일반 지표의 순간값보다 오류율과 지연이 일정 시간 이어지는지를 기준으로 삼아, 일시적인 spike가 불필요한 알림으로 번지지 않게 했습니다.

## 2. 알림 운영 워크플로우

Alertmanager는 라우팅과 억제에는 적합하지만, 기본 화면만으로는 지난 알림의 처리 과정과 담당자 확인 여부를 관리하기 어려웠습니다. 그래서 Alertmanager webhook을 받는 사내 알림 콘솔을 별도 서비스로 분리했습니다.

```text
Prometheus → Alertmanager → 알림 콘솔 → Discord / 문자
                               ↓
                       이력 · Ack · 상태 변경
```

콘솔은 fingerprint가 같은 알림을 묶고 최초 발생·반복·해소 시각과 Ack 담당자를 기록합니다. 다음 날에도 야간 장애의 흐름과 재발 여부를 확인할 수 있습니다. Alertmanager를 다시 만드는 대신 운영 이력과 국내 알림 채널처럼 부족했던 부분만 보완했습니다.

## 3. Prometheus 고가용성 POC

Prometheus 단일 인스턴스는 장애 순간의 지표를 함께 잃는 단일 장애점입니다. 긴 range query가 서비스 서버의 CPU와 메모리를 점유하면, 원인을 확인하려는 쿼리 자체가 복구를 더 어렵게 만들 수도 있습니다.

로컬 Docker Compose 환경에서 다음 Thanos 구조를 POC했습니다.

- Prometheus 두 인스턴스로 동일 타깃 수집
- Sidecar를 통해 오브젝트 스토리지에 block 업로드
- Query가 두 Prometheus와 Store Gateway의 데이터를 하나의 화면으로 조회
- Compactor가 장기 block을 압축·보존

이 구조에서는 장기 조회가 운영 Prometheus 한 대에 몰리지 않습니다. 수집기 하나가 중단돼도 다른 replica의 시계열을 조회할 수 있습니다. 다만 소규모 서비스에서는 운영 복잡도가 더 큰 비용이 될 수 있어, 실제 도입 여부는 보존 기간과 장애 비용, 팀의 운영 역량을 함께 보고 결정해야 합니다.

## 결과와 배운 점

이번 작업에서 대시보드의 개수는 중요하지 않았습니다. “챗봇이 느리다”는 증상을 Spring, FastAPI, 외부 API, 벡터 검색 중 어디가 느린지 답할 수 있는 문제로 바꾼 것이 핵심입니다.

알림은 메시지를 보내는 데서 끝나지 않습니다. 누가 확인했고 언제 해소됐는지, 같은 문제가 다시 발생했는지를 남겨야 다음 대응이 빨라집니다. 실제 배포 전에는 대표 장애를 주입해 알림 발생부터 Ack·해소까지의 흐름과 Thanos의 중복 제거를 검증해야 합니다.

---

**이전 페이지** [[백엔드 포트폴리오]]
