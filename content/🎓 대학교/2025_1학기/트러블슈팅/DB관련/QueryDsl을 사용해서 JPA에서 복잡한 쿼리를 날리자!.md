# 1. 왜 QueryDsl을 사용할까?

- JPA를 사용하는 프로젝트에서 엔티티 기반으로 직접 쿼리문을 날리는 방법은 대표적으로 두가지가 있다.
	1. JPQL
	2. QueryDsl

```java title:"JPQL 예시"
TypedQuery<Member> query = em.createQuery(
    "SELECT m FROM Member m WHERE m.name = :name", Member.class);
query.setParameter("name", "John");
List<Member> result = query.getResultList();
```
- 쿼리를 직접 문자열 쿼리로 써어 날린다.

```java title:"QueryDsl 예시"
QMember m = QMember.member;
List<Member> result = queryFactory
    .selectFrom(m)
    .where(m.name.eq("John"))
    .fetch();
```
- 같은 내용이지만, 문자열 기반과 타입 기반(자바 코드)의 차이가 명확하게 난다.

![[Pasted image 20250509091819.png]]
- 기본적으로 JPQL은 "문자열 기반" 이기 때문에 자동완성, 컴파일 에러, 쿼리 재사용성이 떨어진다.
- 그러나 QueryDsl을 사용하게 되면 마치 자바 코드를 만들 듯이 쿼리문을 쏠 수 있기 때문에 위와 같은 단점이 없어진다. -> <mark style="background: #FFF3A3A6;">대신 별도의 라이브러리를 설치해야함</mark>

____
# 2. 의존성 추가

```groovy title:"build.gradle 의존성 추가"
// queryDSL  
implementation 'com.querydsl:querydsl-jpa:5.0.0:jakarta'  
annotationProcessor "com.querydsl:querydsl-apt:5.0.0:jakarta"  
annotationProcessor "jakarta.annotation:jakarta.annotation-api"  
annotationProcessor "jakarta.persistence:jakarta.persistence-api"
```

- 원래는 build.gradle에 Q파일들 생성위치를 막 /build/src/main.. 이런식으로 정해줬어야 하는데 이제는 필요없음 -> 그래서 검색해보면 자꾸 그거 설정하는 내용이 나옴ㅡㅡ
	- <mark style="background: #FFF3A3A6;">Q파일들(QUser, QPost, QRecruit...)을 QueryDsl 전용의 type-safe한 쿼리 도구임</mark>
	- 쿼리를 날릴 때는 이런 엔티티들이 Q파일로 만들어져서 쿼리문에 사용된다.
		- 자세한건 찾아보셈

____
# 3.  Config파일 추가

```java title:"QuertDslConfig"
package org.ureca.pinggubackend.global.config;  
  
import com.querydsl.jpa.impl.JPAQueryFactory;  
import jakarta.persistence.EntityManager;  
import jakarta.persistence.PersistenceContext;  
import org.springframework.context.annotation.Bean;  
import org.springframework.context.annotation.Configuration;  
  
@Configuration  
public class QueryDslConfig {  
  
    @PersistenceContext  
    private EntityManager em;  
  
    @Bean  
    public JPAQueryFactory jpaQueryFactory(){  
        return new JPAQueryFactory(em);  
    }  
}
```

- <mark style="background: #FFF3A3A6;">이 파일의 목적은 JPAQueryFactory를 Spring Bean으로 등록해서, 다른 Service나 Repository에서 주입할 수 있게 해주는 설정 파일이다.</mark>
	- @PersistenceContext를 통해서 EntityManager를 주입
		- QueryDsl은 JPA위에서 동작하기 때문에
	- EntityManager를 기반으로 JPAQueryFactory를 생성하고 @Bean으로 스프링 빈 등록

___
# 4. 실제 코드 작성

- 우선 아래의 코드는 메인화면에서 검색 필터링을 위한 쿼리를 날리기 위한 코드이다.
- 기존의 JPA의 findBy~ 로는 구현하기 어려운 쿼리기 때문에 직접 작성해야겠다고 생각.

```java title:"RecruitRepositoryCustomImpl", hl:30,39,48,56
package org.ureca.pinggubackend.domain.recruit.repository;  
  
import com.querydsl.core.BooleanBuilder;  
import com.querydsl.core.types.Projections;  
import com.querydsl.jpa.impl.JPAQueryFactory;  
import lombok.RequiredArgsConstructor;  
import org.springframework.data.domain.Page;  
import org.springframework.data.domain.PageImpl;  
import org.springframework.data.domain.Pageable;  
import org.springframework.stereotype.Repository;  
import org.ureca.pinggubackend.domain.location.entity.QClub;  
import org.ureca.pinggubackend.domain.member.enums.Gender;  
import org.ureca.pinggubackend.domain.member.enums.Level;  
import org.ureca.pinggubackend.domain.recruit.dto.response.RecruitPreviewListResponse;  
import org.ureca.pinggubackend.domain.recruit.entity.QRecruit;  
  
import java.time.LocalDate;  
import java.util.List;  
  
@Repository  
@RequiredArgsConstructor  
public class RecruitRepositoryCustomImpl implements RecruitRepositoryCustom {  
    private final JPAQueryFactory queryFactory;  
  
    @Override  
    public Page<RecruitPreviewListResponse> getRecruitPreviewList(LocalDate date, String gu, Level level, Gender gender, Pageable pageable) {  
        QRecruit recruit = QRecruit.recruit;  
        QClub club = QClub.club;  

		// 필터링을 위한 BooleanBuilder
        BooleanBuilder builder = new BooleanBuilder();  
        if (date != null) builder.and(recruit.date.eq(date));  
        if (gu != null) builder.and(club.gu.eq(gu));  
        if (level != null) builder.and(recruit.level.eq(level));  
        if (gender != null) builder.and(recruit.gender.eq(gender));  


        List<RecruitPreviewListResponse> content = queryFactory  
			    // DTO에 매핑하기 위한 Projections
                .select(Projections.constructor(  
                        RecruitPreviewListResponse.class,  
                        club.name,  
                        recruit.date,  
                        recruit.title,  
                        recruit.capacity,  
                        recruit.current  
                )) 
                // 쿼리문 시작 
                .from(recruit)  
                .join(recruit.club, club)  
                .where(builder)  
                .offset(pageable.getOffset())  
                .limit(pageable.getPageSize())  
                .fetch();  

		// Page를 위해서 개수를 세서 반환
        long count = queryFactory  
                .select(recruit.count())  
                .from(recruit)  
                .join(recruit.club, club)  
                .where(builder)  
                .fetchOne();  
  
        return new PageImpl<>(content, pageable, count);  
    }  
}
```
- <mark style="background: #FFF3A3A6;">Member와 Club 엔티티가 쿼리문에 필요하기 때문에 QMember와 QClub을 사용한다.</mark>
- BooleanBuilder를 통해서 .where문을 간단하게 모듈화할 수 있다.
	- <mark style="background: #FFF3A3A6;">재사용성 높음</mark>
- 위 코드는 페이지네이션을 위해서 count을 세는 부분이 있습니다.