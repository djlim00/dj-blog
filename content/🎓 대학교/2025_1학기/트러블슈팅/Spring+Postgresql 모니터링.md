https://steady-coding.tistory.com/643
https://velog.io/@sdsd0908/%EC%8A%A4%ED%94%84%EB%A7%81-%EB%B0%98%EA%B2%BD-%EA%B2%80%EC%83%89-%EA%B8%B0%EB%8A%A5-DB-%EB%B3%80%EA%B2%BD%EC%97%90-%EB%8C%80%ED%95%9C-%EA%B3%A0%EB%AF%BC


```
                🌐 인터넷
                   │
           ┌───────▼────────────┐
           │  EC2 (퍼블릭 서브넷) │
           │                    │
           │  🟦 Spring Boot 앱   │
           │   - port 8080      │
           │   - actuator       │
           │   - /actuator/prometheus
           │                    │
           │  🐳 Docker Compose  │
           │   ┌────────────┐
           │   │ Prometheus │◀──────────────┐
           │   └────────────┘               │
           │   ┌──────────┐                 │
           │   │ Grafana  │                 │
           │   └──────────┘                 │
           │   ┌─────────────────────────┐  │
           │   │ postgres_exporter       │──┘
           │   └─────────────────────────┘
           └────────────┬───────────────┘
                        │
         ┌──────────────▼───────────────┐
         │  RDS PostgreSQL (프라이빗 서브넷) │
         │  - port 5432                 │
         │  - metrics 수집 대상         │
         └─────────────────────────────┘
```



## 1. `build.gradle` (Spring 측)

### ✍️ 추가된 내용

groovy

복사편집

`implementation("org.springframework.boot:spring-boot-starter-actuator") implementation("io.micrometer:micrometer-registry-prometheus")`

### 🧠 역할 설명

|구성 요소|설명|
|---|---|
|`actuator`|Spring Boot의 헬스 체크, 메트릭, 쓰레드, 힙 메모리 등 상태를 확인하는 엔드포인트 제공|
|`micrometer-registry-prometheus`|Micrometer 메트릭을 Prometheus가 읽을 수 있는 포맷으로 노출함|

> 결과적으로 `/actuator/prometheus` 경로에서 Prometheus가 메트릭을 `pull` 가능해집니다.

---

## ✅ 2. `docker-compose.monitoring.yml`

yaml

복사편집

`version: '3.7'  services:   prometheus:     image: prom/prometheus     container_name: prometheus     ports:       - "9090:9090"     volumes:       - ./prometheus.yml:/etc/prometheus/prometheus.yml     networks:       - monitor-net    grafana:     image: grafana/grafana     container_name: grafana     ports:       - "3000:3000"     depends_on:       - prometheus     networks:       - monitor-net    postgres-exporter:     image: wrouesnel/postgres_exporter     container_name: postgres-exporter     ports:       - "9187:9187"     env_file:       - .env     environment:       - DATA_SOURCE_NAME=postgresql://${SPRING_DATASOURCE_USERNAME}:${SPRING_DATASOURCE_PASSWORD}@${SPRING_DATASOURCE_URL#jdbc:postgresql://}?sslmode=disable     networks:       - monitor-net  networks:   monitor-net:     driver: bridge`

### 🧠 역할 설명

|서비스|설명|
|---|---|
|**prometheus**|Spring 및 PostgreSQL exporter로부터 메트릭을 수집하는 서버|
|**grafana**|Prometheus의 메트릭을 대시보드로 시각화하는 UI 도구|
|**postgres-exporter**|RDS PostgreSQL의 내부 상태를 Prometheus 포맷으로 노출하는 exporter|
|**env_file**|`.env`로부터 DB 접근 정보 읽음|
|**networks**|세 컨테이너 간 통신을 위한 브릿지 네트워크 구성|

---

## ✅ 3. `prometheus.yml`

yaml

복사편집

`global:   scrape_interval: 15s  scrape_configs:   - job_name: 'spring'     metrics_path: '/actuator/prometheus'     static_configs:       - targets: ['172.17.0.1:8080']  # Docker에서 EC2 Spring 앱 접근    - job_name: 'pgexporter'     static_configs:       - targets: ['localhost:9187']  # 같은 Docker 네트워크 내 exporter`

### 🧠 역할 설명

|항목|설명|
|---|---|
|`scrape_interval`|메트릭 수집 주기 (15초마다)|
|`job_name: spring`|Spring 애플리케이션 메트릭 수집 설정|
|`metrics_path`|Actuator가 노출하는 메트릭 경로|
|`targets`|Prometheus가 수집할 엔드포인트 주소|
|`job_name: pgexporter`|PostgreSQL 메트릭을 수집하는 exporter 등록|

---

## ✅ 4. `application.yml`

yaml

복사편집

`management:   endpoints:     web:       exposure:         include: prometheus   metrics:     tags:       application: uhyu-server`

### 🧠 역할 설명

|설정|설명|
|---|---|
|`endpoints.web.exposure.include`|`/actuator/prometheus` 엔드포인트를 외부로 노출|
|`metrics.tags.application`|모든 메트릭에 `application=uhyu-server` 태그를 붙여 식별 가능하게 함 (Grafana에서 필터 용이)|

---

## ✅ 전체 흐름 요약

plaintext

복사편집

`[Spring Boot App (EC2)] → exposes /actuator/prometheus  [postgres_exporter] → exposes PostgreSQL 메트릭 at :9187  → [Prometheus] → 주기적으로 둘의 메트릭을 scrape  → [Grafana] → Prometheus 데이터를 시각화`










# Docker 띄우고 권한 없어서 컨테이너 안뜨는 문제 권한 주기
## 해결 방법: 권한 변경

Grafana 컨테이너는 내부적으로 UID/GID `472`을 사용하는데, 이 사용자에게 해당 디렉토리의 권한을 줘야 합니다.

### 1. 호스트에서 권한 수정

bash

복사편집

`sudo chown -R 472:472 ./data/grafana`

혹시 `data` 디렉토리를 통째로 바꿔도 된다면:

bash

복사편집

`sudo chown -R 472:472 ./data`

---

### 2. 컨테이너 재시작

bash

복사편집

`docker-compose -f docker-compose.monitoring.yml down docker-compose -f docker-compose.monitoring.yml up -d`



좋습니다. 이 오류는 Prometheus가 내부에서 쿼리 로그 파일을 쓰려고 할 때 **`/prometheus/queries.active` 경로에 쓸 수 있는 권한이 없기 때문에** 발생합니다.

즉, 지금 이 볼륨 마운트 때문에 문제가 생긴 거예요:

yaml

복사편집

`volumes:   - ./data/prometheus:/prometheus`

이때 `./data/prometheus`는 **호스트(Ubuntu EC2)의 로컬 디렉토리**인데, Prometheus 컨테이너에서 해당 디렉토리에 **쓰기 권한이 없어서** 오류가 나고 있는 거예요.

---

## ✅ 해결 방법

### 🔧 방법 1: `chown`으로 권한 수정 (추천)

1. 호스트 EC2(Ubuntu)에서 아래 명령어 실행:
    

bash

복사편집

`sudo chown -R 65534:65534 ./data/prometheus`

- `65534`는 Prometheus 컨테이너 내부에서 쓰는 nobody 사용자의 UID/GID입니다.
    
- 또는 root 권한으로도 가능하지만 보안상 이게 더 안전합니다.



curl -kso /dev/null -w "\n===============\n\
| DNS lookup: %{time_namelookup}\n\
| Connect: %{time_connect}\n\
| App connect: %{time_appconnect}\n\
| Pre-transfer: %{time_pretransfer}\n\
| Start transfer: %{time_starttransfer}\n\
| Total: %{time_total}\n\
| HTTP Code: %{http_code}\n===============\n" "https://api.u-hyu.site/map/stores?lat=37.52345387780352&lon=126.95886774592051&radius=2000"