#!/usr/bin/env python
import contextlib
import json
import random
import re
import subprocess
import time
import tomllib
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional

CACHE_FILE = Path(".osvcheck")
CACHE_MIN_TTL = 12 * 3600  # 12 hours in seconds
CACHE_MAX_TTL = 24 * 3600  # 24 hours in seconds


def get_direct_dependencies() -> List[str]:
    """Get list of direct dependency names from pyproject.toml"""
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
        deps = data.get("project", {}).get("dependencies", [])
        # Extract package names
        return [re.split(r"[<>=\[~!]", dep)[0].strip().lower() for dep in deps]
    except Exception:
        return []


def get_all_installed_packages() -> List[Dict[str, Any]]:
    """Get ALL installed packages using uv"""
    try:
        result = subprocess.run(["uv", "pip", "list", "--format", "json"], capture_output=True, text=True, check=True)
        packages: List[Dict[str, Any]] = json.loads(result.stdout)
        return packages
    except Exception:
        return []


def load_cache() -> Dict[str, Dict[str, Any]]:
    """Load cache from .osvcheck file"""
    if not CACHE_FILE.exists():
        return {}

    try:
        with open(CACHE_FILE, "r") as f:
            cache = json.load(f)

        # Remove expired entries
        current_time = time.time()
        cache = {k: v for k, v in cache.items() if v.get("expires_at", 0) > current_time}
        return cache
    except Exception:
        return {}


def save_cache(cache: Dict[str, Dict[str, Any]]) -> None:
    """Save cache to .osvcheck file"""
    with contextlib.suppress(Exception):
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=2)


def get_cache_key(pkg_name: str, pkg_version: str) -> str:
    """Generate cache key for a package"""
    return f"{pkg_name}:{pkg_version}"


def check_vulnerability(pkg_name: str, pkg_version: str, cache: Dict[str, Dict[str, Any]]) -> Optional[str]:
    """
    Check if package has vulnerabilities using cache or API.
    Returns 'direct', 'indirect', or None if no vulnerabilities.
    """
    cache_key = get_cache_key(pkg_name, pkg_version)

    # Check cache first, but if vulnerability was found, always re-check
    cached_result = cache.get(cache_key)
    if cached_result and cached_result.get("vuln_type") is None:
        # Only use cache if no vulnerability was previously found
        return None

    # Query OSV API (always check if vulnerability was found before, or not in cache)
    query = {"package": {"ecosystem": "PyPI", "name": pkg_name}, "version": pkg_version}

    req = urllib.request.Request(
        "https://api.osv.dev/v1/query",
        data=json.dumps(query).encode(),
        headers={"Content-Type": "application/json"},
    )

    vuln_type = None
    with contextlib.suppress(Exception):
        with urllib.request.urlopen(req) as response:
            result = json.loads(response.read())
            if result.get("vulns", []):
                vuln_type = "has_vulns"  # Will be updated to direct/indirect by caller

    # Cache the result with random TTL
    ttl = random.randint(CACHE_MIN_TTL, CACHE_MAX_TTL)
    cache[cache_key] = {"vuln_type": vuln_type, "expires_at": time.time() + ttl}

    return vuln_type


def main() -> None:
    # sourcery skip: extract-duplicate-method, remove-redundant-if, split-or-ifs
    direct_deps = get_direct_dependencies()
    all_packages = get_all_installed_packages()

    print(f"Checking {len(all_packages)} packages ({len(direct_deps)} direct dependencies)...\n")

    # Load cache
    cache = load_cache()

    direct_vulnerable = []
    indirect_vulnerable = []

    for pkg in all_packages:
        pkg_name = pkg["name"]
        pkg_version = pkg["version"]
        is_direct = pkg_name.lower() in direct_deps

        # Check vulnerability using cache or API
        if check_vulnerability(pkg_name, pkg_version, cache):
            dep_type = "direct" if is_direct else "indirect"

            # Update cache with correct vulnerability type
            cache_key = get_cache_key(pkg_name, pkg_version)
            cache[cache_key]["vuln_type"] = dep_type

            dep_type_display = "DIRECT" if is_direct else "indirect"
            marker = "⚠️ " if is_direct else "  ⚠️"
            print(f"{marker} [{dep_type_display}] {pkg_name} {pkg_version}: vulnerabilities found")

            if is_direct:
                direct_vulnerable.append(pkg_name)
            else:
                indirect_vulnerable.append(pkg_name)

    # Save the updated cache
    save_cache(cache)

    v_direct = len(direct_vulnerable)
    v_indirect = len(indirect_vulnerable)
    if v_direct or v_indirect:
        print("Vulnerabilities found!")
    if v_direct:
        print(f"  - {v_direct} direct dependency vulnerabilities:")
        print(f"    {', '.join(direct_vulnerable)}")
    if v_indirect:
        print(f"  - {v_indirect} indirect dependency vulnerabilities:")
        print(f"    {', '.join(indirect_vulnerable)}")

    exit(2 if v_direct else 1 if v_indirect else 0)


if __name__ == "__main__":
    main()
