### **Liquibase를 사용하여 데이터베이스 수정하기 (JPA Buddy 활용)**
Liquibase를 활용하여 데이터베이스를 수정하려면 **변경사항을 정의하는 Changelog 파일을 작성하고 적용**해야 합니다.  
JPA Buddy를 사용하면 이를 자동으로 생성할 수 있습니다.

---
## **1. JPA Buddy란?**
JPA Buddy는 **Spring Boot + JPA 프로젝트에서 엔티티 생성, 매핑, Liquibase Changelog 자동 생성**을 지원하는 IntelliJ 플러그인입니다.  
특히 **Liquibase 변경 사항을 쉽게 생성**할 수 있기 때문에 **JPA 엔티티 변경 → Liquibase 스크립트 자동 생성 → DB 업데이트** 과정이 편리해집니다.

---
## **2. JPA Buddy 설치 및 사용법**
### **2-1. JPA Buddy 설치 (IntelliJ IDEA)**
1. **IntelliJ IDEA** → `Preferences` (Mac) / `Settings` (Windows) 이동
2. `Plugins` → `Marketplace` 검색
3. `"JPA Buddy"` 검색 후 설치
4. IntelliJ 재시작

---
## **3. Liquibase를 사용하여 데이터베이스 변경하기**
### **3-1. 엔티티 수정**
예를 들어, `Article` 엔티티에 `category` 컬럼을 추가한다고 가정하겠습니다.
kotlin
복사편집
`@Entity @Table(name = "article") class Article(     @Id     @GeneratedValue(strategy = GenerationType.IDENTITY)     val id: Long = 0,      @Column(nullable = false)     val title: String,      @Column(nullable = false)     val text: String,      @Column(name = "category", nullable = false)  // 새로운 필드 추가     val category: String )`

---
### **3-2. Liquibase Changelog 생성 (JPA Buddy 사용)**
1. **JPA Buddy 창 열기**
    - IntelliJ에서 `JPA Buddy` 탭을 클릭 (`Database` 창과 함께 있음)
2. **Liquibase Changelog 자동 생성**
    - `Generate Liquibase Changelog` 클릭
    - `New Changeset` 선택
    - 변경된 엔티티 선택 (`Article` 엔티티)
    - `Generate` 클릭
3. **변경사항 파일 (`.xml`) 확인**
    - `db/changelog/changes/2025-03-28-add-category-to-article.xml` 파일이 생성됨
xml
복사편집
`<databaseChangeLog>     <changeSet id="20250328-1" author="yourname">         <addColumn tableName="article">             <column name="category" type="varchar(255)">                 <constraints nullable="false"/>             </column>         </addColumn>     </changeSet> </databaseChangeLog>`

---
### **3-3. `master.xml`에 변경 파일 추가**
Liquibase는 `master.xml`을 통해 어떤 변경 사항을 적용할지 관리합니다.  
새로 생성된 Changelog를 `master.xml`에 등록해야 합니다.
xml
복사편집
`<databaseChangeLog>     <include file="db/changelog/changes/2025-03-28-add-category-to-article.xml"/> </databaseChangeLog>`

---
### **3-4. Liquibase 적용 및 DB 업데이트**
이제 변경사항을 적용해야 합니다.
1. **IntelliJ에서 터미널 열기**
2. **Liquibase 적용 명령 실행**
    sh
    복사편집    
    `./gradlew update`

3. **DB 변경 확인**
    - `article` 테이블에 `category` 컬럼이 추가되었는지 확인
---
## **4. 정리**
✅ **JPA Buddy를 이용해 Liquibase Changelog 자동 생성**  
✅ **Changelog를 `master.xml`에 추가하여 관리**  
✅ **Liquibase를 실행하여 DB 업데이트**

이제 JPA 엔티티를 변경할 때 **JPA Buddy를 활용해 Liquibase 변경 사항을 자동 생성**하고,  
손쉽게 **DB 변경 사항을 관리**할 수 있습니다. 🚀




- 우선 JPA Buddy를 깔면 왼쪽에 DB랑 Gradle 아래에 생김
![[Pasted image 20250321153927.png]]
- 이제 내가 변경되야 하는 사항에 대해서 어떤 데이터 베이스랑 연결인지 설정을 해주고
- 그럼 내가 만약에 Entitiy에 변경이 있다면 이런식으로 changelog를 알아서 만들어줌


- JPA Buddy는 일종의 리버스 엔지니어링을 제공하는 플러그인임!
- 우리는 DDL을 만들면 -> 엔티티 코드를 만들어주는게 주로 미는 기능인 듯
- 근데 이제 이런 기능을 제공하면서 liquibase를 이용하는 사람들이 많으니까, changelog를 만들어주는 기능도 있는듯