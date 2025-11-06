# Write your review!

When the review is ready, create a code review file in a markdown file with the format:

Please address the comments from this code review:

```markdown
## Review Comment #

### Issue to address
**severity_level (category):** (brief description of the issue)
(additional detailed description)


### Location(s)
`file_path:line_number`
...

### Code Context
(`file_path:line_number` reference with relevant code snippet(s) using code fences)

### Comments
(explanation and recommendation)


### Suggested Fix
(proposed fix code, preferably as a diff using code fences)

```

Where:

 - "Issue to address" section" contains the severity of and brief summary of the issue
   followed by a more detailed description if necessary. Must inclukde:
   - severity levels (critical, warning, suggestion, info)
   - categories like (bug_risk, dead_code, security, dry, yagni, solid)
 - "Location(s)" contains the file path(s) and line number(s) affected by the issue described
 - "Code Context" section shows the relevant code snippet within code fences
 - Follow this format for all types of issues and severity
 - You may add any additional comments including analysis and suggestions using standard markdown.
