
> **고성능 웹 서버 + 리버스 프록시 + 로드 밸런서**

- 단순하게 HTML을 서비스 역할 뿐만 아니라, 클라이언트의 요청을 받아서 다른 서버로 전달(proxy), 로드밸런싱도 할 수 있음

![[Pasted image 20251106172116.png]]
이때 Nginx는 **가장 앞단(Gateway)** 에 서서
- 요청 수 제한 (Rate Limit)
- 로깅
- 캐싱
- 부하 분산
- SSL 처리  

### 1. .conf 구조
```java
worker_processes  1;  # 워커 프로세스 수

events {
    worker_connections  1024;  # 한 워커당 최대 연결 수
}

http {
    server {
        listen 80;  # 80번 포트로 HTTP 요청 받기
        server_name localhost;

        location / {
            root /usr/share/nginx/html;  # 정적 파일 경로
            index index.html;             # 기본 파일명
        }
    }
}

```
- <u>블록 단위로 동작을 정의</u>
-> <mark class="hltr-yellow">nginx가 어떻게 요청을 처리할지 정의</mark> -> 명령어 기반 설정 스크립트

### 2. OpenResty란 무엇일까?

> **OpenResty = Nginx + Lua(스크립트 엔진)**

- nginx 안에서 Lua 코드를 직접 실행할 수 있도록 확장한 서버.
=> <span style="background:#b1ffff">단순히 요청을 프록시 하는게 아니라, 요청을 Lua 코드로 동적으로 처리</span>

![[Pasted image 20251106172444.png]]

![[Pasted image 20251106172513.png]]

___
## Redis란?

> **Redis = 인메모리 데이터베이스**
> **(데이터를 RAM에 저장해서 매우 빠르게 접근)**

#### Redis 명령어

| 명령                      | 의미            | 예시                     |
| ----------------------- | ------------- | ---------------------- |
| `SET key value`         | 값 저장          | `SET user:1 "kim"`     |
| `GET key`               | 값 조회          | `GET user:1`           |
| `INCR key`              | 숫자 1 증가       | `INCR counter`         |
| `EXPIRE key seconds`    | TTL 설정        | `EXPIRE counter 60`    |
| `ZADD key score member` | Sorted Set 추가 | `ZADD users 100 "kim"` |
| `ZCOUNT key min max`    | 범위 내 요소 개수    | `ZCOUNT users 0 200`   |
현재 실습에서는 Sorted Set(`ZADD`, `ZCOUNT`)를 이용해서 요청이 언제 왔는지를 **타임스탬프(timestamp)** 로 저장하고,  “현재 시점 기준으로 얼마만큼 요청이 있었는지”를 계산함.

___
## Lua Script란?

- Redis는 싱글 스레드 -> **여러 명령(GET, INCR, EXPIRE 등)을 원자적으로 실행하려면 한 번에 묶어서 실행할 방법이 필요**
- 따라서 Redis는 내부에서 Lua 스크립트를 실행할 수 있는 기능을 제공

```java title:"Redis 내부에서 실행되는 Lua"
local count = tonumber(redis.call('GET', 'count') or '0')
if count >= 5 then
  return 0
else
  redis.call('INCR', 'count')
  redis.call('EXPIRE', 'count', 60)
  return count + 1
end
```
=> 단일 트랜잭션으로 처리하므로 원자적



![[Pasted image 20251106173358.png]]


___
## 실습 설명

```sql
Dockerfile      → 환경을 만들기 위한 설정서 (어떤 이미지 + 어떤 파일 복사)
nginx.conf      → Nginx의 기본 설정
nginx_lua.conf  → 실제 라우팅 / Lua 코드 실행 위치 지정
check_limit.lua → Redis에서 실행될 Lua 로직
run.sh          → Docker 빌드 및 실행 테스트
run_lua_test.sh → Redis + Nginx 통합 실행 테스트
```
