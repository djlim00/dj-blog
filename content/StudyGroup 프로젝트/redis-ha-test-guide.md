---
created: 2026-08-17T15:08:30+09:00
modified: 2026-08-17T15:08:30+09:00
---

# Redis HA 페일오버 직접 테스트 가이드

이 가이드대로 따라 하면 **Redis 마스터가 죽을 때 서비스가 몇 초 멈추는지**를 3가지 구성별로 직접 눈으로 확인할 수 있다.

**결론 미리**: 아래 표의 숫자를 직접 재현하는 것이 목표다.

| 구성 | 서버가 죽을 때 사용자가 겪는 다운타임 |
|---|---|
| A. Sentinel만 (기본) | 8~15초 |
| B. Sentinel + HAProxy | 1~3초 |
| C. Sentinel + HAProxy + Predictive Failover | **0초 (관측 불가)** — 배포 시나리오 한정 |

소요 시간: 전체 15~20분. 명령어만 복붙하면 된다.

---

## 0. 이 실험이 뭘 증명하는가 (2분 읽기)

### 등장인물

- **Redis 마스터**: 데이터의 진짜 주인. 이 놈이 죽으면 서비스 다운.
- **Redis 레플리카 2대**: 마스터를 복제해 놓은 놈들. 마스터가 죽으면 이 중 하나가 승격돼야 함.
- **Sentinel 3대**: "마스터 살아있냐?" 감시자. 죽었다고 판단하면 레플리카를 승격시킴.
- **HAProxy**: 우리가 새로 도입하는 프록시. 앱과 Redis 사이에 낀다.
- **앱**: 여기서는 실제 앱 대신 `redis-cli PING`을 100ms 마다 던지는 스크립트로 대체. 다운타임이 몇 초인지 세는 용도.

### 왜 HAProxy를 끼우나

Sentinel만 쓰면 앱이 "지금 마스터 누구야?"를 Sentinel한테 직접 물어봐야 한다. 마스터가 바뀌면 앱이 옛 주소로 계속 시도하다가 실패하고 → Sentinel에 재조회 → 새 주소로 재접속. 이 과정이 **8~15초**.

HAProxy를 앱과 Redis 사이에 끼우면, 앱은 항상 HAProxy 주소(`localhost:6390`)만 보고, HAProxy가 매초 "지금 role:master인 놈이 누구야?"를 검사해서 알아서 라우팅한다. 앱은 마스터가 바뀐 걸 몰라도 됨. → 다운타임 **1~3초**.

### 왜 Predictive Failover까지 하나

배포·재시작 같은 **계획된 종료**는 우리가 언제 죽일지 미리 안다. 이걸 sentinel한테 "5초 뒤에 감지해서 승격시켜"라고 시키지 말고, **죽기 직전에 우리가 먼저 sentinel한테 "지금 승격 시켜"라고 요청**하면 감지 대기 자체가 사라진다. → 다운타임 **0초**.

---

## 1. 준비 (5분)

### 1-1. 필요한 것 확인

- Docker Desktop이 켜져 있어야 함
- 프로젝트 폴더로 이동
  ```bash
  cd ~/Desktop/GIt/studygroup
  ```

### 1-2. 포트 충돌 정리 🔴 필수

이 실습은 6379, 6380, 6381, 26379~26381, 5432, 6390, 8404 포트를 쓴다. 다른 프로젝트가 잡고 있으면 안 됨.

**가장 흔한 충돌**: `baton-*` 컨테이너가 6379(redis), 5432(postgres)를 잡고 있음.

```bash
# 뭐가 잡고 있는지 확인
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep -E "6379|5432"

# baton 이 잡고 있다면 잠깐 stop (실습 끝나면 다시 살릴 것)
docker stop baton-redis baton-postgres
```

### 1-3. HA 스택 띄우기

```bash
docker compose -f docker-compose.ha.yml up -d \
  redis-master redis-replica-1 redis-replica-2 \
  sentinel-1 sentinel-2 sentinel-3 \
  haproxy
```

10초 정도 기다리고 상태 확인.

```bash
sleep 10
docker ps --filter "name=sg-" --format "{{.Names}}: {{.Status}}"
```

**정상이면 이렇게 보임**:

```
sg-sentinel-1: Up 10 seconds
sg-sentinel-2: Up 10 seconds
sg-sentinel-3: Up 10 seconds
sg-haproxy:    Up 10 seconds
sg-redis-master:    Up 15 seconds (healthy)
sg-redis-replica-1: Up 12 seconds (healthy)
sg-redis-replica-2: Up 12 seconds (healthy)
```

컨테이너 7개가 다 떠 있어야 한다. `healthy`가 안 뜨면 20초 더 기다렸다가 다시 봐라.

### 1-4. 기본 동작 확인

**Sentinel이 마스터를 잘 보고 있나?**

```bash
docker exec sg-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
```

**정상 출력**:
```
host.docker.internal
6379
```
→ "마스터는 6379 포트에 있다"는 뜻. (6379는 초기 마스터인 `sg-redis-master`가 광고하는 포트)

**HAProxy가 마스터로 라우팅하나?**

```bash
docker exec sg-redis-master redis-cli -h haproxy -p 6390 INFO replication | grep -E "^role|connected_slaves"
```

**정상 출력**:
```
role:master
connected_slaves:2
```
→ HAProxy를 통해 요청을 보냈더니 `role:master`가 응답. HAProxy가 정확히 마스터로만 라우팅하고 있다는 뜻.

**HAProxy Stats 페이지도 열어봐라** (브라우저):

```
http://localhost:8404
```

`redis_master_back` 섹션에서 `master`는 UP(초록), `replica1`, `replica2`는 DOWN(빨강)으로 보여야 한다. HAProxy가 "role:master 응답하는 놈만 UP"으로 판정하기 때문에 정상이다.

---

## 2. 다운타임 측정 도구 만들기 🔴 필수

100ms 간격으로 HAProxy를 통해 PING을 던져서 성공/실패를 기록하는 스크립트다. FAIL 개수 × 100ms ≈ 다운타임.

```bash
cat > /tmp/ha-ping-loop.sh <<'EOF'
#!/bin/sh
# 사용법: /tmp/ha-ping-loop.sh <반복횟수>
set -u
COUNT=0
LIMIT="${1:-100}"
while [ "$COUNT" -lt "$LIMIT" ]; do
  ts=$(date '+%H:%M:%S')
  out=$(perl -e 'alarm 1; exec @ARGV' \
        docker exec sg-sentinel-1 redis-cli -h haproxy -p 6390 -t 1 PING 2>&1 | head -1)
  case "$out" in
    PONG) echo "$ts OK";;
    "")   echo "$ts FAIL (timeout)";;
    *)    echo "$ts FAIL $out";;
  esac
  COUNT=$((COUNT + 1))
  sleep 0.1
done
EOF
chmod +x /tmp/ha-ping-loop.sh
```

이 스크립트는 클라이언트로 `sg-sentinel-1` 컨테이너를 쓴다 (앱 대체 용도). Sentinel 컨테이너 안에 있는 `redis-cli`로 HAProxy를 두들긴다.

---

## 3. 시나리오 A: Predictive Failover (배포 시나리오)

### 3-1. 무슨 상황을 시뮬레이션하나

**실제 상황**: "새 버전 배포하려고 마스터 컨테이너를 재시작한다."
**Docker 명령어**: `docker stop sg-redis-master` (얌전한 종료 = SIGTERM)

Predictive Failover는 이 얌전한 종료에서만 작동한다. 우리가 만든 `redis-prestop.sh` 스크립트가 SIGTERM을 가로채서 sentinel한테 "지금 승격 시켜줘"라고 미리 요청한다.

### 3-2. 실행

```bash
# 백그라운드로 ping 루프 시작 (30초 = 300 iterations)
/tmp/ha-ping-loop.sh 300 > /tmp/ha-predictive.log 2>&1 &
PLOOP=$!

# 2초 뒤 마스터를 얌전히 stop
sleep 2
echo ">>> $(date '+%H:%M:%S') docker stop 실행"
time docker stop sg-redis-master
echo ">>> $(date '+%H:%M:%S') stop 완료"

# 페일오버 관측을 위해 10초 더 대기
sleep 10
kill $PLOOP 2>/dev/null
```

### 3-3. 결과 확인

**① `docker stop` 소요 시간**

`time docker stop` 결과가 1~2초여야 한다. (기본 10초 timeout까지 걸리면 prestop이 실패한 것)

**② prestop 스크립트 로그**

```bash
docker logs sg-redis-master 2>&1 | grep '\[prestop\]'
```

**성공하면 이렇게 보임**:
```
[prestop] redis-server started, pid=8
[prestop] SIGTERM received, current role=master, my announce-port=6379
[prestop] planned shutdown of master → predictive failover
[prestop] failover requested via sentinel-1: OK
[prestop] sentinel now reports new master on port=6380 (was 6379)
[prestop] propagating SIGTERM to redis-server pid=8
```

**핵심 라인**: `sentinel now reports new master on port=6380 (was 6379)` — 죽기 전에 sentinel이 이미 새 마스터를 확정했음.

**만약** `timeout waiting for sentinel to promote a new master` 라고 뜨면 프리딕티브가 실패한 것. 그 원인은 대개 replica 설정 문제 (아래 트러블슈팅 참고).

**③ Sentinel 이벤트 로그**

```bash
docker logs sg-sentinel-1 2>&1 | grep -E "try-failover|switch-master|sdown|odown" | tail -10
```

**성공하면 이렇게 보임**:
```
+try-failover master mymaster host.docker.internal 6379
+failover-end master mymaster host.docker.internal 6379
+switch-master mymaster host.docker.internal 6379 host.docker.internal 6380
```

**중요**: `+sdown`, `+odown`이 **없다**. 이게 Predictive의 증거다. 반응성(reactive) 페일오버는 항상 sdown → odown → switch 순서로 찍히는데, 이건 sentinel이 "죽음을 감지" 하는 단계 자체를 건너뛴 것이다.

**④ 다운타임 측정**

```bash
echo "FAIL 개수: $(grep -c FAIL /tmp/ha-predictive.log)"
grep FAIL /tmp/ha-predictive.log
```

**성공하면**: `FAIL 개수: 0` — 앱은 페일오버가 있었는지도 몰랐다.

**⑤ 새 마스터 확인**

```bash
docker exec sg-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
```

**출력**:
```
host.docker.internal
6380         ← 6379 에서 6380 (또는 6381) 로 바뀜
```

---

## 4. 시나리오 B: 강제 Kill (하드웨어 장애 시나리오)

### 4-1. 무슨 상황을 시뮬레이션하나

**실제 상황**: "서버 하드웨어가 갑자기 죽었다, 또는 OOM Killer가 프로세스를 죽였다."
**Docker 명령어**: `docker kill sg-redis-master` (SIGKILL = 즉사, prestop 실행 안 됨)

이 경우엔 Predictive가 못 작동한다. 오직 sentinel의 감지에 의존해야 하고, HAProxy가 새 마스터를 얼마나 빨리 찾아내는지가 관건이다.

### 4-2. 이전 stop 흔적 정리

방금 stop한 마스터는 이제 다른 컨테이너(6380 또는 6381)가 새 마스터다. 원래 상태로 복구.

```bash
# 옛 마스터 되살리기 (자동으로 slave 로 편입됨)
docker start sg-redis-master
sleep 10
docker exec sg-redis-master redis-cli info replication | grep -E "^role|master_port"
```

**출력**:
```
role:slave
master_port:6380
```
→ 옛 마스터가 자동으로 slave로 강등되어 새 마스터를 따라감. Sentinel이 알아서 해줌.

### 4-3. 현재 마스터 컨테이너 이름 알아내기

```bash
CURR_PORT=$(docker exec sg-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster | sed -n '2p')
case "$CURR_PORT" in
  6379) TARGET=sg-redis-master;;
  6380) TARGET=sg-redis-replica-1;;
  6381) TARGET=sg-redis-replica-2;;
esac
echo "현재 마스터 = $TARGET (port $CURR_PORT)"
```

### 4-4. 실행

```bash
/tmp/ha-ping-loop.sh 300 > /tmp/ha-kill.log 2>&1 &
PLOOP=$!

sleep 2
echo ">>> $(date '+%H:%M:%S') docker kill $TARGET"
docker kill "$TARGET"

# 페일오버까지 10초 대기 (down-after 5s + switch 시간)
sleep 15
kill $PLOOP 2>/dev/null
```

### 4-5. 결과 확인

**① Sentinel 이벤트 로그**

```bash
docker logs sg-sentinel-1 2>&1 | grep -E "sdown|odown|switch-master" | tail -10
```

**이번엔 이렇게 보임**:
```
+sdown master mymaster host.docker.internal 6380      ← 5초 뒤 감지
+odown master mymaster host.docker.internal 6380      ← 즉시 quorum 확정
+switch-master mymaster host.docker.internal 6380 host.docker.internal 6381
```

**핵심**: **`+sdown`이 나온다.** 이게 A 시나리오와의 결정적 차이. Sentinel의 5초 감지 대기가 그대로 발생.

**② HAProxy 상태 변화**

```bash
curl -s 'http://localhost:8404/;csv' | awk -F, '$1=="redis_master_back" && $2!="BACKEND" {printf "%-10s %s\n", $2, $18}'
```

**출력**:
```
master     UP or DOWN (원래 마스터였던 놈에 따라 다름)
replica1   DOWN
replica2   UP    ← 새로 승격된 놈
```

**③ 다운타임**

```bash
echo "FAIL 개수: $(grep -c FAIL /tmp/ha-kill.log)"
grep FAIL /tmp/ha-kill.log | head -5
```

**결과**:
- Sentinel 로그 상: 마스터 죽음 → 새 마스터 확정까지 **약 6초**
- Ping 스크립트의 FAIL 개수는 이보다 적게 나올 수 있음 (측정 도구의 한계). 정확한 다운타임은 sentinel 로그의 timestamp를 기준으로 판단.

---

## 5. 시나리오 C (선택): Sentinel만 사용 (HAProxy 없는 원래 방식)

이 시나리오는 앱이 sentinel discovery를 직접 하는 경우다. 우리 실습은 HAProxy를 이미 도입한 상태라서, 앱을 sentinel 프로필로 붙여야 한다. 실제 앱 코드를 실행할 여력이 있을 때 해 봐라.

```bash
# 앱을 sentinel discovery 프로필로 실행 (별도 터미널)
SPRING_PROFILES_ACTIVE=ha ./gradlew :studygroup-api:bootRun
# ↑ HAProxy 를 안 거치고, 앱이 sentinel 3대에 직접 물어본다.

# 그 상태에서 docker kill sg-redis-master
# 앱 로그를 관찰: Lettuce 가 topology 재조회하는 데 걸리는 시간까지 다운타임에 포함됨.
```

체감 다운타임: **8~15초** (sentinel 감지 5초 + Lettuce topology refresh 3~10초).

---

## 6. 3가지 시나리오 비교

측정 후 이 표를 채워 봐라.

| 시나리오 | Sentinel 이벤트 로그 | 관측된 앱 다운타임 |
|---|---|---|
| A. Predictive (`docker stop`) | `try-failover → switch-master` (sdown 없음) | 0초 (FAIL 없음) |
| B. Kill + HAProxy (`docker kill`) | `sdown(5s) → switch-master` | ~6초 |
| C. Kill + Sentinel discovery (앱 프로필 ha) | 위와 동일하지만 Lettuce refresh 추가 | 8~15초 |

**결론 한 줄**:
- 계획된 배포는 A로 → 다운타임 0
- 하드웨어 장애 대비는 B → 다운타임 ~6초로 축소
- HAProxy를 끼우는 것만으로 C의 절반 이하로 줄어듦

---

## 7. 정리 (실습 끝난 뒤 🔴 필수)

### HA 스택 내리기

```bash
docker compose -f docker-compose.ha.yml down
```

`-v` 옵션은 안 붙였으니 데이터는 남는다. 다시 실습할 때 새 데이터로 시작하고 싶으면 `down -v`.

### baton 다시 살리기

실습 시작할 때 stop했다면 원상복구:

```bash
docker start baton-redis baton-postgres
```

### 임시 파일 정리

```bash
rm -f /tmp/ha-ping-loop.sh /tmp/ha-predictive.log /tmp/ha-kill.log
```

---

## 8. 트러블슈팅

### 🔴 `docker stop`이 10초 넘게 걸림

prestop 스크립트가 timeout까지 갔다는 신호. 원인 2가지.

**원인 1**: replica 가 sentinel과 이름 불일치. `redis-configs/replica-1.conf`, `replica-2.conf` 파일에서
```
replicaof host.docker.internal 6379
```
로 되어 있는지 확인. `replicaof redis-master 6379`로 되어 있으면 sentinel이 `+fix-slave-config` 하느라 promote가 지연됨.

**원인 2**: sentinel 로그에 `-failover-abort-no-good-slave`가 있음.
```bash
docker logs sg-sentinel-1 2>&1 | grep abort
```
있으면 replica들의 상태가 이상함. 스택 전체 재시작:
```bash
docker compose -f docker-compose.ha.yml down -v
docker compose -f docker-compose.ha.yml up -d redis-master redis-replica-1 redis-replica-2 sentinel-1 sentinel-2 sentinel-3 haproxy
```

### 🟡 HAProxy Stats 페이지가 접속 안 됨

컨테이너 상태 확인:
```bash
docker ps --filter "name=sg-haproxy"
```
`Up`이 아니면:
```bash
docker logs sg-haproxy
```
설정 파일 문법 에러가 대부분. `redis-configs/haproxy.cfg` 확인.

### 🟡 Ping 스크립트가 FAIL 없이 조용함

정상일 수도 있고, `docker exec`가 hang 걸린 것일 수도 있음. 로그 라인 수 확인:
```bash
wc -l /tmp/ha-predictive.log
```
30초 실행했는데 20라인 미만이면 hang. `perl -e 'alarm 1; exec @ARGV'` 부분이 제대로 실행됐는지 확인 (macOS 기본 perl 있어야 함).

### 🟢 다른 포트 충돌

다른 프로젝트의 컨테이너가 5432/6379를 잡고 있으면 위와 같이 stop. 확인:
```bash
lsof -i :6379 -i :5432 -i :6390 -i :8404
```

---

## 부록: 명령어 치트시트

```bash
# 상태 확인
docker exec sg-sentinel-1 redis-cli -p 26379 SENTINEL get-master-addr-by-name mymaster
docker exec sg-sentinel-1 redis-cli -p 26379 SENTINEL master mymaster
docker exec sg-sentinel-1 redis-cli -p 26379 SENTINEL replicas mymaster
curl -s 'http://localhost:8404/;csv' | awk -F, '$1=="redis_master_back" && $2!="BACKEND" {printf "%-10s %s\n", $2, $18}'

# 로그
docker logs -f sg-sentinel-1
docker logs sg-redis-master 2>&1 | grep '\[prestop\]'
docker logs sg-haproxy

# HAProxy 통해 Redis 직접 조작
docker exec sg-sentinel-1 redis-cli -h haproxy -p 6390 SET mykey myvalue
docker exec sg-sentinel-1 redis-cli -h haproxy -p 6390 GET mykey
docker exec sg-sentinel-1 redis-cli -h haproxy -p 6390 INFO replication

# 페일오버 트리거 (수동)
docker stop sg-redis-master              # Predictive (0초)
docker kill sg-redis-master              # Reactive (6초)
docker exec sg-sentinel-1 redis-cli -p 26379 SENTINEL FAILOVER mymaster   # sentinel 에 직접 요청
```
