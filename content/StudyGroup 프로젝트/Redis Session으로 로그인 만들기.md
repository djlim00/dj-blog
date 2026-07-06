---
title: "[studygroup] 1. Redis Session으로 로그인 만들기"
publish: true
created: 2026-07-03T14:56:45+09:00
modified: 2026-07-05T16:17:27+09:00
cover: pasted-image-20260703151507.png
---
## Prologue
- Redis를 통한 로그인 구현
- Redis 세션 사용시 설정 주의점

  
이미 JWT를 통해 토큰 기반으로 RDB에 저장을 하는 방법은 많이 해보셨을 터인데,
Redis를 로그인에 적용하면 어떤 점에서 좋은 걸까요?

1. 서버가 여러 대여도 로그인이 유지
2. 재배포해도 사용자가 튕기지 않아야 함

이번 글을 실제로 제가 어떻게 구현했는지, 어떤 것들을 조심했는지를 작성했습니다.

아래 코드는 전부 실제로 이번 프로젝트에 작성된 코드들입니다!
  
---  
  
## Part 1. Redis를 통한 로그인 구현  세팅
  
### 세션 로그인 흐름
  
일반적인 세션 로그인 흐름을 그대로 따르되, 저장소만 Redis로 사용한다고 보면 됩니다
  
1. 사용자가 `/api/auth/login`으로 아이디/비밀번호 제출  
2. 서비스가 자격 증명 검증 
3. 인증 정보(`Authentication`)를 `SecurityContext`에 심는다  
4. `SecurityContextRepository`가 이걸 세션에 저장  
5. Spring Session이 세션을 Redis에 `HSET`으로 저장하고 `EXPIRE`를 건다  
6. 응답의 `Set-Cookie: SESSION=...`로 세션 ID를 클라이언트에 전달  
  
  
### 의존성  
  
```kotlin  
implementation("org.springframework.boot:spring-boot-starter-web")  
implementation("org.springframework.boot:spring-boot-starter-security")  
implementation("org.springframework.session:spring-session-data-redis")  
```  
  
- build.gradle.kts에 다음과 같이 가져오면 끝!
  
### application.yaml  
  
```yaml  
spring:
  data:
    redis:
      host: localhost
      port: 6379
  session:
    timeout: 30m
    redis:
      namespace: spring:session
      flush-mode: on_save
```  
  
Redis 위치만 알려주면 Spring Boot 자동 배선이 세션 저장소를 Redis로 설정합니다.

  
### SecurityConfig  
  
```java hl:10-11,20-22
@Bean
public SecurityFilterChain securityFilterChain(
        HttpSecurity http,
        SecurityContextRepository securityContextRepository) throws Exception {

    http
        .csrf(AbstractHttpConfigurer::disable)
        .formLogin(AbstractHttpConfigurer::disable)
        .httpBasic(AbstractHttpConfigurer::disable)
        .sessionManagement(s -> s.sessionCreationPolicy(SessionCreationPolicy.IF_REQUIRED))
        .securityContext(c -> c.securityContextRepository(securityContextRepository))
        .authorizeHttpRequests(auth -> auth
            .requestMatchers("/api/auth/signup", "/api/auth/login").permitAll()
            .anyRequest().authenticated());

    return http.build();
}

@Bean
public SecurityContextRepository securityContextRepository() {
    return new HttpSessionSecurityContextRepository();
}
```  
  
-  `SecurityContext`를 세션 attribute (`SPRING_SECURITY_CONTEXT` 키)에 넣고 뺌
	- Spring Session이 활성화된 상태면 이 attribute가 자동으로 Redis Hash에 저장

  
### 로그인 컨트롤러  
  
```java hl:14-17
@PostMapping("/login")
public UserResponse login(
        @Valid @RequestBody SignInRequest request,
        HttpServletRequest servletRequest,
        HttpServletResponse servletResponse) {

    User user = userService.authenticate(request.username(), request.password());

    LoginUser loginUser = new LoginUser(user.getId(), user.getUsername());
    Authentication authToken = UsernamePasswordAuthenticationToken.authenticated(
            loginUser, null, List.of(new SimpleGrantedAuthority("ROLE_USER"))
    );

    SecurityContext context = SecurityContextHolder.createEmptyContext();
    context.setAuthentication(authToken);
    SecurityContextHolder.setContext(context);
    securityContextRepository.saveContext(context, servletRequest, servletResponse);

    return UserResponse.from(user);
}
```  
  
- `securityContextRepository.saveContext(...)` 을 하게 되면 세션에 `SecurityContext`가 얹히고, 요청이 끝날 때 Spring Session이 세션 전체를 Redis에 커밋함
  
- 위의 코드에서는 Principal 자리에 `Long userId`가 아니라 `LoginUser` record를 통째로 담는데..
	- <mark class="hltr-yellow">이것으로 인해서 아래의 문제가 발생했습니다(500에러)</mark>
  
### 확인 

저는 클로드 코드에 간단한 로그인 UI를 만들어달라고 했습니다.

![[Pasted image 20260703151507.png|437]]

- <mark class="hltr-yellow">로그인을 하고 세션이 잘 생성됐는지 확인해보겠습니다</mark>

![[Pasted image 20260703151442.png|717]]

- 그럼 짠! 하고 저의 로그인 세션이 생성된 것을 확인할 수 있습니다
  
---  
  
## Part 2. 발생했던 문제 트러블 슈팅
  
  
### 1. record는 자동으로 Serializable이 아니다 (500 에러 발생..)  
  
저는 세션에 담을 principal을`LoginUser`라는 record로 만들뒀었습니다.
  
```java  
public record LoginUser(Long id, String username) {}  
```  
  
근데 이게 웬걸?
로그인 요청 → **500 Internal Server Error** 가 뜨는거 아니겠습니까?
  
```  
java.io.NotSerializableException: com.studygroup.auth.LoginUser  
```  
  
- Spring Session Redis의 기본 직렬화기는 `JdkSerializationRedisSerializer`
	- 세션에 담기는 모든 객체가 `Serializable`을 구현해야 합니다.
  
여기서 record가 문제가 됩니다.
- record는 컴포넌트가 모두 Serializable이라도 자기 자신은 자동으로 Serializable이 되지 않습니다
	- 따라서 명시적으로 Serializable을 구현해야합니다.
  
```java  
// 명시적으로 Serializable 구현
public record LoginUser(Long id, String username) implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;
} 
```  
  
- Spring Security의 기본 principal 타입(`UserDetails`, `org.springframework.security.core.userdetails.User` 등)은 이미 Serializable을 구현하고 있어서 자동으로 문제가 생기지 않아요
	- <mark class="hltr-yellow">그러나 커스텀 principal을 쓰면 이 문제가 발생할 수 있습니다</mark>

  
### 2. 세션 TTL 조회하다가 세션이 리셋되는 문제

![[Pasted image 20260703173013.png]]

위 처럼 세션 남은 시간을 UI에 표시하고 싶어서 엔드포인트를 만들었는데요.
처음엔 아래처럼  `HttpSession` API로 계산했습니다.
  
```java  
// 문제: getSession() 호출 자체가 세션 접근이라 TTL이 리셋됨
HttpSession session = request.getSession(false);
long remaining = session.getLastAccessedTime()
              + session.getMaxInactiveInterval() * 1000L
              - System.currentTimeMillis(); 
```  
  
- 근데 여기서 `request.getSession(...)`을 호출하는 것 자체가 세션 접근으로 간주되어, `lastAccessedTime`이 갱신되버립니다.
- 특히 UI가 1초마다 이 엔드포인트를 폴링하면, TTL이 영원히 리셋되어 세션이 만료되지 않았습니다
  
**회피**: Spring Session의 추상을 벗기고 Redis에 직접 `TTL` 명령을 날린다.  
  
```java  
// 수정: Redis에 TTL 명령만 직접 조회
@GetMapping("/session")
public SessionInfoResponse session(
        @RequestUser LoginUser loginUser,
        HttpServletRequest request) {

    HttpSession session = request.getSession(false);
    if (session == null) throw new InvalidCredentialsException();

    String key = sessionNamespace + ":sessions:" + session.getId();
    Long ttl = redisTemplate.getExpire(key, TimeUnit.SECONDS);
    long remaining = (ttl != null && ttl > 0) ? ttl : 0L;

    return new SessionInfoResponse(session.getId(), session.getMaxInactiveInterval(), remaining);
}
```  
  
`redisTemplate.getExpire(...)`는 Redis에 `TTL` 명령만 보낼 뿐, 세션 attribute를 건드리지 않는다. `lastAccessedTime`이 유지되고, 조회는 관찰로만 남는다.  
  
교훈: **Spring Session이 만들어주는 추상은 편리하지만, "이 API 호출이 세션 상태를 바꾸는가?"라는 질문에는 자동으로 답해주지 않는다.** 순수 관찰이 필요할 땐 밑에 있는 Redis에 직접 물어보는 게 정직하다.  


- 서버가 다중일 떄, Redis 클러스터링 세팅+서버간 데이터 동기화
	- 아키텍처적으로 고민을 하는게 중요하다
	- 왜 이런 방법으로 동기화를 했을까?
	- 이론의 적용
	- 서버 하나를 죽였을 떄, 다른게 리더가 되서, 

=> <mark class="hltr-yellow"> Redis를 HA 구조로 세팅</mark> 했다는 말이 이력서에 들어있는 것이 좋다!