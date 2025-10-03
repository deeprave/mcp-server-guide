# Groovy Guidelines (Testing Focus)

## Project Structure

**Standard Groovy test layout:**

```
root/
├── build.gradle / pom.xml
├── src/
│   ├── main/java/
│   │   └── com/example/
│   └── test/groovy/
│       └── com/example/
│           ├── unit/
│           └── integration/
├── README.md
└── .gitignore
```

## Dependencies & Setup

**Groovy 3.x with Spock framework:**

```gradle
dependencies {
    testImplementation 'org.codehaus.groovy:groovy-all:3.0.19'
    testImplementation 'org.spockframework:spock-core:2.3-groovy-3.0'
    testImplementation 'org.spockframework:spock-spring:2.3-groovy-3.0'
    testImplementation 'cglib:cglib-nodep:3.3.0'  // For mocking
}
```

## Spock Framework Patterns

**BDD-style specifications:**

```groovy
// Good - Spock specification structure
class UserServiceSpec extends Specification {

    UserRepository userRepository = Mock()
    EmailService emailService = Mock()
    UserService userService = new UserService(userRepository, emailService)

    def "should create user with valid data"() {
        given: "a valid user request"
        def request = new CreateUserRequest(
            name: "John Doe",
            email: "john@example.com"
        )
        def savedUser = new User(id: UUID.randomUUID(), name: "John Doe")

        when: "creating the user"
        def result = userService.createUser(request)

        then: "user is saved and email is sent"
        1 * userRepository.save(_ as User) >> savedUser
        1 * emailService.sendWelcomeEmail("john@example.com")
        result.name == "John Doe"
    }

    def "should throw exception for invalid email"() {
        given: "invalid email"
        def request = new CreateUserRequest(name: "John", email: "invalid")

        when: "creating user"
        userService.createUser(request)

        then: "validation exception is thrown"
        thrown(ValidationException)
        0 * userRepository.save(_)
    }
}

// Good - Parameterized tests with data tables
class ValidationSpec extends Specification {

    def "should validate email format"() {
        expect: "email validation returns expected result"
        EmailValidator.isValid(email) == expected

        where: "testing various email formats"
        email                    | expected
        "valid@example.com"      | true
        "user.name@domain.co.uk" | true
        "invalid.email"          | false
        "missing@.com"           | false
        ""                       | false
        null                     | false
    }
}
```

## Dynamic Test Data Creation

**Leverage Groovy's flexibility:**

```groovy
// Good - Dynamic object creation
class TestDataBuilder {

    static User.UserBuilder aUser() {
        return User.builder()
            .id(UUID.randomUUID())
            .name("Test User")
            .email("test@example.com")
            .createdAt(LocalDateTime.now())
    }

    static CreateUserRequest aUserRequest(Map overrides = [:]) {
        def defaults = [
            name: "John Doe",
            email: "john@example.com",
            age: 30
        ]
    }
}

// Usage in tests
def "should handle different user ages"() {
    given:
    def youngUser = aUserRequest(age: 18)
    def oldUser = aUserRequest(age: 65)

    expect:
    userService.isEligible(youngUser) == true
    userService.isEligible(oldUser) == false
}
```

## Collection Operations & Assertions

**Use Groovy's powerful collection features:**

```groovy
// Good - Collection operations in tests
def "should filter active users"() {
    given: "a mix of active and inactive users"
    def users = [
        new User(name: "John", active: true),
        new User(name: "Jane", active: false),
        new User(name: "Bob", active: true)
    ]

    when: "filtering active users"
    def activeUsers = userService.getActiveUsers(users)

    then: "only active users are returned"
    activeUsers.size() == 2
    activeUsers.every { it.active }
    activeUsers*.name.containsAll(["John", "Bob"])
}

// Good - Complex assertions with closures
def "should have valid user data"() {
    when:
    def users = userService.getAllUsers()

    then:
    users.every { user ->
        user.name != null &&
        user.email.contains("@") &&
        user.createdAt.isBefore(LocalDateTime.now())
    }
}
```

## String Interpolation & GStrings

**Readable test descriptions and assertions:**

```groovy
// Good - GString interpolation for dynamic messages
def "should calculate discount for $customerType customer"() {
    given: "a $customerType customer with purchase amount $amount"
    def customer = new Customer(type: customerType, purchaseAmount: amount)

    when: "calculating discount"
    def discount = discountService.calculate(customer)

    then: "discount should be $expectedDiscount"
    discount == expectedDiscount

    where:
    customerType | amount | expectedDiscount
    "PREMIUM"    | 100    | 10
    "REGULAR"    | 100    | 5
    "NEW"        | 100    | 15
}

// Good - Multi-line strings for complex test data
def "should parse complex JSON"() {
    given: "complex JSON data"
    def jsonData = """
        {
            "users": [
                {"name": "John", "roles": ["USER", "ADMIN"]},
                {"name": "Jane", "roles": ["USER"]}
            ],
            "metadata": {
                "version": "1.0",
                "timestamp": "${LocalDateTime.now()}"
            }
        }
    """

    when: "parsing the JSON"
    def result = jsonParser.parse(jsonData)

    then: "data is correctly parsed"
    result.users.size() == 2
    result.metadata.version == "1.0"
}
```

## Mock & Stub Patterns

**Flexible mocking with Groovy syntax:**

```groovy
// Good - Spock mocks with closures
def "should process users with callback"() {
    given:
    def processor = Mock(UserProcessor)
    def callback = Mock(Closure)

    when:
    userService.processUsers([user1, user2], callback)

    then:
    2 * processor.process(_ as User) >> { User user ->
        // Custom mock behavior
        if (user.name == "John") {
            throw new ProcessingException("Cannot process John")
        }
        return "Processed: ${user.name}"
    }
    1 * callback.call("Processing complete")
}

// Good - Stub with multiple return values
def "should handle service failures gracefully"() {
    given:
    def externalService = Stub(ExternalService)
    externalService.fetchData(_) >>> [
        "success",           // First call succeeds
        { throw new RuntimeException("Service down") }, // Second call fails
        "recovered"          // Third call succeeds
    ]

    expect:
    resilientService.getData("key1") == "success"
    resilientService.getData("key2") == "fallback"  // Handles exception
    resilientService.getData("key3") == "recovered"
}
```

## Integration Testing

**Spring Boot integration with Spock:**

```groovy
@SpringBootTest
@TestPropertySource(properties = ["spring.datasource.url=jdbc:h2:mem:testdb"])
class UserControllerIntegrationSpec extends Specification {

    @Autowired
    TestRestTemplate restTemplate

    @Autowired
    UserRepository userRepository

    def cleanup() {
        userRepository.deleteAll()
    }

    def "should create user via REST API"() {
        given: "a user creation request"
        def request = [
            name: "John Doe",
            email: "john@example.com"
        ]

        when: "posting to user endpoint"
        def response = restTemplate.postForEntity("/api/users", request, Map)

        then: "user is created successfully"
        response.statusCode.is2xxSuccessful()
        response.body.name == "John Doe"

        and: "user exists in database"
        def savedUser = userRepository.findByEmail("john@example.com")
        savedUser.isPresent()
        savedUser.get().name == "John Doe"
    }
}
```

## Error Handling & Edge Cases

**Comprehensive error testing:**

```groovy
// Good - Exception testing with detailed assertions
def "should handle various error scenarios"() {
    when: "calling service with invalid input"
    userService.processUser(input)

    then: "appropriate exception is thrown"
    def ex = thrown(expectedException)
    ex.message.contains(expectedMessage)
    ex.cause?.class == expectedCause

    where:
    input           | expectedException        | expectedMessage | expectedCause
    null            | IllegalArgumentException | "cannot be null" | null
    ""              | ValidationException      | "cannot be empty" | null
    "invalid-email" | ValidationException      | "invalid format" | null
}

// Good - Conditional testing with Groovy truth
def "should validate user based on conditions"() {
    expect: "validation result matches expectation"
    userValidator.isValid(user) == expected

    where:
    user                                    | expected
    new User(name: "John", email: "j@e.c") | true
    new User(name: "", email: "j@e.c")     | false
    new User(name: "John", email: "")      | false
    null                                    | false
}
```

## Performance Testing Patterns

**Load and performance testing with Groovy:**

```groovy
// Good - Performance testing with timing
def "should process large datasets efficiently"() {
    given: "large dataset"
    def users = (1..10000).collect {
        new User(name: "User$it", email: "user$it@example.com")
    }

    when: "processing all users"
    def start = System.currentTimeMillis()
    def result = userService.processUsers(users)
    def duration = System.currentTimeMillis() - start

    then: "processing completes within time limit"
    result.size() == 10000
    duration < 5000  // Less than 5 seconds
}

// Good - Memory usage testing
def "should not cause memory leaks"() {
    given: "initial memory state"
    System.gc()
    def initialMemory = Runtime.runtime.totalMemory() - Runtime.runtime.freeMemory()

    when: "performing memory-intensive operations"
    (1..1000).each {
        userService.createAndProcessUser("User$it")
    }

    then: "memory usage remains reasonable"
    System.gc()
    def finalMemory = Runtime.runtime.totalMemory() - Runtime.runtime.freeMemory()
    (finalMemory - initialMemory) < 50_000_000  // Less than 50MB increase
}
```

## Key Principles

1. **BDD structure** - Use given/when/then for clear test organization
2. **Dynamic data** - Leverage Groovy's flexibility for test data creation
3. **Readable assertions** - Use collection operations and closures for expressive tests
4. **Parameterized testing** - Use data tables for comprehensive test coverage
5. **Flexible mocking** - Use Spock's powerful mocking capabilities
6. **String interpolation** - Use GStrings for dynamic test descriptions
7. **Integration friendly** - Combine with Spring Boot for full-stack testing
8. **Performance aware** - Include timing and memory considerations in tests
   }

// Usage in tests
def "should handle different user ages"() {
given:
def youngUser = aUserRequest(age: 18)
def oldUser = aUserRequest(age: 65)

expect:
userService.isEligible(youngUser) == true
userService.isEligible(oldUser) == false
}

```

## Collection Operations & Assertions
**Use Groovy's powerful collection features:**
```groovy
// Good - Collection operations in tests
def "should filter active users"() {
    given: "a mix of active and inactive users"
    def users = [
        new User(name: "John", active: true),
        new User(name: "Jane", active: false),
        new User(name: "Bob", active: true)
    ]

    when: "filtering active users"
    def activeUsers = userService.getActiveUsers(users)

    then: "only active users are returned"
    activeUsers.size() == 2
    activeUsers.every { it.active }
    activeUsers*.name.containsAll(["John", "Bob"])
}

// Good - Complex assertions with closures
def "should have valid user data"() {
    when:
    def users = userService.getAllUsers()

    then:
    users.every { user ->
        user.name != null &&
        user.email.contains("@") &&
        user.createdAt.isBefore(LocalDateTime.now())
    }
}
```
```

```
