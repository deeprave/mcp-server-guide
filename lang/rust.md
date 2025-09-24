# Rust Guidelines

## Formatting & Quality
- **Use `rustfmt` and `clippy`** - address warnings before considering complete
- **Inline interpolation:** `format!("Error: {e}")` vs `format!("Error: {}", e)`

## Code Complexity
- **Early returns** with guard clauses
- **Minimize cloning,** especially `Arc<T>`
- **Iterate collections once** - chain operations

## Borrowing & Ownership
- **Prefer borrowing:** `&[T]` over `&Vec<T>`, `&str` over `&String`
- **Avoid unnecessary `clone()`** - use references or `Arc`/`Rc`
- Use `?` operator for error propagation

## Iterator Patterns
**Prefer iterators over loops:**
```rust
// Good
items.iter().filter(|x| x.is_valid()).map(|x| x.process()).collect()

// Avoid
let mut results = Vec::new();
for item in &items {
    if item.is_valid() {
        results.push(item.process());
    }
}
```

## Error Handling
- **Use `Result<T, E>` and `Option<T>`** - avoid nullable patterns
- **`expect("msg")` over `unwrap()`** in production
- Prefer use of `thiserror` and use domain specific errors

## Pattern Matching
- **Exhaustive `match`** - avoid catch-all `_` when specific patterns better
- **`if let`** for single patterns
- **`let-else`** for early returns: `let Some(data) = input else { return Err("msg"); };`
- avoid typeless conversions, use of Any

## Collections
- **Choose correctly:** `Vec<T>`, `HashMap<K,V>`, `HashSet<T>`, `BTree*` for ordering
- **Pre-allocate** with `Vec::with_capacity()` when size known

## Function Design
- **Small, focused non-complex functions**
- **`impl Trait`** in return positions
- **`&[T]` parameters** instead of `&Vec<T>`

## Types & Traits
- **`#[derive]`** for common traits
- **`Display`** for users, **`Debug`** for development
- **Associated constants** over module constants

## Anti-Patterns
- **No `unwrap()`** in production
- **No `unsafe`** without justification
- **No `String`** when `&str` works
- **Address compiler warnings**

## Common Idioms
```rust
// Option chaining
value.as_ref().map(|v| v.process()).unwrap_or_default()

// Iterator filtering
items.iter().filter(|x| x.is_valid()).collect::<Vec<_>>()

// Error context
fs::read_to_string(path).with_context(|| format!("Failed to read {}", path.display()))?
```
