"""DocumentInfo model for managed documents."""

from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class DocumentInfo:
    """Information about a managed document."""

    path: Path
    metadata_path: Path
    metadata: Dict[str, Any]
