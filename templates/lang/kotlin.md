# Kotlin Guidelines

## Project Structure
**Standard Gradle/Maven layout:**
```
root/
├── build.gradle.kts / pom.xml
├── src/
│   ├── main/kotlin/
│   │   └── com/example/
│   └── test/kotlin/
│       └── com/example/
├── README.md
└── .gitignore
```

## Formatting & Quality
- **Use ktlint or detekt** - address warnings before considering complete
- **Prefer Gradle Kotlin DSL** (`build.gradle.kts`) over Groovy
- **Use explicit types** only when needed for clarity
- **Follow Kotlin coding conventions**

## Modern Syntax & Idioms
**Data classes for immutable data:**
```kotlin
// Good - Data class with validation
data class Person(
    val name: String,
    val age: Int,
    val hobbies: List<String> = emptyList()
) {
    init {
        require(name.isNotBlank()) { "Name cannot be blank" }
        require(age >= 0) { "Age cannot be negative" }
    }
}

// Avoid - Regular class for simple data
class Person(private val name: String, private val age: Int) {
    // ... manual equals, hashCode, toString
}
```

**Sealed classes for type safety:**
```kotlin
// Good - Sealed class for state management
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val exception: Throwable) : Result<Nothing>()
    object Loading : Result<Nothing>()
}

// Good - When expressions with sealed classes
fun handleResult(result: Result<String>) = when (result) {
    is Result.Success -> println(result.data)
    is Result.Error -> println("Error: ${result.exception.message}")
    Result.Loading -> println("Loading...")
}
```

## Null Safety
**Leverage Kotlin's null safety:**
```kotlin
// Good - Safe calls and Elvis operator
fun processUser(user: User?) {
    val name = user?.name?.takeIf { it.isNotBlank() } ?: "Unknown"
    user?.email?.let { sendEmail(it) }
}

// Good - Smart casts
fun handleInput(input: Any) {
    if (input is String && input.isNotEmpty()) {
        println(input.uppercase()) // Smart cast to String
    }
}

// Avoid - Unnecessary null checks
fun badExample(user: User?) {
    if (user != null) {
        if (user.name != null) {
            println(user.name) // Use user?.name instead
        }
    }
}
```

## Collections & Functional Programming
**Use collection operations and functional style:**
```kotlin
// Good - Collection operations
val validUsers = users
    .filter { it.isActive }
    .map { it.toDto() }
    .sortedBy { it.name }

// Good - Grouping and aggregation
val usersByDepartment = users.groupBy { it.department }
val totalSalary = employees.sumOf { it.salary }

// Good - Sequence for large datasets
val result = largeList.asSequence()
    .filter { it.isValid() }
    .map { it.process() }
    .take(10)
    .toList()

// Avoid - Manual loops for simple operations
val validUsers = mutableListOf<UserDto>()
for (user in users) {
    if (user.isActive) {
        validUsers.add(user.toDto())
    }
}
```

## Extension Functions
**Use extensions for utility functions:**
```kotlin
// Good - Extension functions for readability
fun String.isValidEmail(): Boolean =
    contains("@") && contains(".")

fun <T> List<T>.second(): T = this[1]

fun LocalDate.isWeekend(): Boolean =
    dayOfWeek in listOf(DayOfWeek.SATURDAY, DayOfWeek.SUNDAY)

// Usage
if (email.isValidEmail()) {
    sendEmail(email)
}
```

## Scope Functions
**Use scope functions appropriately:**
```kotlin
// Good - let for null safety and transformation
user?.let { u ->
    println("Processing user: ${u.name}")
    processUser(u)
}

// Good - apply for object configuration
val person = Person().apply {
    name = "John"
    age = 30
    email = "john@example.com"
}

// Good - run for complex initialization
val result = run {
    val config = loadConfig()
    val client = createClient(config)
    client.fetchData()
}

// Good - also for side effects
val numbers = listOf(1, 2, 3, 4, 5)
    .also { println("Original: $it") }
    .map { it * 2 }
    .also { println("Doubled: $it") }
```

## Coroutines & Async Programming
**Use coroutines for async operations:**
```kotlin
// Good - Suspend functions
suspend fun fetchUser(id: String): User {
    return withContext(Dispatchers.IO) {
        userRepository.findById(id)
    }
}

// Good - Flow for reactive streams
fun observeUsers(): Flow<List<User>> = flow {
    while (true) {
        emit(userRepository.getAllUsers())
        delay(5000)
    }
}.flowOn(Dispatchers.IO)

// Good - Structured concurrency
suspend fun processMultipleUsers(ids: List<String>): List<User> {
    return coroutineScope {
        ids.map { id ->
            async { fetchUser(id) }
        }.awaitAll()
    }
}

// Good - Error handling with coroutines
suspend fun safeApiCall(): Result<Data> = try {
    Result.Success(apiService.fetchData())
} catch (e: Exception) {
    Result.Error(e)
}
```

## Delegation & Properties
**Use delegation patterns:**
```kotlin
// Good - Property delegation
class User {
    val name: String by lazy { loadNameFromDatabase() }
    var isActive: Boolean by Delegates.observable(true) { _, old, new ->
        println("Active changed from $old to $new")
    }
}

// Good - Class delegation
interface Repository {
    fun save(item: Item)
    fun findById(id: String): Item?
}

class CachedRepository(
    private val delegate: Repository
) : Repository by delegate {
    private val cache = mutableMapOf<String, Item>()

    override fun findById(id: String): Item? {
        return cache[id] ?: delegate.findById(id)?.also { cache[id] = it }
    }
}
```

## Type Safety & Generics
**Leverage Kotlin's type system:**
```kotlin
// Good - Inline classes for type safety
@JvmInline
value class UserId(val value: String)

@JvmInline
value class Email(val value: String) {
    init {
        require(value.contains("@")) { "Invalid email format" }
    }
}

// Good - Reified generics
inline fun <reified T> parseJson(json: String): T {
    return Json.decodeFromString(json)
}

// Good - Variance annotations
interface Producer<out T> {
    fun produce(): T
}

interface Consumer<in T> {
    fun consume(item: T)
}
```

## Error Handling
**Use Result and sealed classes:**
```kotlin
// Good - Result type for error handling
suspend fun fetchUserSafely(id: String): Result<User> = runCatching {
    userService.fetchUser(id)
}

// Good - Custom result types
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val code: Int, val message: String) : NetworkResult<Nothing>()
    object NetworkError : NetworkResult<Nothing>()
}

// Good - Extension for result handling
inline fun <T> Result<T>.onFailure(action: (Throwable) -> Unit): Result<T> {
    if (isFailure) action(exceptionOrNull()!!)
    return this
}
```

## DSL & Builders
**Create readable DSLs when appropriate:**
```kotlin
// Good - Type-safe builders
class HtmlBuilder {
    fun body(init: BodyBuilder.() -> Unit) = BodyBuilder().apply(init)
}

class BodyBuilder {
    fun h1(text: String) = println("<h1>$text</h1>")
    fun p(text: String) = println("<p>$text</p>")
}

// Usage
html {
    body {
        h1("Welcome")
        p("This is a paragraph")
    }
}
```

## Interoperability
**Java interop best practices:**
```kotlin
// Good - JvmStatic for Java compatibility
object Utils {
    @JvmStatic
    fun formatDate(date: LocalDate): String = date.toString()
}

// Good - JvmOverloads for default parameters
class ApiClient @JvmOverloads constructor(
    private val baseUrl: String,
    private val timeout: Duration = Duration.ofSeconds(30)
)

// Good - Platform types handling
fun processJavaString(javaString: String?) {
    javaString?.let { safeString ->
        println(safeString.uppercase())
    }
}
```

## Performance & Best Practices
**Optimize for performance:**
```kotlin
// Good - Use sequences for large collections
val result = hugeList.asSequence()
    .filter { it.isValid }
    .map { it.transform() }
    .firstOrNull()

// Good - Avoid creating unnecessary objects
fun formatMessage(user: User, action: String) = buildString {
    append("User ")
    append(user.name)
    append(" performed ")
    append(action)
}

// Good - Use inline functions for higher-order functions
inline fun <T> measureTime(block: () -> T): Pair<T, Duration> {
    val start = System.nanoTime()
    val result = block()
    val duration = Duration.ofNanos(System.nanoTime() - start)
    return result to duration
}
```

## Key Principles
1. **Null safety first** - Use safe calls, smart casts, and proper null handling
2. **Immutability by default** - Prefer `val` over `var`, use data classes
3. **Functional style** - Leverage collection operations and higher-order functions
4. **Coroutines for async** - Use structured concurrency and Flow for reactive programming
5. **Type safety** - Use sealed classes, inline classes, and proper generics
6. **Expressive code** - Use extension functions, scope functions, and when expressions
7. **Performance aware** - Use sequences for large datasets, avoid unnecessary allocations
