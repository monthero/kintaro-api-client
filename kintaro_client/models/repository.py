from typing import Dict, List, Optional

from kintaro_client.models.base import BaseKintaroEntity


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
        initial_data: Dict = {
            key: value
            for key, value in initial_data.items()
            if hasattr(self, key)
        }
        super().__init__(initial_data=initial_data)

    def __repr__(self) -> str:
        return f"KintaroRepository<{self.repo_id}>"
