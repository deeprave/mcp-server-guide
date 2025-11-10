# Review instructions

This document details the production of a review artifact.

When the review has concluded, create a code review file in a markdown file with the format described below.
Place this file together with the implementation plan that describes the changes you are reviewing, appending `-review` to (or replacing `-plan` in) the file name.
If there is no specific plan associated with the changes, then use `code-review` as a generic name, overwriting any existing file with that name.

--- BEGIN CODE REVIEW FORMAT ---

Please address the comments from this code review:

```markdown
## Review Comment #

### Issue to address
**severity_level (category):** (brief description of the issue)
(additional detailed description)

### Location(s)
`file_path:line_number`

### Context
(`file_path:line_number` reference with relevant code snippet(s) using code fences)

### Comments
(explanation and recommendation)

### Suggested Fix
(proposed fix code, preferably as a diff using code fences)
```

--- END CODE REVIEW FORMAT ---

Where:

- "Issue to address" section" contains the severity of and brief summary of the issue
  followed by a more detailed description if necessary.
  - Must inclukde:
    - severity levels (critical, warning, suggestion, info)
    - categories like (bug_risk, dead_code, security, dry, yagni, solid)
- "Location(s)" contains the file path(s) and line number(s) affected by the issue described
- "Code Context" section shows the relevant code snippet within code fences
- Follow this format for all types of issues and severity
- You may add any additional comments including analysis and suggestions using standard markdown.
