![[Pasted image 20260416170414.png]]
- **3)에서 '전산과'를 모두 가져오고, DISTINCT DEPT를 하니까 전산과 중복을 제거하니까 하나만 남음!!**
답 : 1)200, 2) 3, 3) 1

![[Pasted image 20260416170957.png|697]]
답 : 
	SELECT 학번, 이름 
	FROM 학생
	WHERE 학년 IN (3,4)

#### 🔥 INDEX 생성하는 SQL문!!
![[Pasted image 20260416171224.png]]

답 : **CREATE INDEX idx_name ON student(name);**

#### 🔥 GROUP BY는 과목이름으로!!!
![[Pasted image 20260416202224.png]]
답 : 
	SELECT 과목이름, MIN(점수) AS 최소점수, MAX(점수) AS 최대점수
	FROM 성적
	GROUP BY 과목이름 HAVING AVG(점수)>=90;

#### 🔥 속성 추가 (ALTER, ADD)
![[Pasted image 20260416202611.png]]
답 : (1) ALTER (2) ADD

#### 🔥 전체 개수를 위해서는 * 을 사용하자
![[Pasted image 20260416202739.png]]
답 : 
	SELECT 학과, COUNT( * ) AS 학과별튜플수
	FROM 학생
	GROUP BY 학과;

![[Pasted image 20260416202956.png]]
답 : 1

![[Pasted image 20260416203031.png]]
답 : 카디널리티 : 5, 디그리 : 4

#### 🔥 UPDATE문은 SET으로 값을 지정한다.
![[Pasted image 20260416203330.png]]
답 : (1) UPDATE (2) **SET**

![[Pasted image 20260416204208.png]]
답 : (1) ON (2) 코드


#### 🔥 "이"로 시작이면 LIKE '이%'
![[Pasted image 20260416205125.png]]
**답 : 이%, DESC**


![[Pasted image 20260416211303.png]]
- CROSS JOIN을 하면 그냥 전부 곱함
- 그 중에서 WHERE 문에 의해서 걸러져서 4개가 남음
- COUNT(*) 라서 4
답 : 4

![[Pasted image 20260416211844.png]]
답 : (1) ORDER (2) SCORE (3) DESC


#### 🔥 ALL, ANY 개념!
![[Pasted image 20260416212249.png]]
- 모든 값보다 크다 : > ALL
- 어느 하나 보다 크다 : > ANY
답 : **ALL**


![[Pasted image 20260416215140.png]]
- COUNT는 칼럼의 갯수를 반환하는 것이다!!
답 : 4

![[Pasted image 20260416215305.png]]
![[Pasted image 20260416215628.png]]
답 : 
	(1) TTL
	(2) 부장
	(3) 대리
	(4) 과장
	(5) 차장

![[Pasted image 20260417124826.png]]
답 : (1) 3 (2) 4


![[Pasted image 20260417125007.png]]
답 : (1) 200 (2) 3 (3)  1

![[Pasted image 20260417125132.png]]
답 : DELETE FROM 학생 WHERE 이름='민수'

![[Pasted image 20260417125216.png]]
답 : SELECT 과목이름, MIN(점수) AS 최소점수, MAX(점수) AS 최대점수 FROM 성적 GROUP BY 과목이름 HAVING AVG(점수) >=90

#### 🔥 INSERT문은 이렇게 하는거다!!
![[Pasted image 20260417125403.png]]
답 : **INSERT INTO 학생 VALUES(99030298, '한국산', 3, '경영학개론', '050-1234-1234')**

![[Pasted image 20260417125520.png]]
답 : CASCADE

![[Pasted image 20260417125536.png]]
- UNION : 결과를 합치고, 중복은 제거
- UNION ALL : 중복 제거 안함
- INTERSECT : 공통으로 존재하는 데이터만 추출
- EXECPT/MINUS : 첫번째에서 두번째의 값을 빼버림
답 : 
	A
	4
	3
	2
	1


![[Pasted image 20260417130004.png]]
답
	B
	a
	b

![[Pasted image 20260417130039.png]]
답 : 1

#### 🔥INSERT할 때 다른 테이블의 값에서 가져오려면 SELECT
![[Pasted image 20260417130110.png]]
답 : (1) VALUES **(2) SELECT** (2) FROM (4) SET


![[Pasted image 20260417130422.png]]
답 : 카디날리티 : 5, 디그리 : 4

![[Pasted image 20260417130504.png]]
![[Pasted image 20260417130519.png]]
답 : 1

![[Pasted image 20260417130943.png]]
답 : 
	name  | incentives
	이순신  | 1000

![[Pasted image 20260417131046.png]]
- 저거슨 이제, 아 뭐더라.....아 새로로 다 뽑아오는거
답 : 
	TTl
	부장
	대리
	과장
	차장