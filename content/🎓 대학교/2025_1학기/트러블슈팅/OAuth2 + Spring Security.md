## 내부에서 `OAuth2AuthorizationRequest`는 어떻게 생성될까?

### 예를 들어 사용자가 다음 주소로 요청을 보내면:

pgsql

복사편집

`GET /oauth2/authorization/kakao?role=TMP_USER`

Spring Security 내부 동작 흐름:

1. `OAuth2AuthorizationRequestRedirectFilter`가 요청을 가로챔
    
2. `ClientRegistrationRepository`에서 `kakao` 등록 정보를 조회함  
    (→ 이게 `application.yml`의 `registration.kakao` 설정)
    
3. `OAuth2AuthorizationRequestResolver`가 이 정보를 바탕으로 `OAuth2AuthorizationRequest` 객체를 생성
    
4. 이 요청 객체를 `authorizationRequestRepository` (네가 만든 `HttpCookieOAuth2AuthorizationRequestRepository`)에 저장
    
5. 이후 카카오 인증 서버로 redirect됨




아니다 됐다. 내가 지금까지 배포하려고 했던 것들은 이제 없어. 그냥 다시 처음부터 시작하려고. 기존의 인스턴스들은 전부 삭제하려고 하는 중이야. 그래서 알려줄 때 기존에 ~가 있다면 삭제하고 진행해 이런걸 알려줘야해.

내가 생각하고 있는 방식은 전부 하나의 VPC안에 Spring 서버의 서브넷이 있고, DB의 서브넷이 있어. 그리고 추후에 python 서버가 추가될 것이야.

Spring은 public 서브넷이고, db는 프라이빗이야. Spring은 EC2에 띄울 것이고, DB는 RDS에서 Postgresql이고 postgis 확장모듈을 사용해.

Docker를 사용할 것이고, Github Actions를 이용해서 CI/CD 환경을 구축해서 main 브랜치에 머지가 되는 순간 배포가 되도록 하고 싶어.

이걸 위해서 어떻게 해야할지 차근차근 알려줘. 그리고 우리는 u-hyu.site라는 도메인을 이용할거야. 그리고 이전에 막혔던 부분은 쿠키(access token)가 넘어오지 않는 문제가 있었어 이런걸 감안해서 만들면 좋을 것 같아. 로드밸런서를 도입했던 기억이 있어. 아무튼 차근차근 알려줘.




### ✅ [1단계] VPC 및 네트워크 구성

**🎯 목표:** 하나의 VPC 안에 Spring(EC2) → Public Subnet, PostgreSQL(RDS) → Private Subnet 구성

1. **기존 VPC/Subnet/IGW/NATGW 등 있으면 전부 삭제**
    
2. **VPC 생성**
    
    - CIDR: `10.0.0.0/16` 등 넉넉하게
        
3. **서브넷 생성**
    
    - Public Subnet: `10.0.1.0/24` (Spring 서버용)
        
    - Private Subnet: `10.0.2.0/24` (RDS용)
        
4. **인터넷 게이트웨이(IGW) 생성 및 VPC에 연결**
    
5. **라우팅 테이블 구성**
    
    - Public Subnet 라우팅 테이블 → IGW 연결
        
    - Private Subnet 라우팅 테이블 → NAT Gateway 연결 (선택)
        
6. **NAT Gateway 생성 (필요 시)**
    
    - EC2에서 외부 접근이 필요하면 생성
        
7. **서브넷에 위 라우팅 테이블 연결**
    

---

### ✅ [2단계] RDS(PostgreSQL + PostGIS) 구성

1. **기존 RDS 있으면 삭제**
    
2. **RDS PostgreSQL 인스턴스 생성**
    
    - 엔진: PostgreSQL
        
    - 옵션 그룹에서 `postgis` 확장 모듈 활성화
        
    - VPC 선택: 위에서 만든 것
        
    - 서브넷 그룹: **Private Subnet으로 구성된 DB Subnet Group** 따로 생성
        
    - 보안 그룹 설정: EC2 IP만 5432 포트 열어주기
        
3. **RDS 접속 테스트**
    
    - 로컬에서 `psql` 또는 DBeaver 등으로 EC2의 퍼블릭 IP에서 포트 열어둔 경우만 테스트
        

---

### ✅ [3단계] EC2(Spring 서버용) 설정

1. **기존 EC2 삭제**
    
2. **새 EC2 인스턴스 생성**
    
    - AMI: Ubuntu 22.04
        
    - Subnet: **Public Subnet**
        
    - 보안 그룹:
        
        - 22번 포트 (SSH) → 본인 IP
            
        - 80, 443 포트 → 전체 허용 (로드밸런서용)
            
        - 8080 포트 → 로컬 개발용 또는 내부 테스트용만 열기
            
3. **Docker, Docker Compose, Git, OpenJDK 17 설치**
    
4. **Spring Boot 앱을 Docker로 빌드하고 docker-compose.yml 구성**
    

---

### ✅ [4단계] 도메인 연결 및 HTTPS 적용

1. **도메인: `u-hyu.site` → Route 53 설정**
    
    - 기존 호스팅 레코드 전부 정리
        
    - ALB 생성 후 Route 53에서 A레코드 연결 예정
        
2. *_ACM에서 인증서 발급 (u-hyu.site + _.u-hyu.site)__
    
3. **Application Load Balancer(ALB) 생성**
    
    - HTTPS (443) → Target Group (EC2 8080 포트)
        
    - HTTPS 리스너에 인증서 연결
        
    - Target Group health check 설정도 /health 등으로 구성
        

---

### ✅ [5단계] Github Actions 기반 CI/CD 구성

1. **`.github/workflows/deploy.yml` 작성**
    
    - main 브랜치에 머지되면 실행
        
    - `scp`, `ssh`로 EC2에 배포
        
    - Docker Compose 자동 실행 (`docker-compose down && up`)
        
2. **EC2에 GitHub Actions용 `SSH key` 등록**
    
    - GitHub → Deploy Key 등록
        
    - EC2 → `~/.ssh/authorized_keys` 등록
        

---

### ✅ [6단계] Spring Boot - 쿠키 인증 문제 대응

1. **JWT 쿠키 → `SameSite=None`, `Secure`, `HttpOnly` 모두 적용**
    
2. **CORS 설정: 프론트 도메인 (`https://{프론트}`) 허용 + `allowCredentials(true)` 필수**
    
3. **프론트 요청 시 `withCredentials: true` 설정**


___

## 1단계: 로컬에서 Git 커밋 & 푸시

### (1) staged 상태 확인

이미 `Dockerfile`, `docker-compose.yml`은 add된 상태이고 수정사항도 존재하네요. 아래 순서대로 처리하세요:

`git add Dockerfile docker-compose.yml git commit -m "feat: 배포용 Dockerfile 및 docker-compose.yml 추가" git push origin CHORE/UHYU-70-Back-deploy-setting`

> ✨ `Dockerfile`, `docker-compose.yml`의 위치가 루트면 경로는 `./` 기준으로 입력하세요. (`../../..` 아님)

---

## ✅ 2단계: EC2에서 Git Pull

EC2에 이미 해당 저장소가 클론되어 있다면 아래와 같이 진행하세요:


`cd /home/ubuntu/<your-project-dir> git checkout CHORE/UHYU-70-Back-deploy-setting git pull origin CHORE/UHYU-70-Back-deploy-setting`

> 📌 폴더가 없다면 `git clone`부터 해야 해요:


`git clone <YOUR_REPO_URL> cd <your-project-dir> git checkout CHORE/UHYU-70-Back-deploy-setting`

---

## ✅ 3단계: .env 파일 준비

로컬 `.env` 파일은 **절대 커밋하면 안 되므로**, EC2에 수동으로 생성해야 해요:

`nano .env`

그리고 아래 내용을 붙여넣기:


`SPRING_PROFILES_ACTIVE=prod  SPRING_DATASOURCE_URL=jdbc:postgresql://uhyu-postgis-db.cfcck8wgq9yu.ap-northeast-2.rds.amazonaws.com:5432/postgres SPRING_DATASOURCE_USERNAME=postgres SPRING_DATASOURCE_PASSWORD=aa15113988!!  JWT_SECRET_KEY=acc932b1902cab0531a268b8df91b8810d26eaddf91badae8602e71b3c910819d18b832f7ba83a3688e6fddc335668432abfa0702a13565eb35d71177bc7df6b ACCESS_TOKEN_EXP=3600000 REFRESH_TOKEN_EXP=86400000  KAKAO_REST_API_KEY=939764722fa99561f1cf6eb250fb6a8d FRONT_BASE_URL=https://u-hyu.site`

---

## ✅ 4단계: Docker 이미지 빌드 & 실행

docker build -t uhyu-backend 
docker-compose up -d

---

## ✅ 5단계: 컨테이너, 로그 확인

`docker ps docker logs -f uhyu-backend`

---

## ⏭️ 다음 단계

- Spring Boot가 잘 뜨면 프론트와 연동 테스트 시작
    
- GitHub Actions 통한 자동 배포(CI/CD)는 이 다음에 구성



정확해요, 바로 그거예요! 👇

---

## ✅ 에러 원인 요약


`COPY build/libs/*.jar app.jar`

이 줄은 `build/libs/` 디렉토리에 `.jar` 파일이 존재해야 Docker가 그 파일을 이미지에 복사할 수 있다는 뜻인데,  
현재 그 경로에 `.jar` 파일이 없어서 **"no source files were specified"** 에러가 발생한 거예요.

---

## ✅ 해결 방법

### 1. Spring Boot 프로젝트 빌드 먼저 하기 (EC2 안에서)


`./gradlew clean build`

- 이 명령은 `build/libs/` 경로에 `your-app-name.jar` 파일을 생성합니다.
    
- `.jar` 파일이 생기면 `docker build`가 성공하게 돼요.
    

빌드가 완료되면 다음과 같이 확인해보세요:

`ls build/libs`

> ✅ `.jar` 파일이 있다면 OK입니다.

---

### 2. 그 후에 Docker 이미지 빌드

`docker build -t uhyu-backend .`
	
---

## 🔧 추가 팁: `.jar` 이름이 다를 경우

생성된 `.jar` 이름이 다를 수 있으므로, 아래처럼 Dockerfile에서 명시적으로 이름 지정해도 됩니다:

`COPY build/libs/uhyu-0.0.1-SNAPSHOT.jar app.jar`

---

작업하시다가 `build 실패`, `OutOfMemory`, `권한 문제` 등이 있으면 알려주세요. 바로 도와드릴게요!



### 권한주기
- <mark style="background: #BBFABBA6;">chmod +x ./gradlew</mark>

### 테스트 빼고 빌드
- <mark style="background: #BBFABBA6;">./gradlew clean build -x test</mark>

### 로그보기
- sudo docker-compose logs -f

### Docker 서버 띄워져 있는지 확인하기
- <mark style="background: #BBFABBA6;">docker ps</mark>

### RDS 접속 
- psql -h <RDS-엔드포인트> -U <postgres-유저> -d <DB이름> -p 543 2
- psql -h uhyu-db.cha0m0sw0ayx.ap-northeast-2.rds.amazonaws.com -U postgres -d uhyu-db -p 5432

```
ubuntu@ip-10-0-1-157:~$ psql -h uhyu-postgis-db.cfcck8wgq9yu.ap-northeast-2.rds.amazonaws.com -U postgres -d postgres
Password for user postgres: 
psql (14.18 (Ubuntu 14.18-0ubuntu0.22.04.1), server 17.4)
WARNING: psql major version 14, server major version 17.
         Some psql features might not work.
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
Type "help" for help.

postgres=> CREATE EXTENSION postgis;
CREATE EXTENSION
postgres=> \dx
                                List of installed extensions
  Name   | Version |   Schema   |                        Description                         
---------+---------+------------+------------------------------------------------------------
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
 postgis | 3.5.1   | public     | PostGIS geometry and geography spatial types and functions
(2 rows)

postgres=> 
```



### 로컬 -> EC2 -> RDS를 SSH로 연결하기
참고 링크 : https://eight20.tistory.com/109



http://ec2-52-79-206-58.ap-northeast-2.compute.amazonaws.com:8080/




### 중간 작업 플로우
1. ALB 생성 (ACM 인증서 연결 포함)
2. ALB → EC2 타겟 그룹 연결 (포트 8080)
3. 도메인 u-hyu.site → ALB에 연결 (Route53 or 가비아 DNS)
4. Spring Boot CORS 설정에서 HTTPS 도메인 허용
5. 프론트에서 API URL을 https://u-hyu.site로 수정
6. 프론트 재배포 (필요시 Owner 계정에서 새로 배포)




## ✅ 전체 빌드 & 재배포 순서

### 1. **기존 컨테이너 정리**

bash

복사편집

`cd ~/U-Hyu-be  # 루트 디렉토리로 이동  # 컨테이너 중지 및 삭제 sudo docker-compose down  # 혹시 컨테이너 남아 있으면 강제로 정리 sudo docker rm -f $(docker ps -aq)  # 사용 중인 이미지도 정리 (선택) sudo docker rmi -f $(docker images -q)`

---

### 2. **build 디렉토리 수동 삭제**

Gradle이 잘 못 지우는 경우가 있으니 수동 삭제해줘야 해:

sudo rm -rf ./build

---

### 3. **Gradle 새로 빌드**

./gradlew clean build -x test

빌드 성공하면 build/libs/ 아래에 `app.jar` 또는 비슷한 jar가 생김.

---

### 4. **docker-compose로 재배포**


sudo docker-compose up -d

- `--build`: Dockerfile 기반 이미지 새로 생성
    
- `-d`: 백그라운드 실행
    

---

### 5. **확인**

- 로그 확인:
    

sudo docker-compose logs -f

- 정상 응답 확인:
`curl http://localhost:8080/`

---

필요하다면 Dockerfile이나 `docker-compose.yml`도 확인 도와줄게.  
혹시 빌드 후에도 `/` 안 뜨면, `IndexController`가 포함된 `.jar` 내부도 체크해야 함.



## 지금 구조 기준 정리

### 🔷 인증서 (ACM)

- `u-hyu.site`, `*.u-hyu.site` 두 도메인에 대해 발급 완료됨 → ✅ OK
    
- ALB에 이 인증서 연결했으므로 `https://api.u-hyu.site`도 안전하게 사용 가능
    

---

## ✅ 프론트엔드 입장에서의 API 요청

프론트는 Vercel에 배포되어 있고, 유저가 접속하는 도메인은:

`https://www.u-hyu.site`

프론트에서 API 요청할 때는 아래처럼:

`// 예시: 로그인 후 사용자 정보 요청 fetch("https://api.u-hyu.site/api/user/me", {   method: "GET",   credentials: "include", // 쿠키 필요 시   headers: {     "Authorization": "Bearer ...", // JWT 방식이라면   }, });`

👉 **`https://api.u-hyu.site`로 백엔드 요청이 날아감**

---

## ✅ 사용자 입장에서 보는 URL

- 유저는 브라우저에서 `https://www.u-hyu.site/map` 이런 주소로 접근함
    
- 화면은 프론트에서 렌더되고, 그 안에서 API는 **`api.u-hyu.site`로 통신**
    

---

## ✅ 도메인 구성 정리

|도메인|사용 용도|연결 대상|
|---|---|---|
|`www.u-hyu.site`|프론트 (React/Vercel)|Vercel (CNAME)|
|`api.u-hyu.site`|백엔드 API(Spring Boot)|ALB (A레코드)|

---

## ✅ 반드시 필요한 CORS 설정 (Spring 쪽)

프론트가 `www.u-hyu.site`, 백은 `api.u-hyu.site`이므로 CORS 설정 필요:

java

복사편집

`@Configuration public class WebConfig implements WebMvcConfigurer {     @Override     public void addCorsMappings(CorsRegistry registry) {         registry.addMapping("/**")             .allowedOrigins("https://www.u-hyu.site")             .allowedMethods("GET", "POST", "PUT", "DELETE")             .allowCredentials(true);     } }`

---

## ✅ 쿠키 사용 시 주의

Spring에서 JWT Access Token을 쿠키로 발급하고 있다면:

- `Set-Cookie` 헤더에 `Domain=api.u-hyu.site; SameSite=None; Secure` 필수
    
- 프론트는 `fetch` 요청에 `credentials: 'include'` 설정 필요
    

---

## 🔚 정리: 프론트/백 요청 도식화

text

복사편집

`[ 브라우저: https://www.u-hyu.site/map ]        ↓        Vercel 프론트엔드 앱        ↓ API 요청 [ https://api.u-hyu.site/api/recommend ]        ↓        ALB (HTTPS → HTTP)        ↓        Spring Boot @ EC2        ↓        응답 반환`

---

필요하면 `Route 53`의 A 레코드, ALB 도메인, 프론트 배포 CNAME 설정까지 체크해드릴게요.  
계속 이어서 도와드릴 준비돼 있어요!