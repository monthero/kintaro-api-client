from typing import Dict, List, Optional

from .base import BaseKintaroEntity


class KintaroDocumentVersion(BaseKintaroEntity):
    snapshot_id: Optional[str] = None
    locales: List[str] = []
    modification_info: Dict[str, str] = {}
    modified_locales: List[str] = []

    def __repr__(self) -> str:
        return f"KintaroDocumentVersion<{self.snapshot_id}>"


class KintaroDocument(BaseKintaroEntity):
    schema_id: Optional[str] = None
    collection_id: Optional[str] = None
    document_id: Optional[str] = None
    content: Dict = {}
    versions: List[KintaroDocumentVersion] = []
    document_state: Optional[str] = None

    def __init__(self, initial_data: Optional[Dict] = None):
        if not initial_data:
            return

        initial_data["content"] = initial_data.pop("content_json", {})
        for field in [
            "translation_readiness",
            "never_published",
        ]:
            if field in initial_data:
                del initial_data[field]

        super().__init__(initial_data=initial_data)

    def __repr__(self) -> str:
        return f"KintaroDocument<{self.collection_id}:{self.document_id}>"


class KintaroDocumentSummary(BaseKintaroEntity):
    collection_id: Optional[str] = None
    schema_id: Optional[str] = None
    document_id: Optional[str] = None
    translations_up_to_date: bool = False
    document_state: Optional[str] = None

    def __init__(self, initial_data: Optional[Dict] = None):
        if not initial_data:
            return

        data: Dict = {}
        for key in initial_data.keys():
            if key == "translation_readiness" or key.endswith("_json"):
                continue
            else:
                data[key] = initial_data[key]

        super().__init__(initial_data=data)

    def __repr__(self) -> str:
        return f"KintaroDocumentSummary<{self.document_id}>"
