"""DocumentInfo model for managed documents."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict


@dataclass
class DocumentInfo:
    """Information about a managed document."""

    path: Path
    metadata_path: Path
    metadata: Dict[str, Any]
