# Instructions for commit message generation

You are tasked with providing a complete but concise description to summarise based on the changes cached for commit.
Use markdown format (dashes, not bullets and subheadings as appropriate)

- Provide a title/subject line
  - Length: Try to keep it under 50 characters (72 max)
  - Format: Use imperative mood ("Add feature" not "Added feature" or "Adds feature")
  - Capitalisation: Capitalise the first letter
  - No period: Don't end with a period
  - Be specific: Describe concisely what the change does, not how or why
  - If known, use an associated issue-id

- Optionally (but recommended) provide a body
  - Blank line: Always separate title/subject from body with a blank line
  - Use bullet points: For multiple changes or details
  - Line length: Wrap at 72 characters
  - Content: Explain the what and why, not the how
  - Reference issues: Include ticket numbers, issue references

- Level of Detail
  - Small changes: Subject line only is often enough
  - Medium changes: Add a brief body explaining context
  - Large changes: Detailed body with motivation, approach, and any breaking changes
  - Bug fixes: Include what was broken and how it was fixed

- Information that MUST NOT be included:
  - Too much detailed information about the implementation
  - Changes with administrative/specification documents in openspec/
  - Test statistics (it is assumed that tests pass with sufficient coverage)
  - Review feedback and actions/changes as a result of review
  - References to phases or other task
