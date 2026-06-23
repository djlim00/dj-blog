# 😀DevOps의 개념

![[Pasted image 20250916092053.png]]

### DevOps Process
![[Pasted image 20250916092106.png]]

### DevOps 툴
![[Pasted image 20250916092127.png]]
- <span style="background:#fff88f">이 과정이 끊임없이 반복될 수 있도록 하는 것이 데브옵스이다.</span>

### 막힘없이 계속해서 이어지는 싸이클
![[Pasted image 20250916092323.png]]
- 애자일 방법론과 굉장히 잘 맞는 방법이다.

___
![[Pasted image 20250916092401.png]]
- <span style="background:#fff88f">깃에 올려서 push하면 CI 서버가 이걸 실행해서 Test를 돌리고 에러가 없으면 main브랜치에 merge되고 main에 merge되면 바로 배포에 들어갈 수 있도록</span>

- **Infrastruture as Code** : 소프트웨어를 만드는 모든 과정이 Code이다.(코드로 머신도 생성하고, 서버에 배포되서 사용할 수 있는 구조)
-  **Continuous integration** 
- **Automated testing** 
- **Application Performance Monitoring / Management** 
- **Continuous Deployment / Delivery** 
- **Release Management** 
- **Configuration Management**


#### 관련 자료
![[Pasted image 20250916092747.png]]

___

# 빠르다!
![[Pasted image 20250916092818.png]]

# 반응형 배포 및 스케일링!
![[Pasted image 20250916092832.png]]
- 자동으로 merge를 감지하고 배포가 된다.
- 요청에 따른 오토 스케일링도 가능하다.

# 같은 하드웨어에서 여러 OS(프로그램)를 돌릴 수 있다!
![[Pasted image 20250916092844.png]]
- 같은 machine에서 같은 OS를 공유


# 단점! - 기반 컴퓨터가 해킹 당하면 모든 컨테이너가 털림
![[Pasted image 20250916093026.png]]
- 하이퍼바이저 기반 보다는 Docker가 독립성이 적기 때문에 하나 털리면 다 털림(보안성이 안좋음..)

___

# 😎 Docker 아키텍처

![[Pasted image 20250916093251.png]]

![[Pasted image 20250916093405.png]]
- 컨테이너 : CPU(프로세스) 관리, 메모리
- 네트워크
- Data Volumn(파일 시스템)

# 0. Docker Engine

- daemon process 즉 항상 뒤에서 돌아가는 서버임
- REST API로 서버에 요청을 보내면 행동을함
- CLI에서 REST API를 쏘거나 docker daemon에게 지시를 내림(명령어로)


# 1. Docker Image

![[Pasted image 20250916093630.png]]
- 도커 컨테이너를 만들고 동작하게 하기 위한 read-only file
- ex) 우분투 이미지, 아파치 서버 이미지 -> 일종의 Layer를 가지고 있음.

#### <mark style="background: #BBFABBA6;">Union file system - Docker가 사용함</mark>
![[Pasted image 20250916093754.png]]
- 보면 fileC가 중복되기 때문에 두번 쓰지 않는다 -> writeable한 파일(DiscC)로 마운트 한다.
- 밑에 있는 파일을 write하고 싶으면 Disc3로 복사해서 거기서 수정하는 과정이 생긴다.

![[Pasted image 20250916094122.png]]

#### 1. Mount(마운트)의 기본 의미
- **운영체제(OS)에서 mount란**:  
    디스크(파일 시스템)를 특정 경로(예: `/mnt/data`)에 연결해서, 그 안에 있는 파일을 **내 로컬 디렉터리처럼 접근할 수 있게 만드는 것**이에요.
    
예시:
`mount /dev/sdb1 /mnt/data`
- `/dev/sdb1` → 디스크 장치
- `/mnt/data` → 마운트 포인트 (접근할 경로)
이렇게 하면 `/mnt/data` 폴더에 들어가면 그 디스크 내용을 볼 수 있게 됩니다.

#### 2. Docker에서의 Mount
Docker도 이 개념을 씁니다.
- 여러 개의 레이어(읽기 전용 이미지 레이어들 + 하나의 writable 레이어)를 **Union File System**을 이용해서 **하나의 디렉터리에 마운트**합니다.
- 즉, 컨테이너 안에서 `/` (루트 디렉터리)를 보면, 사실은 여러 레이어가 합쳐져서 보이는 거예요.
#### 3. 왜 마운트라고 부르는가?

- 이미지의 각 레이어는 독립된 파일 시스템(디렉터리 구조)입니다.
- Docker는 이를 그대로 보여주는 게 아니라, **Union File System을 통해 겹쳐서 하나의 디렉터리에 붙여놓습니다.**
- 이 과정이 바로 “마운트”예요.

즉,
- `Layer 1` (Ubuntu)
- `Layer 2` (Apache)
- `Layer 3` (설정 파일)
- `Writable Layer` (변경사항)

👉 이 네 가지 파일 시스템을 하나로 합쳐서 컨테이너 안에서는 `/` 루트 파일 시스템처럼 보이게 마운트합니다.
## ## 4. 예시 (그림 없이 설명)

- `/dev/d1` → `fileA`, `fileC`
- `/dev/d2` → `fileB`, `fileC`
- `/dev/d3` → writable (여기서 수정 발생)
UnionFS는 이들을 `/mnt`에 마운트 → 컨테이너 안에서는 `fileA`, `fileB`, `fileC`가 모두 있는 것처럼 보임.
- 만약 `fileB` 수정 → `/dev/d3` (writable)에 복사 후 수정됨.

![[Pasted image 20250916094309.png]]
- <span style="background:#fff88f">이렇게 requirements.txt에 깔아야하는 것들을 <u>코드로 만들고</u> 환경을 작성을 해서 실행시키면 된다</span>

___
# 📚Docker 튜토리얼 책 PDF

[[Docker공식 튜토리얼.pdf]]

___

# 2. Docker Container

![[Pasted image 20250916094658.png]]
- 하나의 리눅스 인스턴스에서 여러개의 독립된 리눅스 커널을 이용할 수 있도록 함.
	- 가상 머신 보다는 가벼움
- Docker image로 만든 실행가능한 인스턴스
	- stop, run, start, move, delete 가능
	- OS 이외의 환경 구성을 위해 필요한 모든 것이 있음(ex. 라이브러리)

- <mark style="background: #BBFABBA6;">UnionFS를 이용해서 컨테이너가 띄워지면 read-write가 가능한 Layer가 생김</mark>

- <span style="background:#fff88f">container는 process다</span> -> process counter가 메모리를 할당을 해야함
	- 프로그램을 page 단위로 가져와서 pc counter 한줄한줄 실행을 시킨다.
	- <span style="background:#fff88f">즉 CPU와 메모리를 할당 받음</span>

**ex)**
<font color="#ff0000">Infra</font> -> **(Platform/)** <font color="#ff0000">OS -> JVM -> APP(Spring Framwork)</font> **(/Platform)** ->**(POJO/)**<font color="#ff0000"> JAVA코드</font> **(/POJO)**


# 3. Docker Registry / Hub

![[Pasted image 20250916100018.png]]
- 이미지들의 모음
- public이나 private일 수 있음

https://hub.docker.com/

___

# Docker 명령어

![[Pasted image 20250916100106.png]]

<span style="background:#fff88f">과정 : Dockerfile ->(Build) Docker Image ->(Run) Docker Container</span>

- 빌드하고
- 포트포워딩하고
- docker ps로 프로세스 리스트 확인


# 어떻게 동작하나?

![[Pasted image 20250916100445.png]]

- 만약에 우분투가 이미 깔려있는데 새로운 버전을 가져오면 UnionFS 이기 때문에 바뀐 부분만 가져와서 새로 깔음


## 컨테이너를 실행하면 어떤 일이 일어날까?

**1. Ubuntu 이미지를 가져옴 (Pulls the ubuntu image)**
- Docker Engine은 우선 로컬에 Ubuntu 이미지가 있는지 확인합니다.
- 만약 로컬에 이미지가 있으면 그대로 사용하고, 없다면 Docker Hub에서 다운로드(pull)합니다.

**2. 새로운 컨테이너 생성 (Creates a new container)**
- Docker는 해당 이미지를 이용해 새로운 컨테이너를 만듭니다.

**3. 파일 시스템을 할당하고 읽기-쓰기 레이어를 마운트 (Allocates a filesystem and mounts a read-write layer)**
- 컨테이너는 파일 시스템 안에서 생성되고, 그 위에 읽기-쓰기 가능한 레이어가 추가됩니다. 

**4. 네트워크 / 브리지 인터페이스 할당**  
- Docker 컨테이너가 로컬 호스트와 통신할 수 있도록 네트워크 인터페이스를 생성합니다.

**5. IP 주소 설정**  
- 사용 가능한 IP 주소를 풀에서 찾아 컨테이너에 할당합니다.

**6. 지정한 프로세스 실행**  
- 사용자가 지정한 프로세스를 실행합니다. (예: `/bin/bash` 실행)

**7. 애플리케이션 출력 캡처 및 제공**  
- 표준 입력, 출력, 에러를 연결하고 기록하여 애플리케이션이 어떻게 동작하는지 확인할 수 있게 해줍니다. (특히 인터랙티브 모드를 요청했을 때)


![[Pasted image 20250916101209.png]]
- 가져오려는 부분을 Dockerfile에 정의된대로 Docker Enging의 UnionFS에 올려서 사용할 수 있게 된다.
- <span style="background:#fff88f">쿠버네티스까지 깔게되면 Docker conatiner는 Pot이라고 부르면서 해당 Pot을 생성, 증가, 종료, 삭제 시킬 수 있게된다.</span>

___

# Docker 내부의 기술들

![[Pasted image 20250916102514.png]]

# Union File System을 이용한 Docker FS
![[Pasted image 20250916102712.png]]
![[Pasted image 20250916102742.png]]

## DockerFS의 Copoy-on-Write
![[Pasted image 20250916102809.png]]
![[Pasted image 20250916102931.png]]


## 1. 기본 개념

- Docker는 **리눅스 커널(Linux kernel)**이 제공하는 기능을 활용해서, 하나의 운영체제 위에서 여러 개의 **독립된 컨테이너(container)**를 실행할 수 있습니다.
- 즉, **가상머신(VM)처럼 무겁게 새로운 OS를 올리는 게 아니라**, 같은 커널을 공유하면서도 각각이 격리된 환경을 갖게 하는 기술이에요.
- 이렇게 하면 VM보다 훨씬 가볍고 빠르게 실행할 수 있습니다.
## 2. 핵심 기술 두 가지

### 🔹 Namespaces (네임스페이스, Linux 2.4.19부터, 2002년)
- 역할: <span style="background:#fff88f">**격리(isolation)**</span>
- 애플리케이션이 바라보는 운영체제 환경을 분리해 줍니다.
- 격리되는 항목:
    - **프로세스 트리** (다른 컨테이너의 프로세스는 보이지 않음)
    - **네트워크** (컨테이너별로 독립적인 네트워크 인터페이스)
    - **사용자 ID** (컨테이너 안에서는 root여도, 실제 호스트에서는 일반 사용자일 수 있음)
    - **파일 시스템 마운트** (각 컨테이너마다 다른 루트 파일시스템을 볼 수 있음)

👉 즉, 네임스페이스 덕분에 컨테이너끼리 서로 간섭하지 않고 마치 독립된 서버처럼 보이게 됩니다.

### 🔹 cgroups (Control Groups, Linux 2.6.2부터, 2007년)

- 역할: <span style="background:#fff88f">**자원 제어(resource limiting)**</span>
- 컨테이너마다 CPU, 메모리, 디스크 I/O, 네트워크 사용량을 제한할 수 있습니다.
- 예를 들어:
    - 어떤 컨테이너가 CPU 1코어 이상 못 쓰게 제한
    - 메모리 512MB 이상 못 쓰게 제한
    - 디스크 읽기/쓰기 속도 제한

👉 cgroups 덕분에 특정 컨테이너가 시스템 전체 자원을 독식하는 걸 막고, 공평하게 자원을 배분할 수 있습니다.


# Namespace

![[Pasted image 20250916103216.png]]
![[Pasted image 20250916103223.png]]


# Cgroups(Control groups)
![[Pasted image 20250916103341.png]]
- 컨테이너의 자원 사용량을 제한


- <mark style="background: #BBFABBA6;">사실상 보안성은 리눅스가 Isolation을 보장하는 만큼만 해줌 -> 리눅스가 뚫리면 다 뚫림</mark>


___

# Docker의 추가적인 추상화

![[Pasted image 20250916103841.png]]
1. libvirt : vmware에서 가상머신을 지원하기 위한 라이브러리의 모음임 -> 동일하게 Docker가 지원함
2. LXC(리눅스 컨테이너) : 리눅스의 컨테이너 접근 
3. systemd-nspawn : 잘 모르심..
4. libcontainer : Docker 회사에서 만든 라이브러리

![[Pasted image 20250916104051.png]]
- libvirt도 벌써 많은 것을 지원함

___

# 마무리

![[Pasted image 20250916104136.png]]
![[Pasted image 20250916104142.png]]
