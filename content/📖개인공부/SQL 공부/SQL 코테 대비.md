
```sql title:"칼럼 몇개만 뽑아오기"
-- 예) 구매량이 3 이상인 구매 건수만 세기
SELECT
  USER_ID,
  SUM(CASE WHEN SALES_AMOUNT >= 3 THEN 1 ELSE 0 END) AS cnt_ge_3
FROM ONLINE_SALE
GROUP BY USER_ID;

-- 예) ‘재구매(같은 상품 2회 이상)’인 상품 수
SELECT
  USER_ID,
  COUNT(*) AS num_repurchase_products
FROM (
  SELECT USER_ID, PRODUCT_ID
  FROM ONLINE_SALE
  GROUP BY USER_ID, PRODUCT_ID
  HAVING COUNT(*) >= 2
) x
GROUP BY USER_ID;
```
- <mark class="hltr-yellow">COUNT()와 HAVING과 GROUP BY를 기억하자!</mark>


```sql title:"조건문 활용" hl:6
-- 예) 이때 전화번호가 없는 경우, 'NONE'으로 출력
SELECT PT_NAME
    , PT_NO
    , GEND_CD
    , AGE
    , IF(TLNO IS NULL OR TLNO = '', 'NONE', TLNO) AS TLNO
FROM PATIENT
WHERE AGE <= 12 AND GEND_CD='W'
ORDER BY AGE DESC, PT_NAME ASC;
```
- MySQL의 경우는 `IF(조건식, '값', 칼럼 이름) AS {표시할 칼럼명}`


```sql title:"날짜 범위" hl:5,7
SELECT BOOK_ID
    , DATE_FORMAT(PUBLISHED_DATE,'%Y-%m-%d') AS PUBLISHED_DATE
FROM BOOK
WHERE 
    PUBLISHED_DATE >= DATE '2021-01-01' 
    AND 
    PUBLISHED_DATE < DATE '2022-01-01'
    AND
    CATEGORY='인문'
ORDER BY PUBLISHED_DATE ASC;


-- LIKE를 활용해서 
PUBLISHED_DATE LIKE '2021%'
```
- 그냥 DATE를 활용해서 범위를 조건으로 줘서 사용할 수 있다.


```sql title:"평균 구하기" hl:1
SELECT ROUND(AVG(DAILY_FEE), 0) AS AVERAGE_FEE
FROM CAR_RENTAL_COMPANY_CAR
WHERE CAR_TYPE = 'SUV';
```
- AVG 사용하기

```sql title:"집계 함수 간단 정리"

1. AVG(expr)  
    그룹(또는 전체)에서 `expr`의 **평균**을 반환합니다.
    - NULL은 무시됩니다.
    - 개념적으로 `SUM(expr)/COUNT(expr)`와 같습니다(직접 나눌 땐 정수 나눗셈에 주의—SQL Server 등에서는 `CAST` 필요).
      
2. SUM(expr)  
    - 합계. NULL은 무시.
    
3. COUNT(*) / COUNT(expr)
    - `COUNT(*)`는 **행 수**(NULL 포함).
    - `COUNT(expr)`는 **expr가 NULL이 아닌 행 수**.
        
4. MIN(expr) / MAX(expr)
	- 최솟값/최댓값. NULL은 무시.
	  
5. ROUND(숫자식, 소수_자릿수)
	- ex) ROUND(1234.56, 1) = 1234.6
```

```sql title:"IS NOT NULL이랑 MONTH(), YEAR(), DAY()" hl:11,10

SELECT MEMBER_ID
    , MEMBER_NAME
    , GENDER
    , DATE_FORMAT(DATE_OF_BIRTH, '%Y-%m-%d') AS DATE_OF_BIRTH
FROM MEMBER_PROFILE
WHERE 
    GENDER='W'
    AND
    TLNO is NOT NULL
    AND MONTH(DATE_OF_BIRTH) = 3
ORDER BY MEMBER_ID ASC;
```

```sql title:"🧙‍♂️ 확인하는 습관 + JOIN과 MySQL의 집계함수 사용법"
--  식당 ID, 식당 이름, 음식 종류, 즐겨찾기수, 주소, 리뷰 평균 점수를 조회하는 SQL문을 작성
SELECT A.REST_ID
    , A.REST_NAME
    , A.FOOD_TYPE
    , A.FAVORITES
    , A.ADDRESS
    , ROUND(AVG(B.REVIEW_SCORE),2) AS SCORE
FROM REST_INFO AS A
JOIN REST_REVIEW AS B
ON A.REST_ID = B.REST_ID
WHERE A.ADDRESS LIKE '서울%'
GROUP BY A.REST_ID,	A.REST_NAME, A.FOOD_TYPE, A.FAVORITES, A.ADDRESS
ORDER BY ROUND(AVG(B.REVIEW_SCORE),2) DESC, A.FAVORITES DESC;
```
- 문제 링크 : https://school.programmers.co.kr/learn/courses/30/lessons/131118
- 우선 JOIN을 위해서 ON을 통해서 REST_ID가 같은 경우를 합친다.
- 주소가 서울로 시작하기 때문에 LIKE "서울%"

><span style="background:#affad1"># 집계함수 & GROUP BY 초간단 정리</span>
>- **GROUP BY**: 지정한 식(컬럼) 값이 같은 행들을 **그룹**으로 묶고 **그룹당 1행**을 반환.
>- **집계함수**: 그룹 내부에서 값을 하나로 요약    
>- `AVG(expr)`, `SUM(expr)`, `COUNT(*)/COUNT(expr)`, `MIN/MAX` (NULL은 대부분 무시, `COUNT(*)`만 예외)
> - **실행 순서**: `FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY`
> - 그래서 집계조건은 **HAVING**에서, 행 필터링은 **WHERE**에서.


```sql title:"JOIN을 두번하기 && WHERE IN"
-- 'RARE' 등급인 부모아이템의 모든 자식을 출력
SELECT C.ITEM_ID, C.ITEM_NAME, C.RARITY
FROM ITEM_TREE A
JOIN ITEM_INFO P ON A.PARENT_ITEM_ID=P.ITEM_ID
JOIN ITEM_INFO C ON A.ITEM_ID=C.ITEM_ID
WHERE P.RARITY='RARE'
ORDER BY C.ITEM_ID DESC;

-------------------
SELECT T.ITEM_ID, I.ITEM_NAME, I.RARITY 
FROM ITEM_INFO I 
JOIN ITEM_TREE T ON I.ITEM_ID = T.ITEM_ID 
WHERE T.PARENT_ITEM_ID IN ( 
		SELECT ITEM_ID 
		FROM ITEM_INFO 
		WHERE RARITY = 'RARE' 
) 
ORDER BY T.ITEM_ID DESC
```
- <mark class="hltr-yellow">우리가 필요한 값들을 제대로 쓰는 것이 중요하다.</mark>



```sql title:"비트연산자를 사용하는 경우"
-- 코드를 작성해주세요
SELECT ID,EMAIL,FIRST_NAME,LAST_NAME
FROM DEVELOPERS
WHERE 
    SKILL_CODE & (SELECT CODE FROM SKILLCODES WHERE NAME='Python')
    OR
    SKILL_CODE & (SELECT CODE FROM SKILLCODES WHERE NAME='C#')
ORDER BY ID ASC;
```
![[Pasted image 20250925230109.png]]
>MySQL에선 `WHERE (표현식)`에서 **0은 거짓, 0이 아니면 참**으로 평가되므로  
>굳이 `<> 0`을 안 써도 동작하지만, **명시**하는 편이 읽기 쉬워요.
>문제 : https://school.programmers.co.kr/learn/courses/30/lessons/276034



```sql title:"JOIN을 잘하자"
-- 코드를 작성해주세요
SELECT COUNT(*) AS FISH_COUNT
FROM FISH_INFO A
JOIN FISH_NAME_INFO B ON A.FISH_TYPE=B.FISH_TYPE
WHERE B.FISH_NAME='BASS' OR B.FISH_NAME='SNAPPER';
```


```sql title:"MAX() 가장 비싼 가격의 식품 가져오기"
SELECT *
FROM FOOD_PRODUCT
WHERE PRICE = (
    SELECT MAX(PRICE)
    FROM FOOD_PRODUCT
)
```

```sql title:"LIMIT으로 최솟값 가져오기"
-- 코드를 입력하세요
SELECT DATETIME
FROM ANIMAL_INS
ORDER BY DATETIME DESC
LIMIT 1;
```

```sql title:"이름 중복제거"
-- 코드를 입력하세요
SELECT COUNT(DISTINCT NAME) AS count
FROM ANIMAL_INS 
```
- COUNT(expr)는 NULL은 집계하지 않음
- <mark class="hltr-yellow">DISTINCT를 통해서 중복된 이름은 제거</mark>


```sql title:"⭐️ 우리가 원하는 조건의 컬럼을 만들고 JOIN하기"
-- 코드를 작성해주세요
SELECT 
    YEAR(A.DIFFERENTIATION_DATE) AS YEAR
    , (B.MAX_SIZE - A.SIZE_OF_COLONY) AS YEAR_DEV
    , A.ID
FROM ECOLI_DATA A
JOIN(
    SELECT 
        YEAR(DIFFERENTIATION_DATE) AS YEAR
        , MAX(SIZE_OF_COLONY) AS MAX_SIZE
    FROM ECOLI_DATA
    GROUP BY YEAR(DIFFERENTIATION_DATE)
) AS B
    ON YEAR(A.DIFFERENTIATION_DATE)=B.YEAR
ORDER BY YEAR ASC, YEAR_DEV ASC;


--------- 유사한 문제 ---------

-- 물고기 종류 별로 가장 큰 물고기의 ID, 물고기 이름, 길이를 출력하는 SQL 문을 작성해주세요.
-- 결과는 물고기의 ID에 대해 오름차순 정렬해주세요.
SELECT A.ID
    , C.FISH_NAME
    , B.MAX_LENGTH AS LENGTH
FROM FISH_INFO A
JOIN (
    SELECT FISH_TYPE
        ,MAX(LENGTH) AS MAX_LENGTH
    FROM FISH_INFO
    GROUP BY FISH_TYPE
) B
ON A.FISH_TYPE = B.FISH_TYPE AND A.LENGTH = B.MAX_LENGTH
JOIN FISH_NAME_INFO C ON A.FISH_TYPE = C.FISH_TYPE
ORDER BY A.ID ASC

```
- 우리는 년도별로 최댓값을 가지고 그걸 ECOLI_DATA에 각각의 연도에 맞게 배치를 시키고 싶다 -> 즉 만들어서 JOIN을 해야한다. 
- 그래서 우리는 JOIN문 안에 SELECT를 통해서 YEAR와 MAX_SIZE 두개의 컬럼을 만든다. 
- 그리고 조건을 YEAR를 통해서 JOIN을 하면 각각의 데이터에 최댓값을 가지고 있게 된다.


```sql title:"문자열 붙이기"
-- 코드를 작성해주세요
SELECT CONCAT(MAX(LENGTH),'cm') AS MAX_LENGTH
FROM FISH_INFO
```


```sql title:"having으로 GROUP BY 조건 지정" hl:4,7,8
-- 코드를 입력하세요
SELECT
    NAME
    , COUNT(*) AS COUNT
FROM ANIMAL_INS 
WHERE NAME IS NOT NULL
GROUP BY NAME
HAVING COUNT(*) >=2
ORDER BY NAME ASC;
```
- NULL이 아니라는 것도 강조!


```sql title:"FLOOR - 구간의 시작값"
-- 코드를 입력하세요
SELECT
     FLOOR(PRICE/10000)*10000 AS PRICE_GROUP
    , COUNT(*) AS PRODUCTS
FROM PRODUCT
GROUP BY FLOOR(PRICE/10000)*10000
ORDER BY PRICE_GROUP ASC;
```
-동작예시
- PRICE = 9000 → `FLOOR(9000/10000)=0` → 0 * 10000=0
- PRICE = 10000 → `FLOOR(1)=1` → 10000
- PRICE = 15000 → `FLOOR(1.5)=1` → 10000
- PRICE = 22000 → `FLOOR(2.2)=2` → 20000
- PRICE = 30000 → `FLOOR(3)=3` → 30000


```sql title:"GROUP BY 좋은 문제"
-- 코드를 작성해주세요
SELECT 
    SUM(B.SCORE) AS SCORE
    , A.EMP_NO
    , A.EMP_NAME
    , A.POSITION
    , A.EMAIL
FROM HR_EMPLOYEES A
JOIN HR_GRADE B ON A.EMP_NO=B.EMP_NO
GROUP BY A.EMP_NO
ORDER BY SCORE DESC
LIMIT 1;

```
- <mark class="hltr-yellow">GROUP BY의 기준을 PK인 사원번호로 했어야했음.</mark>


```sql title:"반올림 조심하기 + 정렬기준 조심하기"
-- 코드를 작성해주세요
SELECT ROUTE
    , CONCAT(ROUND(SUM(D_BETWEEN_DIST),1),'km') AS TOTAL_DISTANCE
    , CONCAT(ROUND(AVG(D_BETWEEN_DIST),2),'km') AS AVERAGE_DISTANCE
FROM SUBWAY_DISTANCE
GROUP BY ROUTE
ORDER BY SUM(D_BETWEEN_DIST) DESC;
```
- <mark class="hltr-yellow">반올림은 어디까지 나타내고 싶냐는 의미다! 소수점 둘째자리에서 반올림을 하면 첫째자리까지 나오니까 '1'</mark>
- <mark class="hltr-yellow">정렬을 할 때 ROUND()가 되기 때문에 SUM(expr)로 해야한다! 안그러면 짤리면서 정렬이 제대로 안된다!</mark>


```sql title:"⭐️ WHEN - THEN - ELSE문" hl:16-23
SELECT 
    CAR_ID,
    CASE 
        WHEN SUM(
            '2022-10-16' BETWEEN START_DATE AND END_DATE
        ) > 0 THEN '대여중'
        ELSE '대여 가능'
    END AS AVAILABILITY
FROM CAR_RENTAL_COMPANY_RENTAL_HISTORY
GROUP BY CAR_ID
ORDER BY CAR_ID DESC;

--------------- 좀 더 간단한 풀이 --------------- 

SELECT CAR_ID,
       CASE 
           WHEN CAR_ID IN (
               SELECT CAR_ID
               FROM CAR_RENTAL_COMPANY_RENTAL_HISTORY
               WHERE '2022-10-16' BETWEEN START_DATE AND END_DATE
           ) THEN '대여중'
           ELSE '대여 가능'
       END AS AVAILABILITY
FROM CAR_RENTAL_COMPANY_RENTAL_HISTORY
GROUP BY CAR_ID;
```
- WHEN의 조건에 해당되는 쿼리가 하나 이상만 존재를 해도 WHEN의 조건을 타게 됨. (즉시 나오는게 아님)
- 그러니까 하나의 CAR_ID에 대해서 하나라도 '대여중'인 상태면 GROUP BY에 의해서 대여중으로 나오게 되는 것임.
- 우리의 예시는 좀 더 알아먹기 쉽게 SUM()을 이용해서 개수를 세서 하는 경우고 아래의 쿼리는 좀 더 간략화된 경우


```sql title:"CASE WHEN ELSE"
-- 코드를 작성해주세요
SELECT ID
    ,CASE 
        WHEN SIZE_OF_COLONY <= 100 THEN 'LOW'
        WHEN SIZE_OF_COLONY <= 1000 THEN 'MEDIUM'
        ELSE 'HIGH'
    END  AS SIZE
FROM ECOLI_DATA
ORDER BY ID ASC;
```
