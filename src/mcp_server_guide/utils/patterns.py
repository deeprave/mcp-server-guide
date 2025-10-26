"""Pattern normalization utilities."""

import shlex
from typing import List, Union, Any


def normalize_patterns(patterns_input: Union[str, List[Any]]) -> List[str]:
    """
    Normalize and deduplicate pattern input.
    Handles strings, lists, and nested structures robustly.
    """
    if not patterns_input:
        return []

    if isinstance(patterns_input, list):
        # Handle nested lists and non-string elements
        flattened = []

        def flatten(items: List[Any]) -> None:
            for item in items:
                if isinstance(item, list):
                    flatten(item)
                elif isinstance(item, str) and item.strip():
                    flattened.append(item.strip())
                elif item is not None:  # Convert non-None, non-string to string
                    str_item = str(item).strip()
                    if str_item:
                        flattened.append(str_item)

        flatten(patterns_input)

        # Join with spaces and let shlex handle it
        patterns_str = " ".join(f'"{p}"' if " " in p else p for p in flattened)
    else:
        patterns_str = str(patterns_input)

    if not patterns_str.strip():
        return []

    # First try to split on commas, then use shlex for each part
    comma_parts = [part.strip() for part in patterns_str.split(",")]

    raw_patterns = []
    for part in comma_parts:
        if part:
            try:
                # Use shlex to handle quoted patterns with spaces
                shlex_parts = shlex.split(part)
                raw_patterns.extend(shlex_parts)
            except ValueError:
                # If shlex fails (unmatched quotes), fall back to simple split
                raw_patterns.extend(part.split())

    # Deduplicate while preserving order
    seen = set()
    normalized = []
    for pat in raw_patterns:
        pat = pat.strip()
        if pat and pat not in seen:
            normalized.append(pat)
            seen.add(pat)
    return normalized
