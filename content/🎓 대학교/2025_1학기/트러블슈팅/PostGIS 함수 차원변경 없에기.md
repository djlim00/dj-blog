```java title:"기존의 코드"
private Predicate withinRadius(double lat, double lon, double radius) {  
    return Expressions.booleanTemplate(  
            "cast(ST_DWithin(" +  
                    "ST_Transform({0}, 3857), " +  
                    "ST_Transform(ST_SetSRID(ST_MakePoint({1}, {2}), 4326), 3857), " +  
                    "{3}) as boolean)",  
            store.geom, lon, lat, radius  
    );  
}
```

```java title:"수정된 코드"
private Predicate withinRadius(double lat, double lon, double radius) {  
    return Expressions.booleanTemplate(  
            "ST_DistanceSphere({0}, ST_SetSRID(ST_MakePoint({1}, {2}), 4326)) <= {3}",  
            store.geom, lon, lat, radius  
    );  
}
```
___

#  좌표계 변환(ST_Transform)을 제거하고 ST_DistanceSphere로 변환

> 좌표계를 바꿔서 거리 계산하던 방식(`ST_Transform`)을 제거하고, 지구 구면 기반 거리 계산 함수(`ST_DistanceSphere`)를 도입했다.
- <mark style="background: #BBFABBA6;">공간 연산 성능 최적화</mark>


## 1. 기존 방식: `ST_DWithin` + `ST_Transform`


```java 
ST_DWithin(ST_Transform(geom, 3857),   ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4326), 3857), radius)
```
### 왜 이렇게 했을까?

- **`ST_DWithin`은 거리 비교를 위한 함수**인데, 이 함수는 **투영 좌표계 (예: EPSG:3857)** 상에서 미터 단위로 정확히 연산하려면 좌표계를 변환해야 함.
- `geom`은 기본적으로 EPSG:4326 (위도/경도)이므로, **둘 다 3857로 변환한 후 비교**한 것.
- 결과적으로 "이 두 지점이 radius(미터) 이내인가?"를 정확하게 측정할 수 있었음.

> **기본 선택 이유**: **정확한 거리 계산**이 목적이었고, 공간 인덱스를 활용한 `ST_DWithin`은 일반적으로 효율적인 방식으로 알려져 있음.


## 2. 바꾼 방식: `ST_DistanceSphere`

```java 
ST_DistanceSphere(geom, ST_SetSRID(ST_MakePoint(lon, lat), 4326)) <= radius
```
### 이 방식의 특징

- **지구를 구형으로 보고 거리를 계산**하는 함수.
- 내부적으로 **Haversine 공식** 기반으로 작동.
    
- **좌표계 변환 불필요**, geom과 비교 대상 모두 EPSG:4326 상태 그대로 계산.

> 즉, **SRID 변환 없이 바로 거리 계산** 가능하다는 점이 장점.


___

## 너가 얻는 이점들

| 항목            | 효과                                  |
| ------------- | ----------------------------------- |
| **좌표계 변환 제거** | CPU 연산 감소 (ST_Transform은 계산 비용 큼)   |
| **성능 향상**     | 실시간 거리 필터링 시 지연 시간 단축               |
| **단순화된 쿼리**   | 코드 가독성 및 유지보수성 향상                   |
| **정확도 적절**    | 수 미터 오차 감수 가능하다면 충분한 정확도            |
| **비용 감소**     | PostGIS 연산 부하가 적어짐 (RDS 기준 과금에도 영향) |

ST_Transform을 사용해서 차원을 3857로 바꾸고 ST_DWithin을 이용해서 거리를 측정하는 정확한 방법보다, ST_DistanceSphere를 사용하는 방식은 우리가 기본적으로 데이터를 geom(4326 차원)을 사용하기 때문에 더 빠르다고 볼 수 있는거잖아. 그럼 ST_Transform가 얼마나 큰연산인지에 대해서 어디서 좀 정보를 얻을 수 있을까? 성능이 어느정도 나오는지



____


좋은 질문입니다. 이 두 쿼리는 **PostGIS 공간 거리 연산**을 위한 대표적인 방식들인데, **정확도, 성능, 인덱스 사용 여부**에서 큰 차이가 있습니다. 아래에 비교 방법과 평가 기준, 그리고 `ST_DWithin` 방식 중 최선의 형태까지 정리해 드릴게요.

---

## ✅ 1. 두 쿼리의 역할 요약

|방식|설명|특징|
|---|---|---|
|`ST_DWithin(ST_Transform(..., 3857), ST_Transform(..., 3857), radius)`|위경도를 **평면좌표계로 변환** 후 `DWithin`으로 거리 비교|**정확하지만 느림**, 인덱스 안 탐|
|`ST_DistanceSphere(geom, point) <= radius`|구면 거리 계산 함수, WGS84 좌표계 유지|**빠름**, 인덱스 안 탐, 충분히 정확함|

---

## ✅ 2. 비교 방법 (실제 성능 측정)

### 🔹 **1단계: SQL 직접 성능 측정**

```sql
-- 방법 A: 정확도 중심
EXPLAIN ANALYZE
SELECT * FROM store
WHERE ST_DWithin(
    ST_Transform(geom, 3857),
    ST_Transform(ST_SetSRID(ST_MakePoint(127.0370, 37.5229), 4326), 3857),
    10000
);

-- 방법 B: 성능 중심
EXPLAIN ANALYZE
SELECT * FROM store
WHERE ST_DistanceSphere(
    geom,
    ST_SetSRID(ST_MakePoint(127.0370, 37.5229), 4326)
) <= 10000;
```

→ **실행 시간**, **row 수**, **Index Scan 여부**를 확인  
→ `EXPLAIN (ANALYZE, BUFFERS)`를 사용하면 더 정밀한 I/O 정보까지 확인 가능

---

### 🔹 **2단계: pg_stat_statements로 모니터링**

`pg_stat_statements`에서 쿼리 단위의:

- `calls` (호출 횟수)
    
- `total_exec_time`, `avg_time`
    
- 메모리 사용량
    

등을 비교할 수 있습니다.

---

### 🔹 **3단계: 정확도 비교**

1. 동일한 `(lon, lat, radius)` 조건으로 두 쿼리 실행
    
2. 반환되는 store 목록 비교
    
3. 거리 차이가 **수 미터 이내**면 `ST_DistanceSphere`는 실사용에 적합
    

---

## ✅ 3. `ST_DWithin` 사용 시의 최선 방법은?

현재 사용하는 이 방식은:

```sql
ST_DWithin(
  ST_Transform(geom, 3857),
  ST_Transform(ST_SetSRID(ST_MakePoint(lon, lat), 4326), 3857),
  radius
)
```

> 📌 "정확한 거리"가 필요한 경우에는 **최선**입니다.  
> 다만, **성능이 중요한 실시간 API**에서는 적합하지 않습니다.

### 🔹 대안이 있다면?

1. **PostGIS KNN 인덱스 + Bounding Box 조합**
    
    - `ORDER BY geom <-> ST_SetSRID(ST_MakePoint(...))`
        
    - `&&` 연산자와 `GIST index`를 사용해서 가까운 점을 **인덱스로 빠르게 찾는** 방식
        
2. **ST_DWithin(geom, point, radius)** 로 인덱스를 활용하는 구조
    
    - 단, `geom`과 `point`가 모두 **같은 SRID**여야 인덱스가 걸림
        
    - `geom`이 4326이고, `point`도 4326이면 인덱스 사용 가능
        
    
    ✅ **따라서 아래와 같은 구조가 더 나은 대안일 수 있습니다**:
    
    ```sql
    ST_DWithin(geom, ST_SetSRID(ST_MakePoint(lon, lat), 4326), radius_in_degrees)
    ```
    
    🔸 단점: `radius` 단위가 meter가 아닌 **degree**  
    🔸 서울 기준 1도 ≈ 111km → 1km ≈ 0.009 degrees
    
    → 계산해서 넣으면 인덱스도 타면서 성능과 정확도 모두 보장 가능
    

---

## ✅ 결론 요약

|항목|`ST_DWithin(ST_Transform(...))`|`ST_DistanceSphere(...)`|
|---|---|---|
|정확도|✅ 가장 정확 (미터 단위)|✅ 충분히 정확 (구면 계산)|
|성능|❌ 느림 (CPU 연산, 인덱스 안 탐)|✅ 빠름 (CPU 연산 적음)|
|인덱스 사용|❌ 안 됨|❌ 안 됨|
|실시간 API 적합|❌ 부적합|✅ 적합|
|쿼리 길이|복잡|간결|

---

## ✅ 추천

- 실시간 필터 → `ST_DistanceSphere(...)`
    
- 정확도가 중요한 오프라인 분석 → `ST_DWithin + ST_Transform`
    
- 인덱스를 반드시 활용하고 싶다면 → `ST_DWithin(geom, point, radius_in_degrees)` + GIST 인덱스
    

---

필요하다면 위 세 가지 방식 모두를 코드로 비교 테스트할 수 있도록 예제 쿼리와 QueryDSL 템플릿도 만들어드릴게요.




![[Pasted image 20250805094553.png]]