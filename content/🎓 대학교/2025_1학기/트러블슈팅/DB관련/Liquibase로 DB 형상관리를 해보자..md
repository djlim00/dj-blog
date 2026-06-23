# 1. Liquibase란 무엇인가?

- 형상관리,, 버전관리니 어려운 말들이 많은데.. -> <mark style="background: #FFF3A3A6;">그냥 DB의 Git임</mark>

 - **Liquibase를 써야하는 이유**
	1. 로컬 DB의 통일성을 유지하기 위해서
	2. JPA를 쓰기 때문에 -> @Entity 코드 자체가 테이블이자, 연관관계를 명시함
		- JPA Buddy가 이를 인식하고 changelog를 작성해줌

___
# 2. 우선 로컬 DB부터 만들어보자

- 기존 방식 : MySQL, MariaDB, PostGreSQL을 사용하면 각각 다운 받아서 설치하고 막 그래야함.
- 우리 방식 : DB를 직접 설치하지 않고 Docker에서 PostGreSQL을 띄워서 우리 로컬 DB로 사용한다.
	- 띄운다는게 정확히 뭔지는 Docker관련된 글을 보도록!(나도 잘 모름..컨테이너.. 이미지..)

## 2-1. docker-compose.yaml로 DB 띄우기

```java title:"docker-compose.yml"
name: uplait-db  // Container 이름
  
services:  
  postgres:  
    image: postgres:latest  // image -> 최신버전 PostgreSQL
    environment:  
      POSTGRES_USER: urecauser  // 로컬 DB user
      POSTGRES_PASSWORD: urecapassword  // 로컬 DB password
      POSTGRES_DB: uplait-database  // db이름
    ports:  
      - "6790:5432"  // 포트
    volumes:  
      - postgres_data:/var/lib/postgresql/data  // 잘 모르겠음
  
volumes:  
  postgres_data:
```

- 아래의 과정을 따르면 된다.
	- 우리 프로젝트의 docker-compose.yml에서 우클릭 -> Open In -> terminal
	- 거기서 `docker-compose up -d`
	- 그러고 나서 docker에 들어가면 ...

![[Pasted image 20250313084457.png]]
![[Pasted image 20250502170720.png]]
- 이 처럼 Container에 pinggu-db가 떠 있는걸 볼 수 있다.


## 2-2. 각자 사용하는 DB tool에 연결하기

- 나는 JetBrain사를 좋아하기 때문에 DataGrip을 기준으로 설명하겠다.(이것만 주구장창 써서 다른걸 잘 모름)

![[Pasted image 20250502170915.png]]
- 처음에는 아무것도 없는 화면
	- 왼쪽 상단에 `+` 버튼을 누른다.
	- `Data Source` -> `PostGreSQL`(다른 DB를 사용하면 그거에 맞게 고르면 됨)

![[Pasted image 20250502171047.png]]
- 그럼 이런 화면이 뜨는데 -> 여기에 우리가 Docker로 띄운 DB를 등록하면 된다.
`Name, Port, User, Password`를 우리가 위의 docker-compose.yml에 등록한 값을 넣어주면 된다.

현재 프로젝트의 경우는 
![[Pasted image 20250502171331.png]]
- password도 위에 있다.
- 그러고 이제 `Test Connection`을 눌러보면 
![[Pasted image 20250502171357.png]]
- 지금까지 잘 따라왔다면, 문제가 없어야 한다. -> 실패하면 Fail이 뜸
- 지금 위에 값이 뭔가 잘못됐는지, docker에 pinggu-db가 잘 떠 있는지 확인한다.


![[Pasted image 20250502171556.png]]
<span style="background:#ff4d4f">처음 만들면 이런 테이블이 없다!!</span>
-> 사실 당연하다 우리는 그냥 DB 스키마를 만들었지 그 어떤 CREATE도 하지 않았기 때문이다.

### 그럼 이제 이걸 하러 가자.

___
# 3.  드디어 다시 Liquibase로..

- 자 이렇게 로컬 DB는 위에서 봤듯이 사람이 만드는 것이다. 그러다 보니 각자 SQL문을 막 날려서 만들면 통일성이 전혀 지켜지지 않을 가능성이 100%다.
- <mark style="background: #FFF3A3A6;">그럼 이제 Liquibase를 이용해서 이걸 통일해보자.</mark>
## 3-1.  build.gradle에 liquibase 의존성 추가
![[Pasted image 20250502171942.png]]
- 걍 추가하면 된다.

## 3-2.  필요한 파일 추가
![[Pasted image 20250502172101.png]]

- `/docker/docker-compose.yml`  : 지금까지 주구장창 말했던 파일
- `/liquibase` : liquibase관련 파일 디렉토리
	- `/changelog` : 변경사항이 적힌 일종의 commit로그인 changelog가  저장되는 디렉토리
	- `changelog-master.yaml` :  changelog에 대한 설정파일
- `application.yml` : 다들 알다시피 설정파일 - profile 상관없이 언제나 참조되는 설정파일
	- `application-local.yml` : Spring의 profile이 local 때 추가적으로 참조하는 설정파일


```java title:"changelog-master.yaml"
databaseChangeLog:  
  - includeAll:  
      path: db/liquibase/changelog
```
- path 경로 아래에 있는 changelog를 보고 db를 만들겠다는 말임(우리는 거기 저장 중임)


```java title:"application.yml"
spring:  
  profiles:  
    active: local  
  liquibase:  
    change-log: classpath:db/liquibase/changelog-master.yaml  
    enabled: true
```
- 현재 profile을 local로 설정 -> 개발 환경이니까
- liquibase의 change-log 설정 파일의 경로를 명시 -> "Spring아 liquibase는 여기서 설정 확인해~"


```java title:"application-local.yml"
spring:  
  datasource:  
    driver-class-name: org.postgresql.Driver  
    url: jdbc:postgresql://localhost:6790/pinggu-database  
    username: urecauser  
    password: urecapassword
```
- 현재 profile인 local에서의 설정
- <mark style="background: #FFF3A3A6;">로컬 DB인 우리가 만든 pinggu-databse에 연결하기 위해서 </mark>
	- Spring / datasource 에서 설정을 해줌
- username, password는 보안을 위해 환경변수 설정하는게 좋지만, 뭐 털어갈 것도 없으니 그냥 명시해 놓음

___
# 4. 모든 설정 끝! 사용법

## 4-1. JPA Buddy 설치
- 인텔리제이 플러그인에서 검색해서 설치-> 활성화
- <mark style="background: #FFF3A3A6;">잘 안되면 껏다키기</mark>

![[Pasted image 20250502173236.png]]
- 설치가 잘 됐다면 Member나 Recruit 같이 @Entity가 붙은 엔티티 클래스들에 들어가면 
- 오른쪽에 JPA Buddy가 뜬다

## 4-2. changelog 자동 생성
- 드디어 핵심이..
![[Pasted image 20250502173340.png]]
- 왼쪽 상단에`+`을 누르면 `Liquibase Changelog..`가 있다.
- <span style="background:#ff4d4f">이게 이제 changelog를 자동 생성해준다!!!</span>

![[Pasted image 20250502173459.png]]
- 왼쪽 Source와 오른쪽 Target을 비교해서 변경사항을  changelog로 만들어준다.
- 오른쪽에 Select DB connection에는 아까 우리가 만든 pinggu-database를 연결한다
	- 대충 지금까지랑 비슷하게 하면 됨(그 DataGrip에서 설정하던거랑 동일)


![[Pasted image 20250502173615.png]]
- OK를 누르면 이렇게 변경사항이 나오고 XML로 changelog를 만들어줌
	- <mark style="background: #FFF3A3A6;">근데 가끔 정확하지 않을 수도 있어서 대충이라도 읽어봐야함</mark>
		- 예전의 변경이 살아나거나, 누락된게 들어가거나 할 수 있음..
- <mark style="background: #FFF3A3A6;">처음 설치해서 뭔가 다르다면 위의 사진과 동일하게 하면 된다.</mark>


# changelog 그냥 막 Save하다가 다른 사람 DB까지 이상해질 수 있으니까 확인 하기!!!🙉
-> 지금은 처음이라 그렇지 나중에 하나씩 수정하면 변경 사항이 그렇게 많지 않다.


![[Pasted image 20250502173829.png]]
- Save를 하면 이렇게 생기게 된다.
- <span style="background:#fff88f">이제 이걸 GIt으로 올리면 다른 사람도 변경된 DB를 서로 버전을 맞출 수 있게 된다!</span>



# Save하고 DB에 적용하기 위해서는 Spring 서버를 한번 돌려야한다.
![[Pasted image 20250502173921.png]]
한번 돌리고

![[Pasted image 20250502173935.png]]
한번 새로고침 버튼 누르면 변경사항이 테이블에 적용이 된다.

___
