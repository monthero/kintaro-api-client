from typing import Dict, List, Optional

from .base import BaseKintaroEntity


class KintaroWorkspace(BaseKintaroEntity):
    modification_info: Optional[Dict] = None
    workspace_id: Optional[str] = None
    repo_id: Optional[str] = None
    locales: List[str] = []
    description: Optional[str] = None
    translations_up_to_date: bool = False

    def __repr__(self) -> str:
        return f"KintaroWorkspace<{self.workspace_id}>"
