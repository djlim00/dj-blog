컨테이너 : 프로세스를 가상화하기 위한 최소 단위

Docker는 유니온 파일 시스템을 쓴다는데,,
###### 유니온 파일 시스템 : 디렉토리들을 적층시켜서, 동일한 파일에 대한 수정이 있으면 전부 수정됨.

![[Pasted image 20250911092057.png]]
- lowerdir는 거의 읽기만 가능
- upperdir는 쓰기 가능 (주로 커스텀 되는 부분)


### <span style="background:#fff88f">Docker는 이걸 왜 쓸까?</span>

1. **저장 효율이 좋음**
   -> 동일한 파일을 여러번 큰 수정이 일어나는게 아니라면, 수정이 일어나도 바뀌지 않는 부분은 캐시잉 되어 있어서 메모리 효율적임
2. **단일 페이지 캐시**
3. **상대적으로 쓰기 작업이 느림(coW 방식과 동일)**


#### 알아 볼만한 파일 시스템
<mark style="background: #BBFABBA6;">xfs -> 메모리를 캐싱해서 가속화를 해서 파일 여러개를 읽어올 때 빠르게 가져올 수 있음
- 대신에 램을 많이 먹음</mark>
https://www.google.com/search?q=xfs&oq=xfs&gs_lcrp=EgZjaHJvbWUyBggAEEUYOdIBCDEzNzRqMGo3qAIAsAIA&sourceid=chrome&ie=UTF-8

___
### 명령어

#### open( , , , )

1. 읽기에서는 문제가 없음
2. 쓰기할 때는 lowerdir에서는 쓰기가 안되서, upperdir로 복사를 하고 수정을 하는 과정이 생김
	- 이 과정을 빠르게 하고 싶으면 touch를 이용해서(파일의 시간을 수정) -> 이 과정에서 파일을 한번 건드리면서 갱신값이 생기면서 즉시 upperdir로 이동되면서 속도에 이점이 있음

#### rename()
1. exdev 오류 : 동일한 파일 시스템이 아니면 rename()을 쓸 수가 없음
2. old path와 new path의 과점에서 upperdir와 lowerdir가 다른 마운트를 가지고 있어서 다른 파일 시스템이라고 인식을 해서 안될 때가 있음.

___

![[Pasted image 20250911092828.png]]

- 빌드를 할 때 보면 깃 처럼 달라진 부분들만 수정되어서 반영되는 것을 볼 수 있다
-> 즉 다른 부분들을 캐싱된 값을 사용함.

Docker 막 들어가면 Overlay2 들어가면 저렇게 무슨 커밋 내역 처럼 있는 것을 볼 수 있음.

___
# Dockerfile

- 예전에는 tar.xz 뭐 이런 걸로 압축 파일 형식으로 이미지를 저장했는데 dockerfile로 코드를 작성해 놓으면 이미지를 가져오기 편함.

#### Dockerfile 관련 명령어
![[Pasted image 20250911093914.png]]
- ADD 명령어 vs COPY 명령어
	- local 환경에서는 동일함
	- ADD는 원격에 있는 파일들도 바로 다운로드해서 넣을 수 있음.
	- COPY는 이게 local에 있을 때만 동작하기 때문에 별도로 local로 다운로드 받아서 넣어야함.



![[Pasted image 20250911095214.png]]
- 여기서 명령어 하나하나가, Overlay에서 레이어로 작용된다.
- 캐싱이 되면 안에 코드가 바뀌었는데 캐싱값이 사용되는 문제가 발생할 때가 있다.
	- --no--cache 옵션을 사용하면 된다.(무조건 처음부터 다시 빌드)


```java title:"Dockerfile"
# syntax=docker/dockerfile:1  
FROM ubuntu:22.04  
  
# install app dependencies  
RUN apt-get update && apt-get install -y python3 python3-pip  
RUN pip install flask==3.0.*  
  
# install app  
COPY app.py /  
  
# final configuration  
ENV FLASK_APP=app  
EXPOSE 8000  
CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000"]
```

좋아요! 지금 Dockerfile을 한 줄씩 뜯어서 **무슨 역할을 하는지, 왜 필요한지** 설명해드릴게요.

---

`# syntax=docker/dockerfile:1`

- Dockerfile의 문법 버전을 지정하는 라인입니다.
- 여기서는 Docker 공식 `dockerfile` 문법 버전 1을 사용한다고 명시한 거예요.
- 최신 기능(빌드 캐시, 멀티 스테이지 등)을 활용할 때 필요할 수 있습니다.

---

`FROM ubuntu:22.04`

- 베이스 이미지로 **Ubuntu 22.04**를 사용합니다.   
- 즉, 컨테이너 안에 기본 운영체제 환경이 Ubuntu 22.04로 세팅됩니다.
- Python, pip 등을 설치하려면 Linux 환경이 필요하기 때문에 베이스 이미지를 씁니다.    

---

`# install app dependencies RUN apt-get update && apt-get install -y python3 python3-pip`

- `RUN` 명령어는 컨테이너 이미지 빌드 과정에서 **명령을 실행**합니다.   
- 여기서는:
    1. `apt-get update` → 패키지 목록을 최신으로 갱신
    2. `apt-get install -y python3 python3-pip` → Python3와 pip 설치
- 즉, Flask 앱을 실행할 수 있는 Python 환경을 만들어주는 부분입니다.

---

`RUN pip install flask==3.0.*`

- Python 패키지 설치   
- Flask 3.0 버전을 설치합니다.
- `==3.0.*` → 3.0 계열 최신 버전을 설치하겠다는 의미
- 이 단계에서 Flask 앱을 실행할 수 있는 의존성을 확보합니다.

---

`# install app COPY app.py /`

- 로컬 디렉토리(`.`)에 있는 `app.py` 파일을 **컨테이너 루트 디렉토리(`/`)**로 복사합니다.
- 즉, Flask 애플리케이션 소스 파일을 컨테이너 안에 넣는 단계입니다.

---

`# final configuration ENV FLASK_APP=app`

- 환경변수 설정
- Flask는 `FLASK_APP` 환경변수에 **실행할 앱 모듈 이름**을 기대합니다.
- 여기서 `app` → `app.py` 모듈을 의미합니다 (Python 모듈 이름 기준, `.py` 제외).

---

`EXPOSE 8000`

- 컨테이너가 외부로 **어떤 포트를 열어두는지**를 선언
- 여기서는 Flask가 8000번 포트에서 실행될 예정이므로, 이 포트를 외부와 연결할 수 있도록 표시 
- 실제 포트 연결은 `docker run -p 외부:컨테이너`로 해야 합니다.


---

`CMD ["flask", "run", "--host", "0.0.0.0", "--port", "8000"]`

- 컨테이너가 실행될 때 **기본으로 실행할 명령어**를 지정
- Flask 앱을 실행하고:
    - `--host 0.0.0.0` → 컨테이너 외부에서도 접근 가능하게 함
    - `--port 8000` → 8000번 포트에서 서버 실행        

> CMD는 컨테이너가 시작될 때 실행되는 **프로세스**를 정의하며, 이 프로세스가 종료되면 컨테이너도 종료됩니다.

---

✅ **정리하면**:
1. Ubuntu 22.04 환경 구성
2. Python3 + pip 설치
3. Flask 설치
4. 앱 소스 파일(app.py) 복사
5. 환경변수 설정 (`FLASK_APP=app`)
6. 컨테이너 외부에서 접근 가능한 포트(EXPOSE 8000) 선언    
7. Flask 서버 실행 명령어 지정


즉, 이 Dockerfile로 빌드하면 **`docker run -p 8000:8000 flask-hello`만으로 Flask 앱이 8000번 포트에서 실행되는 컨테이너**를 만들 수 있습니다.



___

![[Pasted image 20250911100812.png]]

![[Pasted image 20250911101256.png]]
- Docker Registry를 pull 한다음에(5001번으로), 우분투를 나의 5001번(나의 local Registy)에 push한다.
- 중간에 tag를 붙일 때 내가 넣으려는 이미지의(여기서는 localhost:5001)을 명시한다.