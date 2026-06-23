# 준비물

1. docker 설치
2. docker-compose.yml
3. 끝!

우선 docker 설치는 homebrew로 어디 잘 검색해보면서 하면 됩니다(윈도우는 알아서 Docker 설치방법 이런거 알아보쇼)

```java title:"docker-compose.yml 예시"
version: '3.8'  
  
name: arabyte-db  
  
services:  
  postgres:  
    image: postgres:latest  
    environment:  
      POSTGRES_USER: myuser  
      POSTGRES_PASSWORD: mypassword  
      POSTGRES_DB: arabyte-database  
    ports:  
      - "6789:5432"  
    volumes:  
      - postgres_data:/var/lib/postgresql/data  
  
volumes:  
  postgres_data:
```
- 도커 컨테이너를 만들어주는 docker-compose 파일입니다!
- 우리가 만들려는 것은 arabyte-db라는 컨테이너인데 -> 이게 이름이 바뀌더라구요?
	- <mark style="background: #FFF3A3A6;">이걸로 만드니까 arabyte-db-postgres-1 이렇게 만들어짐! docker 들어가서 확인하셈</mark>
- cmd창 들어가서 yml 파일 있는 곳 까지 가서 아래 명령어를 친다
![[Pasted image 20250313084457.png]]

그럼 이제 띠리리 하면서 도커에서 postgreSQL 컨테이너를 만들어줌. 우리가 할 건 이제 컨테이너를 실행시키고, 거기에 만들어져 있는(docket-compose에 이미 db의 이름, 유저, 비밀번호, 포트번호가 다 있어서 이미 만들어져 있음) db에 접속해보면 된다~

이제 datagrip에 들어가서 왼쪽 상단에 +해서 postgreSQL을 Data Source에 추가하고
![[Pasted image 20250313084634.png]]
이거 설정해주면 된다.

![[Pasted image 20250313084745.png]]
음하하 잘 연결된 모습

이제 이걸 나의 Spring 프로젝트에 연결을 해보자.

그리고 JPA도 쓸거니까 이것도 설정을 해줘야 한다.


