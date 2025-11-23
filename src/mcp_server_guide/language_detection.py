"""Language auto-detection based on project files."""

import glob
from pathlib import Path
from typing import List, Optional


def count_source_files(project_path: str, patterns: List[str], max_depth: int = 3, max_files: int = 60) -> int:
    """Count source files matching given patterns with depth and count limits."""
    path = Path(project_path)
    count = 0

    for pattern in patterns:
        # Use ** for recursive search with depth limit handled by itertools
        full_pattern = str(path / "**" / pattern)

        # Use iglob for memory efficiency and islice for early exit
        file_iterator = glob.iglob(full_pattern, recursive=True)

        # Filter by depth and limit count
        for file_path in file_iterator:
            # Check depth relative to project path
            rel_path = Path(file_path).relative_to(path)
            if len(rel_path.parts) <= max_depth + 1:  # +1 for the filename itself
                count += 1
                if count >= max_files:
                    return count

    return count


def detect_project_language(project_path: str = ".") -> Optional[str]:
    """
    Detect programming language based on project files with multi-pass analysis.

    Returns None if no language can be detected.
    """
    path = Path(project_path)

    # First pass: definitive indicators
    definitive_indicators = [
        ("Cargo.toml", "rust"),
        ("pyproject.toml", "python"),
        ("requirements.txt", "python"),
        ("setup.py", "python"),
        ("go.mod", "golang"),
        ("tsconfig.json", "typescript"),
        ("Gemfile", "ruby"),
        ("composer.json", "php"),
    ]

    for filename, language in definitive_indicators:
        if (path / filename).exists():
            return language

    # Second pass: ambiguous indicators requiring source file analysis
    ambiguous_cases = []

    # Gradle: Java vs Kotlin vs Scala
    if any((path / f).exists() for f in ["build.gradle", "build.gradle.kts", "settings.gradle", "settings.gradle.kts"]):
        java_count = count_source_files(project_path, ["*.java"], max_depth=7)
        kotlin_count = count_source_files(project_path, ["*.kt", "*.kts"], max_depth=7)
        scala_count = count_source_files(project_path, ["*.scala", "*.sbt", "*.sc"], max_depth=7)
        ambiguous_cases.extend([("java", java_count), ("kotlin", kotlin_count), ("scala", scala_count)])

    # Maven: Java vs Kotlin vs Scala
    elif (path / "pom.xml").exists():
        java_count = count_source_files(project_path, ["*.java"], max_depth=7)
        kotlin_count = count_source_files(project_path, ["*.kt", "*.kts"], max_depth=7)
        scala_count = count_source_files(project_path, ["*.scala", "*.sbt", "*.sc"], max_depth=7)
        if scala_count > max(java_count, kotlin_count):
            ambiguous_cases.append(("scala", scala_count))
        elif kotlin_count > java_count:
            ambiguous_cases.append(("kotlin", kotlin_count))
        else:
            ambiguous_cases.append(("java", java_count))

    # Package.json: JavaScript vs TypeScript
    elif (path / "package.json").exists():
        js_count = count_source_files(project_path, ["*.js", "*.jsx"])
        ts_count = count_source_files(project_path, ["*.ts", "*.tsx"])

        # Check for TypeScript dependencies as tiebreaker
        try:
            import json

            with open(path / "package.json") as f:
                data = json.load(f)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                has_ts_deps = any("typescript" in dep or "@types/" in dep for dep in deps)

                if has_ts_deps or ts_count > js_count:
                    ambiguous_cases.append(("typescript", ts_count + (10 if has_ts_deps else 0)))
                else:
                    ambiguous_cases.append(("javascript", js_count))
        except (json.JSONDecodeError, IOError):
            # Fallback to file count
            if ts_count > js_count:
                ambiguous_cases.append(("typescript", ts_count))
            else:
                ambiguous_cases.append(("javascript", js_count))

    # Makefile/CMake: C vs C++
    elif any((path / f).exists() for f in ["Makefile", "makefile", "CMakeLists.txt"]):
        c_count = count_source_files(project_path, ["*.c", "*.h"])
        cpp_count = count_source_files(project_path, ["*.cpp", "*.hpp", "*.cc", "*.cxx", "*.c++", "*.hxx"])

        # Only consider if we actually find source files (Makefile can be generic)
        if c_count > 0 or cpp_count > 0:
            if cpp_count > c_count:
                ambiguous_cases.append(("cpp", cpp_count))
            else:
                ambiguous_cases.append(("c", c_count))

    # Third pass: pure source file detection (no build files)
    else:
        source_file_checks = [
            (["*.swift"], "swift", 3),
            (["*.cs", "*.csx"], "csharp", 4),
            (["*.fs", "*.fsx"], "fsharp", 4),
            (["*.lua"], "lua", 3),
            (["*.dart"], "dart", 3),
            (["*.sh", "*.ksh", "*.tsh"], "shell", 3),
            (["*.md", "*.markdown", "*.mkdown"], "markdown", 3),
            (["*.scala", "*.sbt", "*.sc"], "scala", 3),
        ]

        for patterns, language, depth in source_file_checks:
            count = count_source_files(project_path, patterns, max_depth=depth)
            if count > 0:
                ambiguous_cases.append((language, count))

    # Return the language with the highest source file count
    if ambiguous_cases:
        best_language = max(ambiguous_cases, key=lambda x: x[1])
        if best_language[1] > 0:  # Only return if we found actual source files
            return best_language[0]

    return None


def should_auto_detect_language(current_language: Optional[str]) -> bool:
    """Check if language auto-detection should be applied."""
    return current_language in (None, "", "none")
