# 🎯 **1. 오토 스케일링 (Auto Scaling)**

**🔹 스프링에서 어떻게 적용할까?**
- AWS EC2 + **Spring Boot** 배포 시 **Auto Scaling Group**을 설정
- **AWS CloudWatch**로 트래픽 급증 감지 후 EC2 인스턴스 자동 확장
📌 **관련 기술**
- **Spring Boot + Docker + AWS ECS + Auto Scaling**
- Kubernetes(HPA, Horizontal Pod Autoscaler)
https://inpa.tistory.com/entry/AWS-%F0%9F%93%9A-EC2-%EC%98%A4%ED%86%A0-%EC%8A%A4%EC%BC%80%EC%9D%BC%EB%A7%81-ELB-%EB%A1%9C%EB%93%9C-%EB%B0%B8%EB%9F%B0%EC%84%9C-%EA%B0%9C%EB%85%90-%EA%B5%AC%EC%B6%95-%EC%84%B8%ED%8C%85-%F0%9F%92%AF-%EC%A0%95%EB%A6%AC#1._%EC%8B%9C%EC%9E%91_%ED%85%9C%ED%94%8C%EB%A6%BF_%EC%83%9D%EC%84%B1


---

# 🎯 **2. 로드 밸런서 (Load Balancer)**

로드밸런서가 죽을 수도 있어서, 로드 밸런서를 늘려야함 -> 로드 밸런서 안에 Nginx를 둔다던가
로드 밸런서 안에서 오토 스케일링을 진행한다. 그렇기 때문에 돈만 지불하면 무한한 자원을 가능하게 하는 클라우드 서비스가 진짜 사기라는 거다.

|방법|적용 방식|효과|
|---|---|---|
|**로드 밸런서 Auto Scaling**|로드 밸런서 자체를 Auto Scaling|트래픽 급증 시 로드 밸런서 자동 확장|
|**DNS 기반 다중 로드 밸런서 (GSLB)**|여러 로드 밸런서를 DNS로 연결|로드 밸런서 한 개가 터져도 자동 우회|
|**Nginx 이중화 (Keepalived 사용)**|여러 Nginx를 VIP로 연결|Nginx 다운 시 자동 전환|
|**Kubernetes Ingress Controller 다중 배포**|여러 개의 Ingress Controller 운영|특정 노드가 다운되더라도 서비스 유지|
|**CDN + 캐싱 사용**|정적 콘텐츠를 CDN에서 제공|서버 장애 시에도 기본 콘텐츠 유지|


**🔹 스프링에서 어떻게 적용할까?**
- **AWS ALB(Application Load Balancer) + Spring Boot**
- **Nginx + Spring Boot** (Reverse Proxy)
- **Spring Cloud Gateway**를 사용해 API 요청을 여러 서버에 분산

📌 **관련 기술**

- **Spring Cloud Gateway**
- **Nginx Load Balancing**
- **Kubernetes Ingress Controller**

# 1️⃣ AWS ALB(Application Load Balancer)
### **ALB + Auto Scaling 적용 흐름**
1️⃣ **Spring Boot를 Docker 컨테이너로 패키징**  
2️⃣ **AWS ECS (Elastic Container Service)에 배포**  
3️⃣ **ALB를 설정하여 트래픽을 여러 컨테이너로 분산**  
4️⃣ **Auto Scaling을 통해 트래픽이 많아지면 자동으로 컨테이너 증가**
**Spring Boot에서 ALB를 활용할 때**
- EC2 / ECS에 배포한 **Spring Boot API 서버를 ALB 뒤에 배치**
- ALB는 클라이언트 요청을 여러 서버로 **라운드 로빈 방식으로 분산**
## **2️⃣ Nginx + Spring Boot (Reverse Proxy)**

**✅ Nginx를 로드 밸런서로 사용하여 트래픽 분산**  
✔ 클라이언트 → **Nginx** → 여러 대의 Spring Boot 서버
✅ **Nginx의 장점**

- **단순하고 가벼운 로드 밸런싱 가능**
- **HTTPS(SSL) 오프로드 가능**
- **정적 리소스 캐싱 가능**

## **3️⃣ Spring Cloud Gateway**

**✅ Spring Boot 자체적으로 API Gateway 역할 수행**  
✔ 클라이언트 → **Spring Cloud Gateway** → 여러 서비스로 요청 전달  
✔ **필터 기능**을 통해 인증, 로깅, 캐싱 등의 추가 기능 가능


---

# 🎯 **3. 서킷 브레이커 (Circuit Breaker)**

```java 
import io.github.resilience4j.circuitbreaker.annotation.CircuitBreaker;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class ExternalApiService {

    private final RestTemplate restTemplate = new RestTemplate();

    @CircuitBreaker(name = "myService", fallbackMethod = "fallbackMethod")
    public String callExternalAPI() {
        return restTemplate.getForObject("http://external-service.com/api", String.class);
    }

    // 서킷이 OPEN 상태일 때 호출되는 대체 메서드 (Fallback)
    public String fallbackMethod(Exception e) {
        return "서비스가 불안정합니다. 잠시 후 다시 시도해주세요.";
    }
}

```
📌 **설명**

1. `@CircuitBreaker(name = "myService", fallbackMethod = "fallbackMethod")`  
    → **"myService"라는 이름의 서킷 브레이커 적용**
2. `fallbackMethod(Exception e)`  
    → **외부 API 장애 시 호출될 대체 응답 (Fallback Method)**
3. **외부 API가 응답을 못하면 즉시 Fallback 메서드 실행 → 추가적인 서버 과부하 방지**

---

### 🎯 **4. 캐싱 (Caching)**

**🔹 스프링에서 어떻게 적용할까?**  
트래픽을 줄이기 위해 **Spring Cache**를 활용하여 **Redis, Caffeine** 등의 캐시 저장소를 이용
# Redis - 메모리 기반 키-밸류 저장소
|특징|설명|
|---|---|
|**인메모리 DB**|데이터를 **RAM에 저장**하여 매우 빠른 속도 제공|
|**Key-Value 저장소**|NoSQL 기반의 **Key-Value** 데이터 구조|
|**데이터 지속성**|데이터를 **디스크에 저장하여 영구 보관 가능 (RDB, AOF)**|
|**고성능**|**읽기/쓰기 속도가 빠르고, 높은 동시성 처리 가능**|
|**다양한 자료구조 지원**|String, List, Set, Hash, Sorted Set 등|
```Java
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class UserService {

    private final UserRepository userRepository;

    public UserService(UserRepository userRepository) {
        this.userRepository = userRepository;
    }

    @Cacheable(value = "user", key = "#userId") // Redis 캐싱 적용
    public User getUser(String userId) {
        System.out.println("DB에서 데이터를 가져옵니다...");
        return userRepository.findById(userId).orElseThrow();
    }
}

```
- 어노테이션을 통한 저장
- `"user::123"` → `{id: 123, name: "형님"}`

```java
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.cache.RedisCacheConfiguration;
import org.springframework.data.redis.connection.RedisConnectionFactory;
import org.springframework.data.redis.cache.RedisCacheManager;

import java.time.Duration;

@Configuration
@EnableCaching
public class RedisCacheConfig {

    @Bean
    public RedisCacheManager cacheManager(RedisConnectionFactory redisConnectionFactory) {
        return RedisCacheManager.builder(redisConnectionFactory)
                .cacheDefaults(RedisCacheConfiguration.defaultCacheConfig()
                        .entryTtl(Duration.ofMinutes(10))) // 캐시 TTL: 10분
                .build();
    }
}

```
- 10분만 캐시로 가지고 있도록 하는 설정 

# **Redis vs DB 성능 차이**

| 비교 항목       | Redis (In-Memory)    | 일반 DB (MySQL, PostgreSQL) |
| ----------- | -------------------- | ------------------------- |
| **저장 위치**   | RAM(메모리)             | 디스크(SSD/HDD)              |
| **응답 속도**   | **1~2ms** (초고속)      | 50~100ms (상대적으로 느림)       |
| **트랜잭션 지원** | 지원하지만 약함             | 강력한 ACID 지원               |
| **주 용도**    | **캐싱, 세션 저장, 메시지 큐** | **데이터 저장, 검색**            |

---

# 🎯 **5. CDN(Content Delivery Network)**

설명을 들으면 이건 뭐 CDN은 뭐 내가 직접 설치를 하라는건가?? 이건 또 누가 할건데 싶을 것이다.. 그렇데 또마존이 하는 일이다.
# **1. AWS CloudFront (AWS의 CDN 서비스)**

✔ **AWS CloudFront는 AWS에서 제공하는 CDN 서비스**  
✔ **정적 리소스를 AWS S3(스토리지)와 연계하여 배포 가능**  
✔ **전 세계 AWS 엣지 로케이션(Edge Location)을 통해 빠르게 콘텐츠 제공**

📌 **AWS CloudFront + S3 적용 방식**
 [클라이언트  →  CloudFront (CDN) →  S3 (정적 리소스 저장소)]

# **2. Nginx를 활용한 정적 파일 캐싱**
```
server { 
	listen 80;
	server_name example.com;
	location /static/ {
		root /var/www/html;
		expires 1d; # 1일 동안 캐시 유지 
	} 
}
```
- 이러면 /static/ 경로에서 제공하는 정적 파일은 Nginx가 캐싱함!

![[Pasted image 20250220172900.png]]


---

# 🎯 **6. 비동기 처리 (Async Processing)**

# **1. Spring @Async란?**

✔ **Spring에서 제공하는 비동기(Asynchronous) 처리 기능**  
✔ **메서드를 백그라운드에서 실행**하여 **메인 쓰레드 블로킹 없이 처리 가능**  
✔ **CPU 부하가 높은 작업, 네트워크 요청, 파일 I/O 작업** 등에 활용

📌 **Spring @Async 적용 효과**

|처리 방식|설명|
|---|---|
|**동기(Sync) 처리**|하나의 요청을 처리하는 동안 다음 요청은 대기|
|**비동기(Async) 처리**|요청을 백그라운드에서 실행하여 빠른 응답 가능|

✅ **결론**
- 동기 방식은 **요청마다 차례로 실행**되기 때문에 **처리가 오래 걸리는 작업이 있으면 대기 시간이 길어짐**
- 비동기 방식(`@Async`)을 사용하면 **백그라운드에서 처리하면서 빠르게 응답 가능**

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableAsync;

@Configuration
@EnableAsync // 비동기 기능 활성화
public class AsyncConfig {
}

```
- @Aync를 적용하기 위해서는 붙여줘야함

```java
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.concurrent.CompletableFuture;

@Service
public class AsyncService {

    @Async
    public CompletableFuture<String> processTask() {
        try {
            Thread.sleep(5000); // 오래 걸리는 작업 (예: 외부 API 호출)
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        return CompletableFuture.completedFuture("작업 완료");
    }
}
```
- `@Async`를 붙이면 해당 메서드는 **별도의 쓰레드에서 실행**
- `CompletableFuture<String>`을 사용하여 **비동기 결과 반환 가능**
- `Thread.sleep(5000)` → **실제 서비스에서는 DB 조회, API 호출 등의 작업이 들어감**

📌 **관련 기술**
- <mark style="background: #FFF3A3A6;"> **Spring @Async**</mark>
- **Apache Kafka / RabbitMQ**
- **Spring Batch (대량 데이터 처리)**

---
#  **8. 미리 준비된 응답 (Graceful Degradation)**

**🔹 스프링에서 어떻게 적용할까?**  
트래픽이 폭주할 경우, **임시 페이지를 보여주는 Fallback 처리**

📌 **Fallback API 예제**

java

복사편집

`@GetMapping("/search") public ResponseEntity<?> search(@RequestParam String keyword) {     if (serverLoadHigh) {         return ResponseEntity.status(HttpStatus.SERVICE_UNAVAILABLE)             .body("현재 검색 서비스가 과부하 상태입니다. 나중에 다시 시도해주세요.");     }     return ResponseEntity.ok(searchService.search(keyword)); }`

📌 **적용 효과**

- 특정 기능을 **일시적으로 비활성화**하여 **전체 서비스 다운을 방지**

📌 **관련 기술**

- **Spring Boot Fallback API**
- **Error Page 처리**
