```java title:"반경 radius만큼 매장을 가져오는 Repository 코드"
package com.ureca.uhyu.domain.store.repository;  
  
import com.querydsl.core.types.dsl.Expressions;  
import com.querydsl.jpa.impl.JPAQueryFactory;  
import com.ureca.uhyu.domain.brand.entity.QBenefit;  
import com.ureca.uhyu.domain.brand.entity.QBrand;  
import com.ureca.uhyu.domain.brand.entity.QCategory;  
import com.ureca.uhyu.domain.store.entity.QStore;  
import com.ureca.uhyu.domain.store.entity.Store;  
import lombok.RequiredArgsConstructor;  
import org.springframework.stereotype.Repository;  
  
import java.util.List;  
  
@Repository  
@RequiredArgsConstructor  
public class StoreRepositoryImpl implements StoreRepositoryCustom{  
    private final JPAQueryFactory queryFactory;  
  
    @Override  
    public List<Store> findStoresWithBrandAndBenefitWithinRadius(double lat, double lon, double radiusInKm) {  
        QStore store = QStore.store;  
        QBrand brand = QBrand.brand;  
        QCategory category = QCategory.category;  
        QBenefit benefit = QBenefit.benefit;  
  
        return queryFactory  
                .selectFrom(store)  
                .leftJoin(store.brand, brand).fetchJoin()  
                .leftJoin(brand.category, category).fetchJoin()  
                .leftJoin(brand.benefits, benefit).fetchJoin()  
                .where(  
                        Expressions.booleanTemplate(  
                                "cast(ST_DWithin(" +  
                                        "ST_Transform({0}, 3857), " +  
                                        "ST_Transform(ST_SetSRID(ST_MakePoint({1}, {2}), 4326), 3857), " +  
                                        "{3}) as boolean)",  
                                store.geom, lon, lat, radiusInKm  
                        )  
                )  
                .distinct()  
                .fetch();  
    }  
}
```

- `(double lat, double lon, double radius)` 을 기준으로 매장을 보여준다. 
- PostGIS의 거리 함수 `ST_DWithin()` 을 이용해서 반경 조건을 구현.


```java 
// Q 클래스는 QueryDSL이 자동 생성한 엔티티 쿼리 클래스입니다.
QStore store = QStore.store;
QBrand brand = QBrand.brand;
QCategory category = QCategory.category;
QBenefit benefit = QBenefit.benefit;
```
- 타입 세이프한 쿼리를 만들기 위해 도구인 <mark style="background: #BBFABBA6;">Q 객체</mark>를 생성


```java 
return queryFactory
    .selectFrom(store)
```
- 기본테이블인 store 테이블 선택


```java
.leftJoin(store.brand, brand).fetchJoin()
.leftJoin(brand.category, category).fetchJoin()
.leftJoin(brand.benefits, benefit).fetchJoin()
```
- <mark style="background: #BBFABBA6;">N+1 문제를 방지하기 위한 핵심</mark>
-  JPA에서 LAZY 로딩된 관계(brand, category, benefits)을 한 번에 즉시 로딩하기 위해 fetchJoin() 사용
- <mark style="background: #BBFABBA6;">JPA가 추가 쿼리를 날리지 않고 한번에 조인한다!</mark>


#### 1. 왜 연관관계를 LAZY(지연로딩)으로 해두는가..

- 필요할 때만 로딩 -> 불필요한 SQL 감소
- 연관 데이터를 원할 때만 불러옴
- 양방향 연관 시 EAGER는 순환 참조 위험이 있음 (ex. Store -> Brand -> Store....)

### 2. N+1 문제란?

- <mark style="background: #BBFABBA6;">1개의 쿼리를 실행한 후 N개의 추가 쿼리가 발생하는 상황</mark>

EX)
```java 
List<Store> stores = storeRepository.findAll(); // 1개의 쿼리
for (Store store : stores) {
    store.getBrand().getName(); // store 수만큼 N개의 brand 쿼리 추가 실행
}
```
- 하나의 Store에 들어가서 어떤 Brand인지 가져오기 위해서 getBrand().getName()을 하면
- N개의 store에 대해서 M개의 Brand가 있다면, N * M 번의 쿼리가 날라가야함..


### 3. 이걸 해결하기 위한 fetchJoin
```java
List<Store> stores = queryFactory
    .selectFrom(store)
    .leftJoin(store.brand, brand).fetchJoin()
    .fetch();
```
- <mark style="background: #BBFABBA6;">단일 SQL로 Store + Brand를 조인해서 한 번에 조회함.</mark>
- `fetchJoin()`은 하나의 SQL 쿼리 안에서 여러 연관 엔티티를 `JOIN`하여 함께 조회하기 때문에, 추가적인 쿼리(N개)가 발생하지 않음.

