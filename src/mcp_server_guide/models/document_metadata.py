"""DocumentMetadata Pydantic model for managed documents."""

from pydantic import BaseModel, ConfigDict


class DocumentMetadata(BaseModel):
    """Metadata for managed documents with forwards compatibility."""

    model_config = ConfigDict(extra="allow")

    source_type: str
    content_hash: str
    mime_type: str
