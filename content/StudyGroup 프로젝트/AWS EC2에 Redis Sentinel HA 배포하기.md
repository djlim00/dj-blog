---
title: "[studygroup] AWS EC2에 Redis Sentinel HA 배포하기"
publish: true
created: 2026-08-05T18:30:11+09:00
modified: 2026-08-05T19:15:02+09:00
cover: pasted-image-20260712045126.png
---
 ## Prologue

- Redis Sentinel HA를 실제 여러 서버(AWS EC2)에 흩어놓으면 어떻게 되는가?
- 마스터 인스턴스를 강제로 stop 시켜도 서비스가 살아있는가?
- 이력서에 쓸 "실전 배포" 근거를 만들기 위한 실측 기록

이미 로컬 Docker Compose로 Sentinel 페일오버는 재현해보셨을 터인데,
같은 걸 **AWS EC2 5대에 실제로 흩어놓고** 하면 도커 네트워크에서는 안 보이던 것들이 튀어나옵니다.

1. Default VPC가 없는 계정이라 네트워크부터 직접 만들어야 함
2. `redis6` 패키지의 systemd 유닛이 `--sentinel` 플래그를 안 붙임
3. 인스턴스 stop → start 시 퍼블릭 IP 재할당

**이번 글은 이 배포의 처음부터 끝까지, 그리고 삽질 기록**을 다룹니다.

이력서에 들어갈 문장은 이거 하나입니다.

> Redis Sentinel HA(1 master / 2 replica / 3 sentinel)를 AWS EC2 5대에 CloudFormation으로 배포. 마스터 인스턴스 강제 stop 시나리오에서 자동 페일오버 성공 및 데이터 무손실 유지를 실측 로그로 확인.

---

## Part 0. 최종 아키텍처

![[Pasted image 20260712045126.png]]

```
                        VPC: studygroup-ha (10.0.0.0/16)
                        Subnet: studygroup-ha-public-a (ap-northeast-2a)
                        SG: redis-ha-sg  (22 open / 6379,26379 SG self-ref)
                        ────────────────────────────────────────────

  sg-ha-master               sg-ha-replica-1           sg-ha-replica-2
  10.0.0.113                 10.0.0.48                 10.0.0.36
  ┌──────────────┐           ┌──────────────┐          ┌──────────────┐
  │ redis(6379)  │◄─── 복제 ─│ redis(6379)  │          │ redis(6379)  │
  │              │           │  replicaof   │          │  replicaof   │
  │ sentinel-3   │           │   10.0.0.113 │          │   10.0.0.113 │
  │  (26379)     │           └──────────────┘          └──────────────┘
  └──────────────┘                    ▲                       ▲
        ▲                             │                       │
        └────────── 감시(gossip) ─────┼───────────────────────┘
                                      │
                       ┌──────────────┴───────────┐
                       │                          │
              sg-ha-sentinel-1-app        sg-ha-sentinel-2
              10.0.0.128                  10.0.0.195
              ┌──────────────────┐        ┌──────────────┐
              │ sentinel-1(26379)│        │ sentinel-2   │
              │ (+ Spring app)   │        │  (26379)     │
              └──────────────────┘        └──────────────┘
```

#### 왜 이 구성인가

| 결정 | 이유 |
|---|---|
| 5대 (master 1 + replica 2 + sentinel-app 1 + sentinel 1) | Sentinel 노드 절약을 위해 3번째 Sentinel은 master 노드에 co-locate |
| Sentinel 3개 (홀수) | Quorum 2/3로 스플릿-브레인 방지. 어느 노드 하나 죽어도 2/3 성립 |
| <mark class="hltr-yellow">3번째 Sentinel을 master 노드에 얹기</mark> | master가 죽으면 그 위 Sentinel도 같이 죽음 → 남은 2/3 quorum 성립. sentinel-1-app에 두 개 몰아넣으면 그 노드 죽을 때 2개 동시 손실 → quorum 붕괴. **분산이 원칙** |
| CloudFormation | EC2 5대 개별 생성 실수 방지 + 스택 삭제 한 번으로 정리 |
| 단일 AZ | 실습은 비용/시간 우선. 인스턴스 stop만으로 노드 다운 시연은 성립 |
| t3.micro | Redis 노드 메모리 500MB도 안 씀. 실습 규모엔 충분 |

---

## Part 1. 인프라: CloudFormation으로 EC2 5대 한 번에

#### 1-1. 사전 준비 (콘솔에서 수동)

CloudFormation은 EC2만 만듭니다. 네트워크는 미리 준비했어요.

1. **VPC** `studygroup-ha` — CIDR `10.0.0.0/16`
2. **서브넷** `studygroup-ha-public-a` — `10.0.0.0/24`, `ap-northeast-2a`
3. **IGW** attach + 라우팅 테이블에 `0.0.0.0/0 → igw`
4. **서브넷 "퍼블릭 IPv4 자동 할당" ON**
5. **보안 그룹** `redis-ha-sg` — 인바운드 22 (0.0.0.0/0), 6379/26379 (SG self-ref)
6. **키 페어** `studygroup-ec2.pem` (`chmod 400`)

> **Innovation Sandbox 환경 함정**: default VPC가 삭제되어 있어서 처음부터 만들어야 했음.

#### 1-2. CloudFormation 템플릿 (핵심만)

```yaml title:"aws/ha-stack.yaml (발췌)" hl:8-11,15-17
Parameters:
  VpcId: { Type: AWS::EC2::VPC::Id }
  SubnetId: { Type: AWS::EC2::Subnet::Id }
  SecurityGroupIds: { Type: List<AWS::EC2::SecurityGroup::Id> }
  KeyName: { Type: AWS::EC2::KeyPair::KeyName }
  InstanceType: { Type: String, Default: t3.micro }
  LatestAmiId:
    Type: AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>
    Default: /aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64

Resources:
  Master:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: !Ref LatestAmiId
      UserData:
        Fn::Base64: |
          #!/bin/bash
          dnf install -y redis6
          systemctl enable redis6
      Tags: [{Key: Name, Value: sg-ha-master}]
  # Replica1, Replica2, Sentinel1App(+ java-21), Sentinel2 도 유사
```

- `LatestAmiId` — Amazon Linux 2023 **최신 AMI를 SSM Parameter에서 자동 조회**. AMI ID를 하드코딩하지 않아도 됨
- `UserData` — 부팅 시 `redis6` 자동 설치까지 완료
- **전체 파일**: `aws/ha-stack.yaml` (141줄)

#### 1-3. 결과 (실측 IP)

콘솔에서 스택 생성 → 2~3분 후 5대 다 `CREATE_COMPLETE`.

| Name | 프라이빗 IP | 퍼블릭 IP |
|---|---|---|
| **sg-ha-master** | **`10.0.0.113`** ★ | `43.201.58.248` |
| sg-ha-replica-1 | `10.0.0.48` | `43.203.221.233` |
| sg-ha-replica-2 | `10.0.0.36` | `13.124.45.207` |
| sg-ha-sentinel-1-app | `10.0.0.128` | `43.203.208.211` |
| sg-ha-sentinel-2 | `10.0.0.195` | `3.35.207.169` |

<mark class="hltr-yellow">`sg-ha-master`의 프라이빗 IP `10.0.0.113`이 뒤에 나오는 모든 replica/sentinel 설정에 하드코딩됩니다.</mark>

---

## Part 2. Redis 마스터 + 레플리카 구성

#### 2-1. 마스터 설정

Amazon Linux 2023의 `redis6` 패키지 특이사항:
- 설정 파일: `/etc/redis6/redis6.conf` (아니, `/etc/redis/redis.conf` 아님)
- 서비스 이름: `redis6`
- 유저: `redis6` (아니, `redis` 아님)

```bash
# 3줄만 수정: bind, protected-mode, appendonly
sudo sed -i 's/^bind .*/bind 0.0.0.0/' /etc/redis6/redis6.conf
sudo sed -i 's/^protected-mode yes/protected-mode no/' /etc/redis6/redis6.conf
sudo sed -i 's/^appendonly no/appendonly yes/' /etc/redis6/redis6.conf

sudo systemctl start redis6 && sudo systemctl enable redis6
```

- `bind 0.0.0.0` — replica가 다른 EC2에서 붙을 수 있게
- `protected-mode no` — 비밀번호 없이 외부 접속 허용 (SG로 이미 격리)
- `appendonly yes` — AOF 켜서 재시작해도 데이터 유지

#### 2-2. Replica 2대 설정 — `replicaof` 한 줄 추가

```bash hl:5
sudo sed -i 's/^bind .*/bind 0.0.0.0/' /etc/redis6/redis6.conf
sudo sed -i 's/^protected-mode yes/protected-mode no/' /etc/redis6/redis6.conf
sudo sed -i 's/^appendonly no/appendonly yes/' /etc/redis6/redis6.conf

echo "replicaof 10.0.0.113 6379" | sudo tee -a /etc/redis6/redis6.conf

sudo systemctl start redis6 && sudo systemctl enable redis6
```

#### 2-3. 마스터에서 최종 확인

```bash
redis6-cli info replication
# role:master
# connected_slaves:2                                    ← 0에서 2로
# slave0:ip=10.0.0.48,port=6379,state=online,lag=0
# slave1:ip=10.0.0.36,port=6379,state=online,lag=0
```

여기까지가 **HA 없는 단순 복제**. 마스터가 죽으면 replica는 알아서 승격하지 못합니다. 그래서 Sentinel이 필요해요.

---

## Part 3. Sentinel 3대 띄우기

#### 3-1. Sentinel 설정 (3대 완전 동일)

3대 노드(`sentinel-1-app`, `sentinel-2`, `master`) 각각에 `/etc/redis6/sentinel.conf`:

```conf hl:4-6
port 26379
bind 0.0.0.0
protected-mode no
sentinel monitor mymaster 10.0.0.113 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 10000
sentinel parallel-syncs mymaster 1
```

- `sentinel monitor mymaster 10.0.0.113 6379 2` — 마스터를 `mymaster`란 이름으로 감시, **quorum=2** (3개 중 2개 동의하면 페일오버)
- `down-after-milliseconds 5000` — 5초 응답 없으면 SDOWN 판정
- `failover-timeout 10000` — 페일오버 재시도 간격

#### 3-2. systemd 우회 (삽질 하이라이트)

기본 `redis6-sentinel.service` 를 그냥 `systemctl start` 하면 이렇게 죽었어요:

```
*** FATAL CONFIG FILE ERROR (Redis 6.2.20) ***
>>> 'sentinel monitor mymaster 10.0.0.113 6379 2'
sentinel directive while not in sentinel mode
```

- AL2023의 redis6 유닛이 <mark class="hltr-yellow">`--sentinel` 플래그 없이</mark> `redis6-server` 를 실행함
- Sentinel 모드가 아닌데 sentinel 설정을 읽으니 즉사

**해결**: systemd 씨름 대신 **직접 데몬 실행**.

```bash
sudo redis6-server /etc/redis6/sentinel.conf --sentinel --daemonize yes
```

실습이라 재부팅 지속성은 포기했어요. 프로덕션이면 커스텀 systemd unit 파일을 새로 만들어야 합니다.

#### 3-3. 3개 Sentinel이 서로 인식했는지 확인

```bash hl:5
redis6-cli -p 26379 sentinel master mymaster | head -20
# "ip"                   "10.0.0.113"
# "port"                 "6379"
# "num-slaves"           "2"
# "num-other-sentinels"  "2"      ← ★ 나 말고 2개 인식 (총 3개)
# "quorum"               "2"
# "flags"                "master"
```

`num-other-sentinels: 2` — 3개가 완전히 서로 붙었다는 뜻. HA 구성 완료.

---

## Part 4. ★ 마스터 강제 종료 → 자동 페일오버

이 실습의 심장입니다.

#### 4-1. 페일오버 전 준비

Sentinel-1에서 이벤트를 실시간으로 구독:

```bash
redis6-cli -p 26379 psubscribe '*'
```

무손실 검증을 위해 데이터 하나 심기:

```bash
redis6-cli -h 10.0.0.113 -p 6379 SET failover-test "before-failover"
```

#### 4-2. AWS 콘솔에서 마스터 인스턴스 stop

`sg-ha-master` 체크 → **인스턴스 상태 → 인스턴스 중지**.

이 순간 그 위의 **Redis 마스터와 Sentinel-3이 동시에** 소실됩니다. 남은 Sentinel은 2개 → quorum=2 딱 맞음.

#### 4-3. Sentinel 이벤트 로그 (실측 원문)

```hl:1-3,10,17-18
+sdown sentinel 54c33a765e... 10.0.0.113 26379 @ mymaster 10.0.0.113 6379
+sdown master mymaster 10.0.0.113 6379
+odown master mymaster 10.0.0.113 6379 #quorum 2/2

+new-epoch 1
+try-failover master mymaster 10.0.0.113 6379
+vote-for-leader 059e0c19... 1
+elected-leader master mymaster 10.0.0.113 6379

+selected-slave slave 10.0.0.48:6379 ... @ mymaster 10.0.0.113 6379
+failover-state-send-slaveof-noone slave 10.0.0.48:6379 ...
+failover-state-wait-promotion slave 10.0.0.48:6379 ...
-role-change slave 10.0.0.48:6379 ... new reported role is master
+promoted-slave slave 10.0.0.48:6379 ...

+failover-end master mymaster 10.0.0.113 6379
+switch-master mymaster 10.0.0.113 6379 10.0.0.48 6379    ← ★★★
```

#### 4-4. 이 로그가 말하는 것 (5단계)

**① 감지 (0~5초)**
- `+sdown` — 각 Sentinel이 개별적으로 "마스터 응답 없음" 판정
- `+odown #quorum 2/2` — **2개 Sentinel이 동의**해서 객관적 다운 확정

**② 리더 선출**
- `+vote-for-leader` — Raft 스타일 리더 투표
- `+elected-leader` — 페일오버 지휘할 Sentinel 결정

**③ 승격**
- `+selected-slave 10.0.0.48:6379` — **replica-1을 새 마스터로 낙점**
- `+failover-state-send-slaveof-noone` — replica-1에게 `SLAVEOF NO ONE` 명령
- `+promoted-slave` — 승격 확정

**④ 나머지 replica 재구성**
- `+slave-reconf-sent` → `+slave-reconf-done` — replica-2가 새 마스터로 재편입

**⑤ 페일오버 완료 — 이력서 문구의 그 라인**
```
+switch-master mymaster 10.0.0.113 6379 10.0.0.48 6379
```
"클러스터 이름 `mymaster` 의 마스터를 `10.0.0.113:6379` → `10.0.0.48:6379` 로 공식 교체." 이 라인이 뜬 순간, 앱은 새로 열리는 클라이언트 연결부터 자동으로 새 마스터에 붙습니다.

#### 4-5. 무손실 검증

```bash hl:2,6
redis6-cli -p 26379 sentinel master mymaster | head -6
# "ip"    "10.0.0.48"     ← 마스터가 바뀜

redis6-cli -h 10.0.0.48 -p 6379 GET failover-test
# "before-failover"        ← ★ 페일오버 전 데이터 유지
```

**감지 → 승격 → 새 마스터 확정까지 총 5~10초.** `down-after-milliseconds`(5000ms) + Sentinel 간 협상 시간이 대부분이에요.

![[Pasted image 20260712045225.png]]

---

## Part 5. 죽인 마스터 되살리기 → 자동 slave 편입

AWS 콘솔에서 `sg-ha-master` 를 **인스턴스 시작**.

> <mark class="hltr-yellow">⚠ stop → start 하면 퍼블릭 IP가 바뀝니다.</mark> 사설 IP(`10.0.0.113`)는 그대로. 새 퍼블릭 IP로 SSH 재접속.

접속 후:

```bash hl:2-3
redis6-cli info replication
# role:slave                     ← 마스터에서 slave로 바뀜
# master_host:10.0.0.48          ← 새 마스터를 자동으로 따라감
# master_link_status:up
```

`psubscribe` 창에도 이 순간이 잡혔습니다:

```hl:3,5
+slave slave 10.0.0.113:6379 ... @ mymaster 10.0.0.48 6379
+sdown slave 10.0.0.113:6379 ...
-role-change slave 10.0.0.113:6379 ... new reported role is master  ← 재기동 직후 잠깐 master로 자기 주장
-sdown slave 10.0.0.113:6379 ...
+role-change slave 10.0.0.113:6379 ... new reported role is slave   ← Sentinel이 교정 → slave 확정
```

**해석**: 되살아난 옛 마스터는 자기가 마지막에 저장한 상태(master)로 시작하지만, Sentinel과 통신하면서 즉시 "지금 진짜 마스터는 10.0.0.48이야"라는 걸 알게 되고 **slave로 자동 강등**합니다. 사람 손이 전혀 필요 없어요.

Sentinel 프로세스는 재부팅으로 사라졌으니 다시 띄우기:

```bash
sudo redis6-server /etc/redis6/sentinel.conf --sentinel --daemonize yes
```

---

## Part 6. 다른 삽질 기록

로컬 도커에서는 안 보이던 것들:

#### SG self-reference 저장 실패

`sg-redis-ha` 의 6379/26379 인바운드에 소스로 자기 자신을 지정하려니:

> "기존 IPv4 CIDR 규칙에 참조된 그룹 ID을(를) 지정할 수 없습니다"

원인: **소스 검색창에 SG ID를 직접 타이핑하면 CIDR로 오해**함. 검색창을 클릭만 하고 **드롭다운에서 선택**해야 그룹 참조로 인식됩니다.

#### `.pem` 파일 이름이 계획서와 달랐음

계획서엔 `studygroup-ha-key.pem`, 실제 다운받은 건 `studygroup-ec2.pem`. Mac 전체 검색으로 찾음.

교훈: <mark class="hltr-yellow">`.pem` 파일은 생성 시점에만 다운로드 가능. 잃으면 인스턴스 재생성이 유일한 복구.</mark>

#### EC2 Instance Connect 실패

Innovation Sandbox의 SCP가 `ec2-instance-connect:SendSSHPublicKey` 를 차단. SG를 아무리 열어도 안 됨. `.pem` 파일 SSH가 유일한 접속 방법이었어요.

#### Heredoc 자동 들여쓰기 문제

`sudo tee ... <<'EOF' ... EOF` 로 파일 만들려니 터미널 붙여넣기가 각 줄 앞에 공백을 자동으로 넣어서 `EOF` 종료 인식 실패. 결국 **nano**로 통일.

---

## Part 7. 비용 & 정리

#### 실측 비용 (오늘 하루)

- t3.micro × 5 × 약 3시간 = 5 × $0.0104 × 3 ≒ **$0.16 (약 220원)**
- 데이터 전송/스토리지는 미미
- CloudFormation 자체는 무료

#### 정리는 스택 삭제 한 번으로

```
CloudFormation → studygroup-ha-stack → 삭제
```

5대 EC2 다 terminate. **네트워크 리소스(VPC/서브넷/IGW/SG/키페어)는 스택 밖이라 남음** — 다시 실습할 때 재사용 가능해요.

---

## Epilogue

핵심 인사이트 세 가지:

1. **HA는 "안 죽음"이 아니라 "죽어도 서비스 지속"이다.** 마스터가 진짜 죽었고, 5~10초 안에 다른 노드가 대신 마스터 자리를 이어받았다.
2. **Quorum 홀수 & 분산 배치가 중요하다.** Sentinel 3개를 한 노드에 몰아넣었다면 그 노드 죽을 때 quorum 붕괴로 페일오버 실패.
3. **되살아난 옛 마스터의 자동 강등이 우아하다.** 사람 개입 없이 slave로 편입되어 새 마스터의 데이터를 다시 복제받기 시작한다.

___
