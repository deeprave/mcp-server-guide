# Instructions for Code Quality Checks

These are the guidelines to follow for testing python code.

To enhace the quality of code the following checks are mandatory during the CHECKS phase:

- Test   - `pytest -v -Walways`       - ensure that all tests pass and there are no warnings
- Lint   - `ruff check`               - ensure that all lint checks are fixed
- Types  - `mypy`                     - ensure that full typing is correct and issues fixed
- Format - `ruff format`              - format code to a known standard

**REQUIRED**
- ALL tests MUST PASS WITHOUT WARNINGS. NO EXCEPTIONS
- ALL linting issues must pass. NO EXCEPTIONS
- ALL type checks must be correct. NO EXCEPTIONS

For tools with an option to fix issues NEVER use "unsafe" versions.
Examine the error, do an analysis and fix it directly.

**You must run these checks before you can move out of CHECK phase**
