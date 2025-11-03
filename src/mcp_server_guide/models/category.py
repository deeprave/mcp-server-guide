from typing import Optional, List, Any

from pydantic import BaseModel, Field, field_validator


class Category(BaseModel):
    """Category configuration for organizing source code.

    A category can either:
    - Point to HTTP resources via 'url' field
    - Point to local files via 'dir' and 'patterns' fields
    But not both.
    """

    url: Optional[str] = Field(None, description="HTTP URL for remote resources")
    dir: Optional[str] = Field(None, description="Directory path relative to project root")
    patterns: Optional[List[str]] = Field(None, description="File patterns to match")
    description: str = Field(default="", description="Human-readable description of the category")

    def model_post_init(self, __context: Any) -> None:
        """Validate that category has either url OR dir/patterns, but not both."""
        has_url = self.url is not None
        has_dir = self.dir is not None
        has_patterns = self.patterns is not None and len(self.patterns) > 0

        if has_url and (has_dir or has_patterns):
            raise ValueError("Category cannot have both 'url' and 'dir'/'patterns' fields")

        if not has_url and not has_dir:
            raise ValueError("Category must have either 'url' or 'dir' field")

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("URL cannot be empty")
        # Basic URL validation
        v = v.strip()
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("URL must start with http:// or https://")
        return v

    @field_validator("dir")
    @classmethod
    def validate_dir(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Directory path cannot be empty")
        # Normalize path separators and remove redundant slashes
        normalized = v.strip().replace("\\", "/")
        # Remove leading slash to ensure relative paths
        if normalized.startswith("/"):
            normalized = normalized[1:]
        # Ensure it ends with / for consistency
        if normalized and not normalized.endswith("/"):
            normalized += "/"
        return normalized

    @field_validator("patterns")
    @classmethod
    def validate_patterns(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is None:
            return v
        if not v:  # Empty list is allowed
            return v
        for pattern in v:
            if not isinstance(pattern, str):
                raise ValueError("File patterns must be strings")
            if not pattern.strip():
                raise ValueError("File patterns cannot be empty")
            # Basic glob pattern validation
            if ".." in pattern:
                raise ValueError("File patterns cannot contain path traversal sequences")
        return [p.strip() for p in v]

    @field_validator("description")
    @classmethod
    def validate_description(cls, v: str) -> str:
        # Inline validation to avoid circular imports
        if not isinstance(v, str):
            raise ValueError("Description must be a string")
        return v.strip() if v else ""
