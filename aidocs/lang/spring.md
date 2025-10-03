# Spring Framework Guidelines

## Project Structure
**Standard Spring Boot layout:**
```
root/
├── build.gradle(.kts) / pom.xml
├── src/
│   ├── main/
│   │   ├── java/kotlin/
│   │   │   └── com/example/
│   │   │       ├── Application.java/kt     # Spring Boot only
│   │   │       ├── config/
│   │   │       ├── controller/
│   │   │       ├── service/
│   │   │       └── repository/
│   │   └── resources/
│   │       ├── application.yml             # Spring Boot only
│   │       └── static/
│   └── test/
├── README.md
└── .gitignore
```

## Configuration & Setup
**Prefer annotation-based configuration:**
```java
// Good - Component scanning with annotations
@Configuration
@ComponentScan(basePackages = "com.example")
@EnableJpaRepositories("com.example.repository")
public class AppConfig {

    @Bean
    @Primary
    public DataSource dataSource() {
        return new HikariDataSource(config);
    }
}

// Spring Boot - Auto-configuration (Boot-specific)
@SpringBootApplication  // Combines @Configuration, @EnableAutoConfiguration, @ComponentScan
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

// Avoid - XML configuration for new projects
<!-- Don't use XML config unless legacy requirements -->
<bean id="userService" class="com.example.UserService"/>
```

## Dependency Injection
**Use constructor injection and immutable components:**
```java
// Good - Constructor injection (works in Java/Kotlin)
@Service
public class UserService {
    private final UserRepository userRepository;
    private final EmailService emailService;

    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
}

// Good - Kotlin with constructor injection
@Service
class UserService(
    private val userRepository: UserRepository,
    private val emailService: EmailService
) {
    // Implementation
}

// Avoid - Field injection
@Service
public class UserService {
    @Autowired
    private UserRepository userRepository; // Harder to test, mutable
}
```

**Component lifecycle and scoping:**
```java
// Good - Explicit scoping when needed
@Service
@Scope("prototype")  // New instance per injection
public class StatefulService {
    // Implementation
}

// Good - Lifecycle methods
@Component
public class DatabaseInitializer {

    @PostConstruct
    public void initialize() {
        // Setup logic after dependency injection
    }

    @PreDestroy
    public void cleanup() {
        // Cleanup before shutdown
    }
}
```

## Web Layer (Spring MVC)
**RESTful controller design:**
```java
// Good - RESTful endpoints with proper HTTP methods
@RestController
@RequestMapping("/api/users")
@Validated
public class UserController {

    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @GetMapping("/{id}")
    public ResponseEntity<UserDto> getUser(@PathVariable @Valid UUID id) {
        return userService.findById(id)
            .map(user -> ResponseEntity.ok(user))
            .orElse(ResponseEntity.notFound().build());
    }

    @PostMapping
    public ResponseEntity<UserDto> createUser(@RequestBody @Valid CreateUserRequest request) {
        UserDto created = userService.create(request);
        return ResponseEntity.status(HttpStatus.CREATED).body(created);
    }
}

// Good - Global exception handling
@ControllerAdvice
public class GlobalExceptionHandler {

    @ExceptionHandler(ValidationException.class)
    public ResponseEntity<ErrorResponse> handleValidation(ValidationException ex) {
        return ResponseEntity.badRequest()
            .body(new ErrorResponse("VALIDATION_ERROR", ex.getMessage()));
    }
}
```

**Request/Response handling:**
```java
// Good - DTOs for API boundaries
public record CreateUserRequest(
    @NotBlank String name,
    @Email String email,
    @Valid AddressDto address
) {}

public record UserDto(
    UUID id,
    String name,
    String email,
    LocalDateTime createdAt
) {}

// Good - Validation groups for different scenarios
public class UserValidation {
    public interface Create {}
    public interface Update {}
}

@NotNull(groups = UserValidation.Create.class)
@Null(groups = UserValidation.Update.class)
private UUID id;
```

## Data Access Layer
**Spring Data JPA patterns:**
```java
// Good - Repository interfaces with custom queries
@Repository
public interface UserRepository extends JpaRepository<User, UUID> {

    @Query("SELECT u FROM User u WHERE u.email = :email AND u.active = true")
    Optional<User> findActiveByEmail(@Param("email") String email);

    @Modifying
    @Query("UPDATE User u SET u.lastLogin = :loginTime WHERE u.id = :id")
    void updateLastLogin(@Param("id") UUID id, @Param("loginTime") LocalDateTime loginTime);

    // Method name queries
    List<User> findByDepartmentAndActiveTrue(String department);
}

// Good - Entity design
@Entity
@Table(name = "users", indexes = @Index(columnList = "email"))
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.UUID)
    private UUID id;

    @Column(nullable = false, unique = true)
    private String email;

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;

    // Constructors, getters, setters
}
```

**Transaction management:**
```java
// Good - Declarative transactions
@Service
@Transactional(readOnly = true)  // Default for all methods
public class UserService {

    @Transactional  // Override for write operations
    public User createUser(CreateUserRequest request) {
        User user = new User(request.name(), request.email());
        User saved = userRepository.save(user);
        emailService.sendWelcomeEmail(saved.getEmail());
        return saved;
    }

    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void auditUserAction(UUID userId, String action) {
        // Always runs in new transaction
        auditRepository.save(new AuditLog(userId, action));
    }
}

// Avoid - Programmatic transaction management unless necessary
@Autowired
private PlatformTransactionManager transactionManager;
```

## Configuration Management
**Externalized configuration:**
```yaml
# application.yml (Spring Boot)
spring:
  datasource:
    url: ${DATABASE_URL:jdbc:h2:mem:testdb}
    username: ${DATABASE_USER:sa}
    password: ${DATABASE_PASSWORD:}

  jpa:
    hibernate:
      ddl-auto: ${DDL_AUTO:validate}
    show-sql: ${SHOW_SQL:false}

server:
  port: ${PORT:8080}

app:
  jwt:
    secret: ${JWT_SECRET}
    expiration: ${JWT_EXPIRATION:3600}
```

```java
// Good - Configuration properties (Spring Boot)
@ConfigurationProperties(prefix = "app.jwt")
@ConstructorBinding  // Immutable configuration
public record JwtProperties(
    String secret,
    Duration expiration,
    String issuer
) {}

// Good - Profile-specific configuration
@Configuration
@Profile("production")
public class ProductionConfig {

    @Bean
    public CacheManager cacheManager() {
        return new RedisCacheManager(redisConnectionFactory());
    }
}
```

## Security
**Spring Security configuration:**
```java
// Good - Security configuration
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    private final JwtAuthenticationEntryPoint jwtAuthenticationEntryPoint;
    private final JwtRequestFilter jwtRequestFilter;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        return http
            .csrf(csrf -> csrf.disable())
            .sessionManagement(session ->
                session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
            .authorizeHttpRequests(auth -> auth
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/actuator/health").permitAll()  // Spring Boot
                .requestMatchers("/api/admin/**").hasRole("ADMIN")
                .anyRequest().authenticated())
            .exceptionHandling(ex ->
                ex.authenticationEntryPoint(jwtAuthenticationEntryPoint))
            .addFilterBefore(jwtRequestFilter, UsernamePasswordAuthenticationFilter.class)
            .build();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder(12);
    }
}

// Good - Method-level security
@Service
public class UserService {

    @PreAuthorize("hasRole('ADMIN') or #userId == authentication.principal.id")
    public User updateUser(UUID userId, UpdateUserRequest request) {
        // Implementation
    }
}
```

## Testing
**Comprehensive testing strategy:**
```java
// Good - Unit tests with mocks
@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    @Mock
    private UserRepository userRepository;

    @Mock
    private EmailService emailService;

    @InjectMocks
    private UserService userService;

    @Test
    void shouldCreateUserSuccessfully() {
        // Given
        CreateUserRequest request = new CreateUserRequest("John", "john@example.com");
        User savedUser = new User("John", "john@example.com");
        when(userRepository.save(any(User.class))).thenReturn(savedUser);

        // When
        User result = userService.createUser(request);

        // Then
        assertThat(result.getName()).isEqualTo("John");
        verify(emailService).sendWelcomeEmail("john@example.com");
    }
}

// Good - Integration tests (Spring Boot)
@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
@Testcontainers
class UserControllerIntegrationTest {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:15")
            .withDatabaseName("testdb")
            .withUsername("test")
            .withPassword("test");

    @Autowired
    private TestRestTemplate restTemplate;

    @Test
    void shouldCreateUserViaApi() {
        CreateUserRequest request = new CreateUserRequest("John", "john@example.com");

        ResponseEntity<UserDto> response = restTemplate.postForEntity(
            "/api/users", request, UserDto.class);

        assertThat(response.getStatusCode()).isEqualTo(HttpStatus.CREATED);
        assertThat(response.getBody().name()).isEqualTo("John");
    }
}

// Good - Repository tests
@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private TestEntityManager entityManager;

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldFindActiveUserByEmail() {
        // Given
        User user = new User("John", "john@example.com");
        user.setActive(true);
        entityManager.persistAndFlush(user);

        // When
        Optional<User> found = userRepository.findActiveByEmail("john@example.com");

        // Then
        assertThat(found).isPresent();
        assertThat(found.get().getName()).isEqualTo("John");
    }
}
```

## Monitoring & Production (Spring Boot)
**Actuator and observability:**
```yaml
# Spring Boot Actuator configuration
management:
  endpoints:
    web:
      exposure:
        include: health,info,metrics,prometheus
  endpoint:
    health:
      show-details: when-authorized
  metrics:
    export:
      prometheus:
        enabled: true
```

```java
// Good - Custom health indicators (Spring Boot)
@Component
public class DatabaseHealthIndicator implements HealthIndicator {

    private final DataSource dataSource;

    @Override
    public Health health() {
        try (Connection connection = dataSource.getConnection()) {
            if (connection.isValid(1)) {
                return Health.up()
                    .withDetail("database", "Available")
                    .build();
            }
        } catch (SQLException ex) {
            return Health.down()
                .withDetail("database", "Unavailable")
                .withException(ex)
                .build();
        }
        return Health.down().build();
    }
}

// Good - Custom metrics
@Service
public class UserService {

    private final MeterRegistry meterRegistry;
    private final Counter userCreationCounter;

    public UserService(MeterRegistry meterRegistry) {
        this.meterRegistry = meterRegistry;
        this.userCreationCounter = Counter.builder("users.created")
            .description("Number of users created")
            .register(meterRegistry);
    }

    public User createUser(CreateUserRequest request) {
        Timer.Sample sample = Timer.start(meterRegistry);
        try {
            User user = // ... creation logic
            userCreationCounter.increment();
            return user;
        } finally {
            sample.stop(Timer.builder("user.creation.time")
                .description("User creation time")
                .register(meterRegistry));
        }
    }
}
```

## Performance & Best Practices
**Caching and optimization:**
```java
// Good - Declarative caching
@Service
public class UserService {

    @Cacheable(value = "users", key = "#id")
    public Optional<User> findById(UUID id) {
        return userRepository.findById(id);
    }

    @CacheEvict(value = "users", key = "#user.id")
    public User updateUser(User user) {
        return userRepository.save(user);
    }

    @Caching(evict = {
        @CacheEvict(value = "users", key = "#user.id"),
        @CacheEvict(value = "userStats", allEntries = true)
    })
    public void deleteUser(User user) {
        userRepository.delete(user);
    }
}

// Good - Async processing
@Service
public class NotificationService {

    @Async("taskExecutor")
    public CompletableFuture<Void> sendNotificationAsync(String email, String message) {
        // Send notification
        return CompletableFuture.completedFuture(null);
    }
}

@Configuration
@EnableAsync
public class AsyncConfig {

    @Bean("taskExecutor")
    public TaskExecutor taskExecutor() {
        ThreadPoolTaskExecutor executor = new ThreadPoolTaskExecutor();
        executor.setCorePoolSize(5);
        executor.setMaxPoolSize(10);
        executor.setQueueCapacity(100);
        executor.setThreadNamePrefix("async-");
        executor.initialize();
        return executor;
    }
}
```

## Key Principles
1. **Constructor injection** - Prefer immutable dependencies over field injection
2. **Configuration over XML** - Use annotations and Java/Kotlin config classes
3. **Externalized configuration** - Use profiles and environment-specific properties
4. **Declarative approach** - Leverage annotations for transactions, caching, security
5. **Proper layering** - Separate concerns with controller/service/repository layers
6. **Comprehensive testing** - Unit tests with mocks, integration tests with test slices
7. **Production ready** - Use Actuator for monitoring, proper error handling
8. **Performance aware** - Use caching, async processing, and connection pooling appropriately
