![[Pasted image 20250909092549.png]]
- 레거시 시스템에서는 모든 조직이 하나의 시스템을 사용하지만
- Micro Architecture를 적용하면 각각의 시스템을 가지게 된다.

![[Pasted image 20250909092615.png]]
- <mark style="background: #BBFABBA6;">"아키텍처의 핵심은 모듈화다"</mark>
	- 같은 기능을 하는 것을 하나의 클래스로 만들던가
	- 아니면 하나의 모듈로 만들던가

### DDD(도메인 기반 디자인)
![[Pasted image 20250909092845.png]]
- 시스템의 도메인을 어떻게 나눌 것인가?
- 같은 기능(function)을 가지고 있는 기능들을 모으면 -> context bounded 된다.
	- 데이터가 공유되는 부분은 둘 사이에 존재하는 context가 생김 -> 이걸 어떻게 하면 제한할 수 있을까? (도메인별로 나누어져야 하기 때문이다.)



### EX) 온라인 스토어 예시
![[Pasted image 20250909093024.png]]
![[Pasted image 20250909093030.png]]
![[Pasted image 20250909093356.png]]
- <mark style="background: #BBFABBA6;">위와 같이 도메인을 나눈 다음에, context가 생기는 부분을 두고, 나머지는 각각의 도메인 별로 개발을 한다.</mark>
	- ex) Ordering 도메인에서만 customer의 정보를 가지고 있고, 이런 데이터들은 각자 가지고 있는 것이다.

- 예전에는 각 부서마다 시스템을 따로 만들었음(다른 웹 페이지) -> 다 다른 DB랑 서버를 두고 있음.



#### 하나의 UI에 대해서 마이크로 서비스를 만든 예시
![[Pasted image 20250909093418.png]]
- <u>기존 처럼 모든 부분 기능에 대한 팀이 존재하는 것이 아니라 -> 도메인 별로 팀을 만들어서 기술 개발을 한다.</u>


____
# 마이크로 서비스의 장점

1. 수정사항에 대해서 각각의 도메인 팀에서만 수정을 하면 되니까, 훨씬 쉽다.
	- 수정 이후에 CI/CD툴을 통해서 바로 배포가 가능하다.

<mark style="background: #BBFABBA6;">"우리는 Docker를 통해서 마이크로 서비스를 만드는 것을 배울 것이다."</mark>
-> Docker가 있기 때문에 가능해졌기 때문이다.

___
# 전통의 SOA vs MicroService
![[Pasted image 20250909093838.png]]
- **SOA : 2000년대 정도 부터 시작함**
	- 별도의 업체(회사)들을 하나로 통합 -> <mark style="background: #BBFABBA6;">보안이 굉장히 중요함</mark>
	- <mark style="background: #BBFABBA6;">범위가 큼</mark>
	- **<u>한 업체에서 수정되면 너무 분산 트랜잭션에 따른 롤백이 굉장히 복잡하고 큼</u>**


- **MicroService**
	- 각각의 서비스를 결합해서 -> <mark style="background: #BBFABBA6;">전부 동일한 회사 내이기 때문에 보안이 필요없음</mark>
	- <mark style="background: #BBFABBA6;">범위가 작음</mark>
	- **<u>상태를 유지할 수 있기 때문에 롤백이 쉬움</u>


![[Pasted image 20250909094520.png]]
- MicroService는 훨씬 심플하고
- 웹 기반 보안을 하고  
- 데이터 타입이 JSON으로 간단

___
# MicroService의 특징
![[Pasted image 20250909094639.png]]
- 수평적 슬라이싱 : 프엔, 백엔, 디비 -> 기술적으로 나눔

1. <mark style="background: #BBFABBA6;">수직적 슬라이싱 : 도메인별로 자름</mark> 을 시행함.
2. 한 도메인에 5~9명의 소규모 개발자
3. 하나의 팀으로 하나의 MicroService를 담당
4. 독립적임 -> 수정하고 바로 배포 가능
5. 하나의 팀이 모든 것을 처리할 수 있음(개발 -> 배포 -> 운영) DevOps(개발과 운영을 동시에)
6. 서비스의 재사용성이 높음
___
# MicroService의 국룰(표준)
![[Pasted image 20250909094924.png]]
- HTTP(s)를 사용 : 결론적으로는 모든 소통은 웹을 사용해라!
- UI로 REST로 만든다! : 정보를 주는 용도
- JSON : key-value로 알아서 해라(DB 안만든다!)


___
# SOA 스케일링의 한계 -> <mark style="background: #BBFABBA6;">이 부분은 GPT 물어보기</mark>

![[Pasted image 20250909095047.png]]
![[Pasted image 20250909095543.png]]



# MicroService의 스케일링은?
![[Pasted image 20250909095136.png]]
![[Pasted image 20250909095552.png]]

___
# The Challenge -> 도전과제!

![[Pasted image 20250909095958.png]]
- <mark style="background: #BBFABBA6;">그럼 각각의 서비스를 어떤 서버에 연결을 한 것인가?</mark>

![[Pasted image 20250909100200.png]]

![[Pasted image 20250909100233.png]]
"경우의 수.."

![[Pasted image 20250909100245.png]]
- <mark style="background: #BBFABBA6;">컨테이너라는 하나에 전부 넣을 수 있는 것을 만들자! -> 나르기가 쉬워짐 즉 배포(Deploy)가 쉬워짐!</mark>
- <span style="background:#fff88f">Docker는 개발 기술이 아닌 배포 Deploy 기술이다</span>

![[Pasted image 20250909100348.png]]
- Docker 기반으로 모든 것을 전부 컨테이너 기반으로 띄울 수 있다.
- Docker만 있으면 된다.

![[Pasted image 20250909100612.png]]

"한번 빌드하면 어디에서든지 실행할 수 있다."

![[Pasted image 20250909100647.png|500]]
- 모든 것을 Docker Container로!

___
# Docker란 무엇인가.

![[Pasted image 20250909101046.png]]
- Docker는 OS 레벨
- Hypervisor는 HAL Level임.
![[Pasted image 20250909101143.png]]
![[Pasted image 20250909101152.png]]
![[Pasted image 20250909101202.png]]


![[Pasted image 20250909101217.png]]
- Docker는 컨테이너라는 애플리케이션을 패키징하고 독립된 환경을 만듦.
- 한번에 여러개의 컨테이너를 돌릴 수 있음
- DB를 하나만 두고 여러개의 컨테이너에서 조회를 하는 식으로 시스템 구성이 되기 때문에 <mark style="background: #BBFABBA6;">가볍다</mark>.
	- hypervisor에서는 불가능함

___
# Docker vs VM
![[Pasted image 20250909101655.png]]
- Docker는 OS 밑에 Docker가 깔리고
- VM은 Hypervisor가 하드웨어에 올라오고 그 위에 각각의 OS를 올림.
	- 그럼 Hypervisor는 각각의 OS에 대해서 CPU 스케줄링을 해준다.
	- 네트워크 공유도 해준다.
	- GPU도 가상화
	- <mark style="background: #BBFABBA6;">대신 느려짐..</mark>
	  ![[Pasted image 20250909102333.png]]


![[Pasted image 20250909101932.png]]
![[Pasted image 20250909101949.png]]


___
# 컨테이너 기반의 가상머신(VM) - 짬뽕
![[Pasted image 20250909102057.png]]
- VM은 VCPU(가상 CPU), 가상메모리, VGPU(예전에는 그냥 공유했었는데.. 이제는 GPU가 중요해짐)
- Docker는 그냥 OS의 기능을 그대로 사용한다 -> Hypervisor가 개고생 안해도 됨.

<span style="background:#fff88f">그래서 요즘은 VM위에서 Docker를 사용한다 -> VM을 사용하는 오버헤드가 있어도 회사가 여러개라면 VM을 사용해서 각각의 독립된 OS를 제공하면서 그 위에서 Docker를 띄우는 방법을 선택함</span> 


___
# 왜 Docker 컨테이너는 가벼울까~

![[Pasted image 20250909102935.png]]
- 일단 컨테이너에는 OS를 가지고 있을 필요가 없음 -> 실행되는 컴퓨터의 OS를 사용하니까.
- 그림과 같이 기존의 App의 부분들을 가져올 수도 있고, 수정도 가능함.

___
# Docker 플랫폼이 제공하는 기능들
![[Pasted image 20250909103125.png]]
- 이미지로서 캡슐화가 됨
- 컨테이너는 띄우고 내리기가 너무 쉬움(협업이 쉬워짐)
- 배포가 쉬워짐

___
# Docker 플랫폼 아키텍처

![[Pasted image 20250909103306.png]]

- host에서는 이미지를 올릴 수도, 내릴 수도 있음.
	- 바로 띄울 수도 있고, 이미지를 변형해서 띄울 수도 있고
- 또 내가 올린걸 다른 플랫폼에서 가져와서 사용할 수도 있고.


# Docker 라이프 사이클(<font color="#ff0000">GPT</font>)

![[Pasted image 20250909103407.png]]
1. Docker Registry에서 이미지를 땡겨옴(우분투 기반)
2. Docker의 라이브러리에 새로운 lib(아파치)를 깔음
3. 이걸 Commit함(아파치가 깔린 상태로)
4. 이걸 Docker Conainer로 만듦
5. Container에 또 다른 라이브러리 같은 것을 깔음
6. 새로운 이미지가 됨
7. 그걸 pull해서 실행


![[Pasted image 20250909103656.png]]
![[Pasted image 20250909103724.png]]
- 커뮤니티도 활성화, 서드파티툴도 많고...

___
# DevOps란?

![[Pasted image 20250909103753.png]]

ex) Docker에서 땡겨오기 전에 그냥 VM으로 OS랑 Docker 깔고 땡겨오면 됨.
-> **필요한 시점에 VM만 만들어서 환경 구축해서 딱!**

![[Pasted image 20250909103407.png]]
-> <mark style="background: #BBFABBA6;">이걸 DevOps 관점에서 어떻게 진행되는 것인지 물어보기</mark>

<span style="background:#fff88f">AI가 요구사항에 맞게 Docker Image를 Verification을 하는 부분이 요즘 핫함</span>

