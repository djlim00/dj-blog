정답해설 카페 : https://cafe.naver.com/sqlpd

![[Pasted image 20251112200827.png]]

# 1. 제1정규형 (1NF: First Normal Form)

## ✔ 정의

- **모든 속성의 값이 원자값(Atomic value)이어야 한다.**
- 즉, **반복되는 그룹(다중값 속성)이 있으면 안 된다.**

## ✔ 쉽게 말하면

“하나의 칼럼(속성)에 **한 개의 값만** 넣어라.”

## ✔ 위반 예 (비정규형)

|학생|연락처|
|---|---|
|홍길동|010-2222-3333, 010-4444-5555|

- 연락처가 2개 → 다중값 → 1NF 위반

## ✔ 해결(1NF 준수)

|학생|연락처|
|---|---|
|홍길동|010-2222-3333|
|홍길동|010-4444-5555|

또는
**학생 - 학생전화번호(1:N)** 로 엔터티 분리

## ✔ 시험 포인트

- 핵심 단어: **원자값**, **반복그룹 제거**, **다중값 속성 X**
- “전화번호 여러 개”, “복수 주소” → 무조건 1NF 위반

# 2. 제2정규형 (2NF: Second Normal Form)

## ✔ 정의

- **부분 함수 종속(Partial Dependency)을 제거한 상태**
- 즉, **기본키가 복합키일 때**,  
	    <font color="#ff0000">기본키  일부에만 종속되는 속성을 없애야 함.</font>

## ✔ 쉽게 말하면
“**복합키 일부에만 의존하는 속성**을 분리하라.”

## ✔ 문제 예시 (1NF는 만족하면서 2NF 위반)

|(학생ID, 과목ID)|과목명|
|---|---|
|1, A|데이터베이스|
|1, B|알고리즘|

여기서
- PK = (학생ID, 과목ID) → 복합키
- <font color="#ff0000">과목명은 과목ID에만 종속  </font>
    → **부분 함수 종속** 발생 → 2NF 위반

## ✔ 해결

**과목 엔터티로 분리**

1. 수강
- 학생ID
- 과목ID

2. 과목
- 과목ID
- 과목명
## ✔ 시험 포인트
- “기본가 복합키일 때만 문제됨”
- “부분 함수 종속 제거 = 2NF”

# 3. 제3정규형 (3NF: Third Normal Form)

## ✔ 정의
- **이행적 함수 종속(Transitive Dependency)을 제거한 상태**
- 비키 속성이 다른 비키 속성에 종속되면 안 됨.

## ✔ 쉽게 말하면

“키가 아닌 속성이 **다른 키가 아닌 속성**을 결정하면 안 된다.”

## ✔ 문제 예시 (2NF는 만족, 3NF 위반)

|학생ID(PK)|학과ID|학과명|
|---|---|---|
|1|C001|컴퓨터공학|
|2|C002|기계공학|

- PK = 학생ID
- 학과명은 학과ID에 종속  
    → 학생ID → 학과ID → 학과명  
    → **이행적 종속** → 3NF 위반

## ✔ 해결
1. 학생
- 학생ID
- 학과ID

2. 학과
- 학과ID
- 학과명
## ✔ 시험 포인트

- “이행적 종속 제거 = 3NF”
- 3NF는 “**비키 → 비키 종속 금지**”

# 4. 보이스–코드 정규형 (BCNF: Boyce–Codd Normal Form)

## ✔ 정의

- **모든 결정자가 후보키(Candidate Key)이어야 한다.**
- 3NF보다 더 엄격한 조건.

## ✔ 쉽게 말하면

“결정자(→ 왼쪽 값)가 되려면 반드시 후보키여야 한다.”

## ✔ 어떤 경우에 3NF는 만족하지만 BCNF는 위반?

→ **복합키가 여러 개** 있는 경우 발생.

## ✔ 예시 (3NF는 OK, But BCNF는 위반)

|(교수, 과목)|강의실|
|---|---|
|김교수, DB|101|
|박교수, OS|202|

규칙:
- **한 과목은 한 강의실에서만 진행된다.**  
    → 과목 → 강의실  
    → 과목이 결정자  
    → 과목은 후보키 아님  
    → **BCNF 위반**
## ✔ 해결

엔터티 분리:
1. 과목–강의실
- 과목
- 강의실
2. 교수–과목
- 교수
- 과목

## ✔ 시험 포인트
- “모든 결정자가 후보키인가?” → YES = BCNF
- “결정자 중 후보키가 아닌 것이 있다” → BCNF 위반
- SQLD에서 자주 나오는 문장:
    - **“결정자는 반드시 후보키!”**

# ✅ 제4정규형(4NF: Fourth Normal Form)

## ✔ 핵심 개념

- **다중값 종속(Multi-Valued Dependency, MVD)을 제거하는 단계**
- 1행이 **여러 개의 다중 속성 조합**을 가진 경우,  
    이를 각각 독립된 엔터티로 분해하는 것.

## ✔ 왜 필요한가?

- 한 테이블에서 서로 **독립적인 두 개의 다중값 속성**을 함께 보관하면  
    → 중복 데이터 폭발  
    → INSERT/DELETE/UPDATE 이상현상 발생

### 예시로 바로 이해해보자

## 🔥 예시(비정규 상태)

한 학생은
- 여러 개의 **전공(major)** 을 가질 수 있고
- 여러 개의 **자격증(cert)** 도 가질 수 있다고 하자.

이를 하나의 테이블에 넣으면:

|student|major|cert|
|---|---|---|
|A|컴퓨터|정보보안|
|A|컴퓨터|SQLD|
|A|영어학|정보보안|
|A|영어학|SQLD|

→ 전공 X 자격증 **모든 조합이 생겨버림**  
→ 엄청난 중복 발생 (조합 수 = 전공 수 × 자격증 수)

## ✔ 이상현상

- **삽입 이상**: 전공만 추가하고 싶은데 자격증도 입력해야 함
- **삭제 이상**: 특정 전공-자격증 행을 지우면 전공/자격증 정보도 날아갈 수 있음
- **갱신 이상**: 전공명 변경 시 수십 개 행 모두 수정해야 함

---

## ✔ 해결(4NF 만족)

**다중값 속성끼리 분리**한다.

### 테이블 1: 학생 – 전공

|student|major|
|---|---|
|A|컴퓨터|
|A|영어학|

### 테이블 2: 학생 – 자격증

|student|cert|
|---|---|
|A|정보보안|
|A|SQLD|

→ 독립 관계로 분리하여 중복 제거  
→ 조합 폭발 사라짐
## ⭐ 4NF 한 줄 요약

**서로 독립적인 다중값 속성들이 한 테이블에 같이 존재하면 조합 폭발 발생 → 분해 필요**

# ✅ 제5정규형(5NF: Fifth Normal Form, PJ/NF)

## ✔ 핵심 개념

- **조인을 통해 새로운 종속성이 생기는 경우를 방지**하는 단계
- 즉, 테이블을 나눠놓았는데  
    → 다시 조인하면 원래 데이터 외에 “의도하지 않은 데이터 추가(중복)”가 생기면  
    → 그것은 아직 완전히 정규화되지 않은 상태
- 이를 해결하기 위해 **조인 종속성(Join Dependency)** 을 제거하는 것이 5NF.

# 🔥 예시로 쉽게 이해해보자

회의(프로젝트 협업) 테이블을 생각해보자.

- 한 프로젝트에는 여러 **팀원(Member)**
- 여러 **역할(Role)**
- 여러 **도구(Tool)** 이 필요하다고 해보자.

각 속성이 **독립적이지 않고**,  
“특정 팀원이 특정 역할에서 특정 도구를 사용”하는 조합 관계로 구성될 때 문제가 생김.

## ✘ 비정규 예 (5NF 위반)

|Project|Member|Role|Tool|
|---|---|---|---|
|P1|김민수|개발자|VSCode|
|P1|김민수|분석가|Python|
|P1|박영희|개발자|VSCode|
|P1|박영희|분석가|Python|

이걸 분해하면:
### (1) 프로젝트 – 멤버

|Project|Member|
|---|---|
|P1|김민수|
|P1|박영희|

### (2) 프로젝트 – 역할

|Project|Role|
|---|---|
|P1|개발자|
|P1|분석가|

### (3) 프로젝트 – 도구

|Project|Tool|
|---|---|
|P1|VSCode|
|P1|Python|

---

## ✔ 이제 문제:

3개 테이블을 다시 조인하면?
→ **멤버 × 역할 × 도구** 의 모든 조합이 생김
| P1 | 김민수 | 개발자 | VSCode |  
| P1 | 김민수 | 개발자 | Python | ❌ 원래 없던 조합  
| P1 | 김민수 | 분석가 | VSCode | ❌ 원래 없던 조합  
| … | … | … | … |

→ “원래 없던 행”이 대량 생성됨  
→ **조인에 의해 새로운 종속성(잘못된 조합)이 발생한 것**

→ 따라서 5NF 위반

# ✔ 해결 (5NF 충족)

관계 구조를 더 세분화하여  
**정합성을 가진 조합만 별도 엔터티로 유지**해야 한다.

예:
- Project–Member–Role
- Project–Role–Tool  
    등으로 분해
    

각 조합이 명확하게 정의되면  
조인 재구성 시 **원래 데이터만 정확히 재현됨**

# ⭐ 5NF 한 줄 요약

**테이블을 분해했다가 다시 조인했을 때 원본과 다른 결과가 나오면 → 더 분해해서 조인 종속성을 제거해야 한다.**



# 🔥 정규화 단계 전체 요약 (1~5NF + BCNF)

|정규형|제거하는 종속성|핵심 문제|대표 키워드|
|---|---|---|---|
|1NF|반복 그룹|다중값 하나의 칼럼|원자값|
|2NF|부분 함수 종속|복합키 일부 종속|부분 종속|
|3NF|이행적 종속|비키 → 비키|이행 종속|
|BCNF|비후보키 결정자|이상한 결정자|모든 결정자 후보키|
|**4NF**|**다중값 종속(MVD)**|조합 폭발|독립 다중값 분리|
|**5NF**|**조인 종속(Join Dependency)**|조인 시 새로운 튜플 생성|조인 종속 제거|

____

이 부분은 **계층형 질의(Hierarchical Query)** 라고 해서  
“부모-자식 구조(트리)” 데이터를 SQL로 탐색하는 방법을 말하는데,  
Oracle이 전통적으로 제공하는 매우 강력한 기능이야.

너 기준에서 **완전 처음 보는 사람도 이해할 수 있게**  
“예시 → 개념 → 사용법 → 파일 내용 설명” 순으로 정리해줄게.


# 🟦 먼저: 계층형 질의란?

> **부모-자식 구조(트리 구조)를 SQL 한 번으로 탐색하는 기능**

예를 들어 직원을 나타내는 employee 테이블이 있다고 하자.

|emp_id|name|manager_id|
|---|---|---|
|1|사장|NULL|
|2|이사|1|
|3|팀장|2|
|4|선임|3|
|5|대리|4|

이런 구조는

`사장  └─ 이사      └─ 팀장          └─ 선임              └─ 대리`

이렇게 **트리** 형태가 된다.

이걸 SQL만으로 위에서 아래, 아래에서 위로 자동 탐색하는 쿼리가 바로:

### ✔ Oracle:

- `START WITH`
    
- `CONNECT BY`
    
- `PRIOR`
    
- `SYS_CONNECT_BY_PATH`
    
- `CONNECT_BY_ROOT`, `CONNECT_BY_ISLEAF`
    
- `ORDER SIBLINGS BY`
    

# 🟦 파일 내용 하나씩 설명해줄게


# ✅ 1) START WITH

> **시작 노드(최상위 행)** 지정

예:

`START WITH manager_id IS NULL`

→ 사장 같은 최상위 직원부터 시작



# ✅ 2) CONNECT BY

> 부모-자식 관계 정의 (트리를 어떻게 타고 내려갈지)

예:

`CONNECT BY PRIOR emp_id = manager_id`

뜻:

> “부모의 emp_id가 자식의 manager_id와 같으면 연결하라”

즉, 위 → 아래로 내려가는 구조 만들기



# 📌 START WITH + CONNECT BY 전체 예

`SELECT emp_id, name FROM employees START WITH manager_id IS NULL   -- 사장부터 시작 CONNECT BY PRIOR emp_id = manager_id;  -- 부모(emp_id) → 자식(manager_id)`

이렇게 쓰면 자동으로 트리 구조 전체가 나온다.


# 🟦 파일의 상세 옵션 설명



# 🔵 3) CONNECT_BY_ROOT

> **현재 노드의 최상위 부모(루트)** 값 반환

예:

`SELECT name,        CONNECT_BY_ROOT name AS top_manager FROM employees START WITH manager_id IS NULL CONNECT BY PRIOR emp_id = manager_id;`

각 직원의 **최상위 관리자**를 구할 수 있다.



# 🔵 4) CONNECT_BY_ISLEAF

> **해당 노드가 마지막 레벨(leaf)이면 1, 아니면 0**

예:

`SELECT name, CONNECT_BY_ISLEAF`

대리는 리프노드=1,  
사장은 리프노드=0



# 🔵 5) SYS_CONNECT_BY_PATH

> **부모 → 자식으로 이어지는 전체 경로 문자열로 반환**

`SELECT name,        SYS_CONNECT_BY_PATH(name, '→') AS path FROM ...`

결과 예:

`사장→이사→팀장→선임→대리`

# 🔵 6) ORDER SIBLINGS BY

> **형제 노드끼리 정렬**

형제가 뭐냐면, 같은 부모를 가진 직원들.

예:

`ORDER SIBLINGS BY name`

→ 같은 레벨 직원끼리 정렬됨  
(전체 정렬 아님! “레벨별 정렬”)


# 🟦 파일 하단 내용 (2),(3),(4) 의미 설명


# ✔ (2) "앵커 멤버를 실행하여 기본 결과 집합을 만들고 이후 재귀 멤버를 지속적으로 실행한다"

→ 이건 **WITH RECURSIVE (CTE)를 쓰는 SQL Server/PG 방식** 설명임  
Oracle CONNECT BY와 비슷한 기능을 CTE에서 재귀적으로 수행한다는 뜻.

즉:

- **앵커 멤버**: 시작점 (START WITH와 동일)
    
- **재귀 멤버**: 계속 부모-자식 탐색 (CONNECT BY와 동일)
    

예: SQL Server

`WITH cte AS (     SELECT emp_id, name, manager_id     -- 앵커     FROM employees     WHERE manager_id IS NULL      UNION ALL      SELECT e.emp_id, e.name, e.manager_id  -- 재귀     FROM employees e     JOIN cte c ON e.manager_id = c.emp_id ) SELECT * FROM cte;`

Oracle CONNECT BY와 똑같은 기능을 수행한다.


# ✔ (3) “오라클 계층형 질의에서 WHERE절은 모든 전개를 진행한 후 조건 적용”

이게 매우 중요해.

Oracle CONNECT BY 구조에서:

- START WITH + CONNECT BY로 **전체 트리를 완성**한 뒤,
    
- WHERE로 **필터링**한다.
    

즉, WHERE는 “나중에” 적용됨.

예:

`WHERE level >= 3`

→ 전체 트리를 만든 후  
→ 레벨 3 이상만 보여줌


# ✔ (4) PRIOR는 CONNECT BY뿐 아니라 SELECT/WHERE에도 사용 가능

PRIOR는 “부모/자식 관계를 표시하는 키워드”인데  
CONNECT BY 안에서만 쓰는 게 아님.

예:

`SELECT * FROM employees e1, employees e2 WHERE e1.emp_id = PRIOR e2.manager_id CONNECT BY PRIOR e2.emp_id = e2.manager_id;`

즉, PRIOR는 “이전 단계의 행을 참조”한다는 뜻.

# 🟦 총정리: Oracle 계층형 질의 핵심

|키워드|역할|
|---|---|
|**START WITH**|시작 위치 지정|
|**CONNECT BY**|부모-자식 연결 규칙|
|**PRIOR**|CONNECT BY에서 부모/자식 방향 지정|
|**ORDER SIBLINGS BY**|형제 노드끼리 정렬|
|**CONNECT_BY_ROOT**|해당 행의 루트(최상위)|
|**CONNECT_BY_ISLEAF**|리프 여부(1/0)|
|**SYS_CONNECT_BY_PATH**|루트→현재까지 경로 문자열|


# 🧡 최종 예시 (전체 조합)

`SELECT LEVEL,        name,        CONNECT_BY_ROOT name AS root_name,        SYS_CONNECT_BY_PATH(name, '→') AS path,        CONNECT_BY_ISLEAF AS leaf FROM employees START WITH manager_id IS NULL CONNECT BY PRIOR emp_id = manager_id ORDER SIBLINGS BY name;`

결과 예:

|LEVEL|name|root_name|path|leaf|
|---|---|---|---|---|
|1|사장|사장|사장|0|
|2|이사|사장|사장→이사|0|
|3|팀장|사장|사장→이사→팀장|0|
|4|선임|사장|사장→이사→팀장→선임|0|
|5|대리|사장|사장→이사→팀장→선임→대리|1|
