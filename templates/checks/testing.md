# Testing Guidelines

These are the guidelines to follow for general code and quality testing.

## Instructions for Testing

- Do not use conditionals in tests
- Avoid loops
- Prefer not using mocks
- Test the API not the implementation
- Test that a feature works

NEVER use "coverage" in module, class, function, method or variable names.
Always use names that describe what is being tested.

### Conditionals

Use of conditionals:

- obfuscates the intent of a test.
- introduce a risk of introducing subtle bugs, including false positives and negatives.

Always separate testing of happy and error paths.

### Loops

Use of loops in tests can:

- lead to tigher dependency between code and the test.
- introduce the possibility of reduecing the isolation between tests.
- obscure the result by not pinpointing which iteration causes a failure.
- introduce a risk of skipping certain test cases
- making debugging more complex, must take into account the loop logic.

### Mocks

Avoid using mocks if possible, especially avoid testing mock behaviour.
Mocks:

- simiulate behaviour, which may not accurately reflect the real system.
- bypass test dependencie, so they do not fully test integration
- usually rely on implementation detail, increasing coupling between code and test.

Prefer running real code, using real objects, classes and results where possible.
The exceptions are fairly obvious:

- to avoid side-effects
- to produce a scenario to be tested

Try to always test the public or external API, not its implementation
