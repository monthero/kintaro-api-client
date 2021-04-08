from typing import Dict, List, Optional

from .base import BaseKintaroEntity


class KintaroRepository(BaseKintaroEntity):
    repo_id: Optional[str] = None
    repo_label: Optional[str] = None
    modification_info: Dict[str, str] = {}
    description: Optional[str] = None
    default_language: Optional[str] = None
    content_type: Optional[str] = None
    locales: List[str] = []
    allowed_operations: List[str] = []
    schema_ids: List[str] = []

    def __init__(self, initial_data: Optional[Dict] = None):
        data: Dict = {}
        for key in initial_data:
            if not hasattr(self, key):
                continue

        super().__init__(initial_data=data)
        if hasattr(self, "workspace_id"):
            delattr(self, "workspace_id")

    def __repr__(self) -> str:
        return f"KintaroRepository<{self.repo_id}>"
