# Java Guidelines

## Project Structure

**Standard Maven/Gradle layout:**

```
root/
├── pom.xml / build.gradle
├── src/
│   ├── main/java/
│   │   └── com/example/
│   └── test/java/
│       └── com/example/
├── README.md
└── .gitignore
```

## Formatting & Quality

- **Use modern Java (17+)** - leverage latest LTS features
- **Consistent formatting** with IDE defaults or Spotless
- **Use `var`** for local variables when type is obvious
- **Text blocks** for multi-line strings (Java 15+)

## Modern Syntax & Idioms

**Records for immutable data:**

```java
// Good - Modern record
public record Person(String name, int age, List<String> hobbies) {
    public Person {
        hobbies = List.copyOf(hobbies); // Defensive copy
    }
}

// Avoid - Traditional class for simple data
public class Person {
    private final String name;
    private final int age;
    // ... boilerplate constructor, getters, equals, hashCode
}
```

**Pattern matching and switch expressions:**

```java
// Good - Modern switch expression
String result = switch (status) {
    case PENDING -> "Waiting";
    case APPROVED -> "Ready";
    case REJECTED -> "Failed";
};

// Good - Pattern matching (Java 17+)
if (obj instanceof String s && s.length() > 5) {
    return s.toUpperCase();
}
```

## Collections & Streams

**Use factory methods and streams:**

```java
// Good - Collection factories (Java 9+)
var numbers = List.of(1, 2, 3, 4, 5);
var config = Map.of("host", "localhost", "port", "8080");

// Good - Stream operations
var result = items.stream()
    .filter(Item::isValid)
    .map(Item::process)
    .collect(Collectors.toList());

// Good - Collectors for complex operations
var grouped = people.stream()
    .collect(Collectors.groupingBy(Person::department));

// Avoid - Manual loops for simple operations
List<String> results = new ArrayList<>();
for (Item item : items) {
    if (item.isValid()) {
        results.add(item.process());
    }
}
```

**Prefer immutable collections:**

```java
// Good - Immutable by default
public List<String> getItems() {
    return List.copyOf(items);
}

// Good - Use Collections.unmodifiableList() for older Java
return Collections.unmodifiableList(new ArrayList<>(items));
```

## Error Handling

**Use Optional and proper exceptions:**

```java
// Good - Optional for nullable returns
public Optional<User> findUser(String id) {
    return users.stream()
        .filter(u -> u.id().equals(id))
        .findFirst();
}

// Good - Specific exceptions
public void validateInput(String input) {
    if (input == null || input.isBlank()) {
        throw new IllegalArgumentException("Input cannot be null or blank");
    }
}

// Avoid - Returning null
public User findUser(String id) {
    return null; // Don't do this
}
```

## Functional Programming

**Leverage functional interfaces:**

```java
// Good - Method references
users.stream()
    .map(User::getName)
    .filter(Objects::nonNull)
    .forEach(System.out::println);

// Good - Custom functional interfaces when needed
@FunctionalInterface
public interface Validator<T> {
    boolean isValid(T item);
}

// Avoid - Single-use interfaces for simple operations
interface UserProcessor {
    void process(User user); // Just use Consumer<User>
}
```

## Code Organization

**Avoid single-use interfaces:**

```java
// Good - Use standard functional interfaces
Function<String, Integer> parser = Integer::parseInt;
Predicate<String> isEmpty = String::isEmpty;
Consumer<String> logger = System.out::println;

// Avoid - Creating interfaces for single methods
interface StringParser {
    Integer parse(String s);
}
```

**Prefer composition over inheritance:**

```java
// Good - Composition with records
public record EmailService(EmailClient client, TemplateEngine engine) {
    public void sendEmail(String to, String template, Map<String, Object> data) {
        var content = engine.render(template, data);
        client.send(to, content);
    }
}
```

## Performance & Best Practices

**String handling:**

```java
// Good - Text blocks for readability
var sql = """
    SELECT u.name, u.email
    FROM users u
    WHERE u.active = true
    AND u.created_date > ?
    """;

// Good - StringBuilder for concatenation in loops
var builder = new StringBuilder();
items.forEach(item -> builder.append(item.toString()).append("\n"));
```

**Resource management:**

```java
// Good - Try-with-resources
try (var reader = Files.newBufferedReader(path)) {
    return reader.lines()
        .filter(line -> !line.isBlank())
        .collect(Collectors.toList());
}
```

## Testing Patterns

**Use modern testing approaches:**

```java
// Good - Parameterized tests
@ParameterizedTest
@ValueSource(strings = {"", " ", "\t", "\n"})
void shouldRejectBlankInput(String input) {
    assertThrows(IllegalArgumentException.class,
        () -> validator.validate(input));
}

// Good - Test records for test data
record TestUser(String name, int age, boolean active) {}
```

## Key Principles

1. **Immutability by default** - Use records, final fields, defensive copying
2. **Fail fast** - Validate inputs early, use Optional for nullable returns
3. **Readable code** - Prefer streams and method references over loops
4. **Modern features** - Use var, text blocks, pattern matching, switch expressions
5. **Functional style** - Leverage standard functional interfaces, avoid single-use interfaces
6. **Performance aware** - Use appropriate collections, avoid unnecessary object creation
