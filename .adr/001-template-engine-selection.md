# ADR 001: Template Engine Selection for Agent-Specific Content

**Status**: Proposed
**Date**: 2025-11-22
**Deciders**: Development Team
**Context**: Guide Command Prefix Refactor (`.todo/guide-command-prefix-refactor-spec.md`)

## Context and Problem Statement

The MCP server needs to provide agent-specific documentation and help content that adapts to different MCP clients (Kiro, Claude, Cursor, Copilot, Gemini). Each agent uses different prompt invocation syntax and may require different instructions.

**Requirements:**
- Load templates from markdown files (user documents and internal help)
- Variable substitution (agent name, prompt prefix, server name, version)
- Conditional content based on agent type
- Safe for user-provided content (no code execution)
- Minimal complexity for simple use cases

**Key Use Case:**
```markdown
# Guide Help for {{agent_name}}

Use {{prompt_prefix}}guide to access documentation.

{{#is_claude}}
**Important**: For Claude, replace "guide" with your mcpServers config key.
{{/is_claude}}

{{^is_claude}}
Example: {{prompt_prefix}}guide -help
{{/is_claude}}
```

## Decision Drivers

1. **File-based templates** - Must load from markdown files
2. **Conditional logic** - Agent-specific content sections
3. **Safety** - No arbitrary code execution
4. **Simplicity** - Lightweight for simple substitution
5. **Dependencies** - Prefer minimal external dependencies
6. **Familiarity** - Developers should recognize the syntax

## Considered Options

### Option 1: Python T-Strings (PEP 750)

**Syntax:**
```python
template = t"Hello, {name}!"
```

**Pros:**
- ✅ Native Python 3.14+
- ✅ Zero dependencies
- ✅ Familiar f-string syntax
- ✅ Type-safe

**Cons:**
- ❌ **Compile-time only** - Cannot load from files
- ❌ No conditionals
- ❌ Requires code changes for new templates

**Verdict:** ❌ **Rejected** - Cannot load templates from files (blocker)

---

### Option 2: string.Template (Python stdlib)

**Syntax:**
```python
template = Template("Hello, $name!")
template.substitute(name="World")
```

**Pros:**
- ✅ Built-in (zero dependencies)
- ✅ Safe (no code execution)
- ✅ Simple syntax (`$var`)
- ✅ Can load from files

**Cons:**
- ❌ **No conditionals** - Must preprocess in Python
- ❌ **No loops** - Must preprocess in Python
- ❌ Complex templates require extensive preprocessing

**Example with preprocessing:**
```python
# Template
"Use $prompt_prefix guide. $claude_note"

# Must compute conditionals in Python
context = {
    'prompt_prefix': agent_info.prompt_prefix,
    'claude_note': 'For Claude, use config key' if is_claude else ''
}
```

**Verdict:** ⚠️ **Acceptable but limited** - Works for simple cases, awkward for conditionals

---

### Option 3: Jinja2

**Syntax:**
```jinja2
Hello {{ name }}!
{% if is_claude %}
  Claude-specific content
{% endif %}
```

**Pros:**
- ✅ Industry standard
- ✅ Powerful (conditionals, loops, filters, inheritance)
- ✅ Can load from files
- ✅ Safe (sandboxed)
- ✅ Excellent documentation

**Cons:**
- ❌ **Heavy dependency** (~200KB)
- ❌ Overkill for simple substitution
- ❌ More complex syntax
- ❌ Steeper learning curve

**Verdict:** ⚠️ **Powerful but heavy** - Too much for our needs

---

### Option 4: Chevron (Mustache)

**Syntax:**
```mustache
Hello {{name}}!

{{#is_claude}}
Claude-specific content
{{/is_claude}}

{{^is_claude}}
Standard content
{{/is_claude}}
```

**Pros:**
- ✅ **Lightweight** (~10KB, pure Python)
- ✅ **Conditionals built-in** (`{{#var}}...{{/var}}`)
- ✅ **Negation/else** (`{{^var}}...{{/var}}`)
- ✅ **List iteration** (`{{#list}}...{{/list}}`)
- ✅ **Logic-less** - Safe, no code execution
- ✅ **Industry standard** - Mustache spec widely known
- ✅ **Can load from files**
- ✅ **Fast** - Faster than pystache and comparable implementations
- ✅ **Simple syntax** - Easy to learn and read

**Cons:**
- ⚠️ External dependency (but minimal)
- ⚠️ Less powerful than Jinja2 (but we don't need that power)

**Example Usage:**
```python
import chevron

template = """
# Guide for {{agent_name}}

{{#is_claude}}
Use /{{server_name}}:guide commands
{{/is_claude}}

{{^is_claude}}
Use {{prompt_prefix}}guide commands
{{/is_claude}}
"""

context = {
    'agent_name': 'claude-code',
    'is_claude': True,
    'server_name': 'my-guide',
    'prompt_prefix': '@'
}

result = chevron.render(template, context)
```

**Verdict:** ✅ **Best fit** - Sweet spot between simplicity and functionality

---

## Decision Outcome

**Chosen Option:** **Chevron (Mustache)**

### Rationale

1. **Conditionals are essential** - Agent-specific content requires conditional sections
2. **Lightweight** - 10KB dependency is acceptable for the functionality gained
3. **Logic-less design** - Safe for user-provided templates
4. **File-based** - Can load from markdown documents
5. **Standard syntax** - Mustache is widely recognized
6. **Right-sized** - Not too simple (string.Template), not too complex (Jinja2)

### Comparison Summary

- **T-Strings**: ❌ Can't load from files (blocker)
- **string.Template**: ⚠️ No conditionals (requires complex preprocessing)
- **Jinja2**: ⚠️ Too heavy for our needs (~200KB vs ~10KB)
- **Chevron**: ✅ Perfect balance of features and simplicity

### Trade-offs

**Accepting:**
- Small external dependency (~10KB)
- Mustache syntax learning curve (minimal)

**Gaining:**
- Clean conditional logic in templates
- List iteration capability
- Logic-less safety
- Cleaner, more maintainable templates

## Implementation Notes

### Template Context Builder

```python
def build_template_context(agent_info: AgentInfo, server_name: str) -> dict:
    """Build context for template rendering."""
    return {
        'agent_name': agent_info.name,
        'agent_normalized': agent_info.normalized_name,
        'agent_version': agent_info.version or 'Unknown',
        'prompt_prefix': agent_info.prompt_prefix,
        'server_name': server_name,
        # Boolean flags for conditionals
        'is_kiro': agent_info.normalized_name == 'kiro',
        'is_claude': agent_info.normalized_name == 'claude',
        'is_cursor': agent_info.normalized_name == 'cursor',
        'is_copilot': agent_info.normalized_name == 'copilot',
        'is_gemini': agent_info.normalized_name == 'gemini',
    }
```

### Template Loading

```python
import chevron

def render_markdown_template(template_path: Path, context: dict) -> str:
    """Render a markdown template with agent-specific context."""
    with open(template_path, 'r') as f:
        template = f.read()
    return chevron.render(template, context)
```

### Dependency Addition

Add to `pyproject.toml`:
```toml
dependencies = [
    # ... existing dependencies
    "chevron>=0.14.0",
]
```

## Consequences

### Positive

- ✅ Clean, readable templates with conditionals
- ✅ Agent-specific content without Python preprocessing
- ✅ Users can create agent-aware documentation
- ✅ Maintainable template files
- ✅ Safe for user-provided content

### Negative

- ⚠️ Adds external dependency (mitigated by small size)
- ⚠️ New syntax for contributors to learn (mitigated by simplicity)

### Neutral

- Templates use Mustache syntax instead of Python syntax
- Need to document template variables and syntax

## Alternatives Considered

Documented above in "Considered Options" section.

## Related Decisions

- Agent detection system (implemented 2025-11-22)
- Tool result handling standardization (`.todo/tool-result-handling-spec.md`)
- Guide command prefix refactor (`.todo/guide-command-prefix-refactor-spec.md`)

## References

- [Mustache Specification](https://mustache.github.io/mustache.5.html)
- [Chevron GitHub](https://github.com/noahmorrison/chevron)
- [PEP 750 - Template Strings](https://peps.python.org/pep-0750/)
- Python string.Template documentation
