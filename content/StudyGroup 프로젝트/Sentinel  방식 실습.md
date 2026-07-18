---
title: "[studygroup] Redis Sentinel"
publish: true
created: 2026-07-11T23:39:07+09:00
modified: 2026-07-12T13:48:08+09:00
cover: pasted-image-20260712015908.png
---
## Prologue
- Redis Sentine은 무엇인가?
- 어떻게 실습할까?

___

# 1. Redis Sentinel

>- Redis 설정에 문제가 발생했을 때 모니터링, 알람, 자동 페일 오버를 제공하는 Redis 용 고가용성 솔루션
>- 분산 환경에서 레디스와 함께 동작하도록 설계됨
>- 레디스의 상태와 신뢰성을 유지하는데 도움을 준다.

#### 1. 모니터링
- 주기적으로 Redis 인스턴스 상태 확인
- 가용성, 지연율과 같은 인스턴스 상태 관련 수치 정보 수집

#### 2. 알람
- Master 혹은 Replica 노드에 장애가 발생했을 때 알아챈다.
- 이를 시스템 관리자 or 다른 모니터링 시스템에 장애를 알린다.

#### 3. 자동 장애 극복
- 마스터 노드 장애 -> 장애 극복
	- 다른 Replica가 마스터 역할 수행
	- 다른 Replica가 새로운 마스터를 사용하기 위해 노드 설정 재구성

#### 4. 구성 정보 제공자
- Redis Sentinel이 Redis Configuraion에 대한 권한 소스가 될 수 있음
- 클라이언트는 Redis Sentinel을 퀴리하여 현재 마스터 노드의 주소를 얻을 수 있음
	- <mark class="hltr-yellow">이에 따라 장애 조치 후에 새로운 마스터 주소를 알 수 있음</mark>


### 어떻게 사용할 수 있을까?
- Redis 노드를 모니터링할 Redis Sentinel 인스턴스의 클러스터를 설정해야한다!
	- 적어도 3개의 Redis Sentinel 인스턴스가 있어야한다 -> 장애 극복 조치가 실질적으로 가능해기 때문

___

# 2. Redis Sentinel  설정

#### docker.compose.ha.yml
```yml title:"docker.compose.ha.yml" hl:5,20,38,56,73,89
# 구성: master 1 + replica 2 + sentinel 3 (quorum 2)  
# 앱은 호스트에서 실행되므로 각 노드는 host.docker.internal 로 자신을 광고함
  
services:  
  redis-master:  
    image: redis:7-alpine  
    container_name: sg-redis-master  
    command: ["redis-server", "/etc/redis/redis.conf"]  
    volumes:  
      - ./redis-configs/master.conf:/etc/redis/redis.conf:ro  
      - sg-redis-master-data:/data  
    ports:  
      - "6379:6379"  
    healthcheck:  
      test: ["CMD", "redis-cli", "ping"]  
      interval: 5s  
      timeout: 3s  
      retries: 5  
  
  redis-replica-1:  
    image: redis:7-alpine  
    container_name: sg-redis-replica-1  
    command: ["redis-server", "/etc/redis/redis.conf"]  
    volumes:  
      - ./redis-configs/replica-1.conf:/etc/redis/redis.conf:ro  
      - sg-redis-replica-1-data:/data  
    ports:  
      - "6380:6379"  
    depends_on:  
      redis-master:  
        condition: service_healthy  
    healthcheck:  
      test: ["CMD", "redis-cli", "ping"]  
      interval: 5s  
      timeout: 3s  
      retries: 5  
  
  redis-replica-2:  
    image: redis:7-alpine  
    container_name: sg-redis-replica-2  
    command: ["redis-server", "/etc/redis/redis.conf"]  
    volumes:  
      - ./redis-configs/replica-2.conf:/etc/redis/redis.conf:ro  
      - sg-redis-replica-2-data:/data  
    ports:  
      - "6381:6379"  
    depends_on:  
      redis-master:  
        condition: service_healthy  
    healthcheck:  
      test: ["CMD", "redis-cli", "ping"]  
      interval: 5s  
      timeout: 3s  
      retries: 5  
  
  sentinel-1:  
    image: redis:7-alpine  
    container_name: sg-sentinel-1  
    # sentinel.conf 는 sentinel 이 상태를 기록해야 하므로 rw
    command: ["redis-sentinel", "/etc/redis/sentinel.conf"]  
    volumes:  
      - ./redis-configs/sentinel-1.conf:/etc/redis/sentinel.conf  
    ports:  
      - "26379:26379"  
    depends_on:  
      redis-master:  
        condition: service_healthy  
      redis-replica-1:  
        condition: service_started  
      redis-replica-2:  
        condition: service_started  
  
  sentinel-2:  
    image: redis:7-alpine  
    container_name: sg-sentinel-2  
    command: ["redis-sentinel", "/etc/redis/sentinel.conf"]  
    volumes:  
      - ./redis-configs/sentinel-2.conf:/etc/redis/sentinel.conf  
    ports:  
      - "26380:26379"  
    depends_on:  
      redis-master:  
        condition: service_healthy  
      redis-replica-1:  
        condition: service_started  
      redis-replica-2:  
        condition: service_started  
  
  sentinel-3:  
    image: redis:7-alpine  
    container_name: sg-sentinel-3  
    command: ["redis-sentinel", "/etc/redis/sentinel.conf"]  
    volumes:  
      - ./redis-configs/sentinel-3.conf:/etc/redis/sentinel.conf  
    ports:  
      - "26381:26379"  
    depends_on:  
      redis-master:  
        condition: service_healthy  
      redis-replica-1:  
        condition: service_started  
      redis-replica-2:  
        condition: service_started  
  
volumes:  
  sg-redis-master-data:  
  sg-redis-replica-1-data:  
  sg-redis-replica-2-data:
```

#### 구성
- 데이터 서버 3대 : master 1(읽기/쓰기), replica 2대 (master의 복사본, 읽기 전용)
- Redis Seinel 인스턴스 3대 : 데이터는 가지지 않고, master가 죽었는지 확인만

#### 주요 설정
1. **named volume**
``` yml
volumes: - sg-redis-master-data:/data
```
- master가 죽었다가 다시 되살라났을 때, volume을 읽고 "나 master임"뜬다.
- 이때 Sentinel이 개입해서 replica로 강등시키는 것을 확인하기 위해서 volume을 남겼다.

2. **Sentinel의 conf에만 rw로 마운트 하기**
```yml
volumes:  
  - ./redis-configs/master.conf:/etc/redis/redis.conf:ro     # 읽기 전용
  ...
  - ./redis-configs/sentinel-1.conf:/etc/redis/sentinel.conf # :ro 없음 (읽기/쓰기 가능)
```
- Sentinel은 실행 중에 자기 conf 파일을 수정한다.
	- 새로운 master 갱신
	- 다른 sentinel 발견하면 추가
	- replica 발견하면 추가
- <mark class="hltr-yellow">Sentinel은 "지금 master가 누구인가"를 기억해야하기 때문</mark>


#### application-ha.yml
```yml
# Redis Sentinel HA 프로필.  
# 실행: SPRING_PROFILES_ACTIVE=ha ./gradlew :studygroup-api:bootRun  
# 기존 application.yaml 의 spring.data.redis.host/port 를 여기서 덮어씀    
  
spring:  
  data:  
    redis:  
      sentinel:  
        master: mymaster  
        nodes:  
          - localhost:26379  
          - localhost:26380  
          - localhost:26381  
      # Lettuce topology refresh: 페일오버 후 새 마스터 주소를 다시 잡아오도록.  
      # adaptive=true : 예외를 감지하면 즉시 topology 재조회.      
      # period=30s   : 주기적으로도 재조회.      
      lettuce:  
        cluster:  
          refresh:  
            adaptive: true  
            period: 30s
```
- Redis의 동작 방식을 기존에는 바로 Redis 서버에 직접 붙였다면 -> Sentinel 3대에게 먼저 물어봄.
	- "mymaster라는 이름의 master가 어디?" -> "6379이다."

- Lettuce는 Spring boot가 쓰는 Redis 클라이언트 라이브러리
	- "현재 master가 6379"라는 사실을 메모리에 캐싱.
		- 연결 실패 같은 예외 발생 -> Sentinel에 물어본다.
		- 30초 마다 확인

___

# 실제 동작 확인

#### 초기상태
```
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-sentinel-1 redis-cli -p 26379 sentinel master mymaster
 1) "name"
 2) "mymaster"
 3) "ip"
 4) "host.docker.internal"
 5) "port"
 6) "6379"
...
```
- 우리가 yml 파일에 설정한대로, `6379`포트가 master인 것을 확인할 수 있습니다.

#### master kill 이후의 로그
```
djlim00@DJs-MacBook-Pro studygroup % docker kill sg-redis-master

# master 죽음 감지
1:X 11 Jul 2026 16:23:40.613 # +sdown master mymaster host.docker.internal 6379
...

# 투표 진행
1:X 11 Jul 2026 16:23:40.699 # +new-epoch 1
1:X 11 Jul 2026 16:23:40.701 # +vote-for-leader ecaa1f13286d5a421f3cf310ff0aa036783f105a 1

# 투표 결과 3대의 Sentinel이 master가 죽었음을 동의
1:X 11 Jul 2026 16:23:41.744 # +odown master mymaster host.docker.internal 6379 #quorum 3/2

# 페일오버 진행 -> 새로운 master는 6380
1:X 11 Jul 2026 16:23:41.912 # +config-update-from sentinel ecaa1f13286d5a421f3cf310ff0aa036783f105a host.docker.internal 26381 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:23:41.912 # +switch-master mymaster host.docker.internal 6379 host.docker.internal 6380
```

1. master의 죽음을 감지 +sdown
2. 새로운 master를 위한 투표 진행
3. 투표 결과
4. 페일오버를 진행하여서 새로운 master(6380) 선출

#### master를 다시 되살리면?
```
djlim00@DJs-MacBook-Pro studygroup % docker start sg-redis-master

1:X 11 Jul 2026 16:23:46.954 # +sdown slave host.docker.internal:6379 host.docker.internal 6379 @ mymaster host.docker.internal 6380
```
- 기존의 master는 sdown -> 즉 replica로 편입된다!


#### 확인 - 현재의 마스터(6380)
```
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-sentinel-1 redis-cli -p 26379 sentinel master mymaster
 1) "name"
 2) "mymaster"
 3) "ip"
 4) "host.docker.internal"
 5) "port"
 6) "6380"
...
7) "num-slaves"
8) "2"
```
- num-slaves가 2인 것을 확인할 수 있다.


#### 확인 - 기존의 마스터(6379)
```
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-redis-master redis-cli info replication
# Replication
role:slave
master_host:host.docker.internal
master_port:6380
```
- role:slave가 된 것을 확인할 수 있다.


___

# 3. 실제 사용자 입장에서

#### 1. 로그인 완료 화면 (초기화면)
![[Pasted image 20260712015908.png]]

#### 2. master kill 직후
![[Pasted image 20260712015937.png]]
- 잠시 500에러가 발생하고

#### 3. 새로운 master 선출 완료
![[Pasted image 20260712015954.png]]
- 몇 초 후에 선출되자마자 다시 동작하는 것을 확인할 수 있다!
- 로그인 세션도 유지된다!


___

# 전체 로그 기록

#### 센티넬 로그 : docker logs -f sg-sentinel-1 
```
djlim00@DJs-MacBook-Pro studygroup % docker logs -f sg-sentinel-1
1:X 11 Jul 2026 16:18:08.414 * oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
1:X 11 Jul 2026 16:18:08.414 * Redis version=7.4.9, bits=64, commit=00000000, modified=0, pid=1, just started
1:X 11 Jul 2026 16:18:08.414 * Configuration loaded
1:X 11 Jul 2026 16:18:08.414 * monotonic clock: POSIX clock_gettime
1:X 11 Jul 2026 16:18:08.415 * Running mode=sentinel, port=26379.
1:X 11 Jul 2026 16:18:08.416 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:18:08.416 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:18:08.416 * Sentinel ID is 4344e3f32f8cc886ff29d01239587c0dd2a7e530
1:X 11 Jul 2026 16:18:08.416 # +monitor master mymaster host.docker.internal 6379 quorum 2
1:X 11 Jul 2026 16:18:10.426 * +sentinel sentinel 0e618b2a3cf67c7c5185a2a65072c01da4883f72 host.docker.internal 26380 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:18:10.429 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:18:10.429 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:18:10.486 * +sentinel sentinel ecaa1f13286d5a421f3cf310ff0aa036783f105a host.docker.internal 26381 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:18:10.487 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:18:10.488 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:18:18.475 * +slave slave host.docker.internal:6380 host.docker.internal 6380 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:18:18.476 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:18:18.476 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:18:18.478 * +slave slave host.docker.internal:6381 host.docker.internal 6381 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:18:18.479 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:18:18.479 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:18:28.571 * +fix-slave-config slave host.docker.internal:6381 host.docker.internal 6381 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:18:28.571 * +fix-slave-config slave host.docker.internal:6380 host.docker.internal 6380 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:23:40.613 # +sdown master mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:23:40.699 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:23:40.699 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:23:40.699 # +new-epoch 1
1:X 11 Jul 2026 16:23:40.701 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:23:40.701 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:23:40.701 # +vote-for-leader ecaa1f13286d5a421f3cf310ff0aa036783f105a 1
1:X 11 Jul 2026 16:23:41.744 # +odown master mymaster host.docker.internal 6379 #quorum 3/2
1:X 11 Jul 2026 16:23:41.744 * Next failover delay: I will not start a failover before Sat Jul 11 16:24:01 2026
1:X 11 Jul 2026 16:23:41.912 # +config-update-from sentinel ecaa1f13286d5a421f3cf310ff0aa036783f105a host.docker.internal 26381 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:23:41.912 # +switch-master mymaster host.docker.internal 6379 host.docker.internal 6380
1:X 11 Jul 2026 16:23:41.918 * +slave slave host.docker.internal:6381 host.docker.internal 6381 @ mymaster host.docker.internal 6380
1:X 11 Jul 2026 16:23:41.920 * +slave slave host.docker.internal:6379 host.docker.internal 6379 @ mymaster host.docker.internal 6380
1:X 11 Jul 2026 16:23:41.925 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:23:41.925 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:23:46.954 # +sdown slave host.docker.internal:6379 host.docker.internal 6379 @ mymaster host.docker.internal 6380
1:X 11 Jul 2026 16:34:01.721 # +tilt #tilt mode entered
1:X 11 Jul 2026 16:34:31.748 # -tilt #tilt mode exited
1:X 11 Jul 2026 16:38:17.452 # -sdown slave host.docker.internal:6379 host.docker.internal 6379 @ mymaster host.docker.internal 6380
1:X 11 Jul 2026 16:55:35.845 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:55:35.845 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:55:35.845 # +new-epoch 2
1:X 11 Jul 2026 16:55:35.848 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:55:35.848 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:55:35.848 # +vote-for-leader 0e618b2a3cf67c7c5185a2a65072c01da4883f72 2
1:X 11 Jul 2026 16:55:35.848 # +sdown master mymaster host.docker.internal 6380
1:X 11 Jul 2026 16:55:35.903 # +odown master mymaster host.docker.internal 6380 #quorum 3/2
1:X 11 Jul 2026 16:55:35.903 * Next failover delay: I will not start a failover before Sat Jul 11 16:55:55 2026
1:X 11 Jul 2026 16:55:36.799 # +config-update-from sentinel 0e618b2a3cf67c7c5185a2a65072c01da4883f72 host.docker.internal 26380 @ mymaster host.docker.internal 6380
1:X 11 Jul 2026 16:55:36.799 # +switch-master mymaster host.docker.internal 6380 host.docker.internal 6379
1:X 11 Jul 2026 16:55:36.805 * +slave slave host.docker.internal:6381 host.docker.internal 6381 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:55:36.806 * +slave slave host.docker.internal:6380 host.docker.internal 6380 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:55:36.809 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:55:36.809 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:55:41.884 # +sdown slave host.docker.internal:6380 host.docker.internal 6380 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:58:03.671 # -sdown slave host.docker.internal:6380 host.docker.internal 6380 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:58:19.890 * +fix-slave-config slave host.docker.internal:6380 host.docker.internal 6380 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:59:34.896 # +sdown master mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:59:35.008 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:59:35.008 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:59:35.008 # +new-epoch 3
1:X 11 Jul 2026 16:59:35.010 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:59:35.010 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:59:35.010 # +vote-for-leader 0e618b2a3cf67c7c5185a2a65072c01da4883f72 3
1:X 11 Jul 2026 16:59:35.995 # +odown master mymaster host.docker.internal 6379 #quorum 3/2
1:X 11 Jul 2026 16:59:35.995 * Next failover delay: I will not start a failover before Sat Jul 11 16:59:55 2026
1:X 11 Jul 2026 16:59:36.302 # +config-update-from sentinel 0e618b2a3cf67c7c5185a2a65072c01da4883f72 host.docker.internal 26380 @ mymaster host.docker.internal 6379
1:X 11 Jul 2026 16:59:36.302 # +switch-master mymaster host.docker.internal 6379 host.docker.internal 6380
1:X 11 Jul 2026 16:59:36.306 * +slave slave host.docker.internal:6381 host.docker.internal 6381 @ mymaster host.docker.internal 6380
1:X 11 Jul 2026 16:59:36.308 * +slave slave host.docker.internal:6379 host.docker.internal 6379 @ mymaster host.docker.internal 6380
1:X 11 Jul 2026 16:59:36.310 # Could not rename tmp config file (Resource busy)
1:X 11 Jul 2026 16:59:36.310 # WARNING: Sentinel was not able to save the new configuration on disk!!!: Resource busy
1:X 11 Jul 2026 16:59:41.309 # +sdown slave host.docker.internal:6379 host.docker.internal 6379 @ mymaster host.docker.internal 6380
```


#### 2. 확인 로그
```
djlim00@DJs-MacBook-Pro studygroup % docker kill sg-redis-master
sg-redis-master
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-sentinel-1 redis-cli -p 26379
  sentinel master mymaster | head -20
127.0.0.1:26379> 
zsh: command not found: sentinel
djlim00@DJs-MacBook-Pro studygroup % docker ps
CONTAINER ID   IMAGE                COMMAND                  CREATED         STATUS                   PORTS                                             NAMES
1040898ac696   redis:7-alpine       "docker-entrypoint.s…"   9 minutes ago   Up 8 minutes             0.0.0.0:26381->26379/tcp, [::]:26381->26379/tcp   sg-sentinel-3
f736485e68b8   redis:7-alpine       "docker-entrypoint.s…"   9 minutes ago   Up 8 minutes             0.0.0.0:26379->26379/tcp, [::]:26379->26379/tcp   sg-sentinel-1
76d9bb6e63d3   redis:7-alpine       "docker-entrypoint.s…"   9 minutes ago   Up 8 minutes             0.0.0.0:26380->26379/tcp, [::]:26380->26379/tcp   sg-sentinel-2
d406beaf6bf1   redis:7-alpine       "docker-entrypoint.s…"   9 minutes ago   Up 8 minutes (healthy)   0.0.0.0:6381->6379/tcp, [::]:6381->6379/tcp       sg-redis-replica-2
236e4bf6b726   redis:7-alpine       "docker-entrypoint.s…"   9 minutes ago   Up 8 minutes (healthy)   0.0.0.0:6380->6379/tcp, [::]:6380->6379/tcp       sg-redis-replica-1
ab886da363f9   postgres:16-alpine   "docker-entrypoint.s…"   9 minutes ago   Up 8 minutes (healthy)   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp       studygroup-postgres
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-sentinel-1 redis-cli -p 26379
  sentinel master mymaster | head -20
127.0.0.1:26379> c
zsh: command not found: sentinel
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-sentinel-1 redis-cli -p 26379 sentinel master mymaster
 1) "name"
 2) "mymaster"
 3) "ip"
 4) "host.docker.internal"
 5) "port"
 6) "6380"
 7) "runid"
 8) "0287de87cf6c4b2260a3e72579ed8f668f320d3b"
 9) "flags"
10) "master"
11) "link-pending-commands"
12) "0"
13) "link-refcount"
14) "1"
15) "last-ping-sent"
16) "0"
17) "last-ok-ping-reply"
18) "395"
19) "last-ping-reply"
20) "395"
21) "down-after-milliseconds"
22) "5000"
23) "info-refresh"
24) "1362"
25) "role-reported"
26) "master"
27) "role-reported-time"
28) "825921"
29) "config-epoch"
30) "1"
31) "num-slaves"
32) "2"
33) "num-other-sentinels"
34) "2"
35) "quorum"
36) "2"
37) "failover-timeout"
38) "10000"
39) "parallel-syncs"
40) "1"
djlim00@DJs-MacBook-Pro studygroup % docker ps
CONTAINER ID   IMAGE                COMMAND                  CREATED          STATUS                    PORTS                                             NAMES
1040898ac696   redis:7-alpine       "docker-entrypoint.s…"   19 minutes ago   Up 19 minutes             0.0.0.0:26381->26379/tcp, [::]:26381->26379/tcp   sg-sentinel-3
f736485e68b8   redis:7-alpine       "docker-entrypoint.s…"   19 minutes ago   Up 19 minutes             0.0.0.0:26379->26379/tcp, [::]:26379->26379/tcp   sg-sentinel-1
76d9bb6e63d3   redis:7-alpine       "docker-entrypoint.s…"   19 minutes ago   Up 19 minutes             0.0.0.0:26380->26379/tcp, [::]:26380->26379/tcp   sg-sentinel-2
d406beaf6bf1   redis:7-alpine       "docker-entrypoint.s…"   19 minutes ago   Up 19 minutes (healthy)   0.0.0.0:6381->6379/tcp, [::]:6381->6379/tcp       sg-redis-replica-2
236e4bf6b726   redis:7-alpine       "docker-entrypoint.s…"   19 minutes ago   Up 19 minutes (healthy)   0.0.0.0:6380->6379/tcp, [::]:6380->6379/tcp       sg-redis-replica-1
ab886da363f9   postgres:16-alpine   "docker-entrypoint.s…"   19 minutes ago   Up 19 minutes (healthy)   0.0.0.0:5432->5432/tcp, [::]:5432->5432/tcp       studygroup-postgres
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-redis-replica-1 redis-cli info replication
# Replication
role:master
connected_slaves:1
slave0:ip=host.docker.internal,port=6381,state=online,offset=301544,lag=1
master_failover_state:no-failover
master_replid:3da655da55778506f437ca24f33a7974b429e20a
master_replid2:cd5f4965fce9d3aeb54219585521b22065276d8f
master_repl_offset:301544
second_repl_offset:96378
repl_backlog_active:1
repl_backlog_size:1048576
repl_backlog_first_byte_offset:974
repl_backlog_histlen:300571
djlim00@DJs-MacBook-Pro studygroup % docker start sg-redis-master
sg-redis-master
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-sentinel-1 redis-cli -p 26379 sentinel master mymaster
 1) "name"
 2) "mymaster"
 3) "ip"
 4) "host.docker.internal"
 5) "port"
 6) "6380"
 7) "runid"
 8) "0287de87cf6c4b2260a3e72579ed8f668f320d3b"
 9) "flags"
10) "master"
11) "link-pending-commands"
12) "0"
13) "link-refcount"
14) "1"
15) "last-ping-sent"
16) "0"
17) "last-ok-ping-reply"
18) "1011"
19) "last-ping-reply"
20) "1011"
21) "down-after-milliseconds"
22) "5000"
23) "info-refresh"
24) "9048"
25) "role-reported"
26) "master"
27) "role-reported-time"
28) "893963"
29) "config-epoch"
30) "1"
31) "num-slaves"
32) "2"
33) "num-other-sentinels"
34) "2"
35) "quorum"
36) "2"
37) "failover-timeout"
38) "10000"
39) "parallel-syncs"
40) "1"
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-redis-master redis-cli info replication
# Replication
role:slave
master_host:host.docker.internal
master_port:6380
master_link_status:up
master_last_io_seconds_ago:0
master_sync_in_progress:0
slave_read_repl_offset:511059
slave_repl_offset:511059
slave_priority:100
slave_read_only:1
replica_announced:1
connected_slaves:0
master_failover_state:no-failover
master_replid:3da655da55778506f437ca24f33a7974b429e20a
master_replid2:0000000000000000000000000000000000000000
master_repl_offset:511059
second_repl_offset:-1
repl_backlog_active:1
repl_backlog_size:1048576
repl_backlog_first_byte_offset:308295
repl_backlog_histlen:202765
djlim00@DJs-MacBook-Pro studygroup % docker kill sg-redis-replica-1
sg-redis-replica-1
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-sentinel-1 redis-cli -p 26379 sentinel get-master-addr-by-name mymaster
1) "host.docker.internal"
2) "6379"
djlim00@DJs-MacBook-Pro studygroup % docker start sg-redis-replica-1
sg-redis-replica-1
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-sentinel-1 redis-cli -p 26379 sentinel master mymaster | head -8
 3) "name"
 4) "mymaster"
 5) "ip"
 6) "host.docker.internal"
 7) "port"
 8) "6379"
 9) "runid"
 10) "b7554313ed6de0c25f66addca61646f9c1ad7963"
djlim00@DJs-MacBook-Pro studygroup % djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-sentinel-1 redis-cli -p 26379 sentinel master mymaster | head -8
zsh: command not found: djlim00@DJs-MacBook-Pro
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-sentinel-1 redis-cli -p 26379 sentinel master mymaster | head -8
 11) "name"
 12) "mymaster"
 13) "ip"
 14) "host.docker.internal"
 15) "port"
 16) "6379"
 17) "runid"
 18) "b7554313ed6de0c25f66addca61646f9c1ad7963"
djlim00@DJs-MacBook-Pro studygroup % docker exec -it sg-sentinel-1 redis-cli -p 26379 sentinel get-master-addr-by-name mymaster
19) "host.docker.internal"
20) "6379"
djlim00@DJs-MacBook-Pro studygroup % docker kill sg-redis-master
sg-redis-master
djlim00@DJs-MacBook-Pro studygroup % 
```




- 마스터-슬레이브 구조에서 내가 설정한 구조
	- 그리고 원리에 대해서
	- 이게 왜 HA인지
	- <mark class="hltr-yellow">지금은 다운타임 동안, 어떻게 해야할까? -> 나는 이 부분이 좀 걸리는데 -> 어떻게 하면 다운 타임을 최소화할 수 있을까?</mark>


#### 1. New 사이드 프로젝트 주제 - 로깅
- <mark class="hltr-yellow">Logback,  MDC설정 (muti-profile 기본으로 깔고 가고) </mark>
	- 어필 포인트1. 둘이 개념과 왜 필요한지 -> 좀 야가긴해
	- 직접 퍼다가 ELK -> 대시보드 만들기(Grafana)
	- key값들은 왜 이 값을 설정을 했냐! 이걸 진짜로 생각을 해서 중요한 값을 내가 선정해서 한건지!

