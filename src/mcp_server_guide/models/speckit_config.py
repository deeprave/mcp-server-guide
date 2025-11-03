"""SpecKit configuration model."""

from pydantic import BaseModel, Field


class SpecKitConfig(BaseModel):
    """SpecKit configuration for global installation settings."""

    enabled: bool = Field(description="Whether SpecKit is enabled")
    url: str = Field(default="https://github.com/spec-kit/spec-kit", description="GitHub URL for SpecKit repository")
    version: str = Field(default="latest", description="SpecKit version (latest or specific version)")
