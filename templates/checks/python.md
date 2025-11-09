# Code Quality Checks

To enhace the quality of code the following checks are mandatory during the CHECKS phase:

Test   - pytest -v -Walways       - ensure that all tests pass and there are no warnings
Lint   - ruff check               - ensure that all lint checks are fixed
Types  - mypy                     - ensure that full typing is correct and issues fixed
Format - ruff format              - format code to a known standard

**REQUIRED**
 ALL tests must pass without warnings. NO EXCEPTIONS
 ALL linting issues must pass. NO EXCEOPTIONS
 ALL type checks must be correct. NO EXCEPTIONS
