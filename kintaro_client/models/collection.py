from typing import Dict, Optional

from kintaro_client.models.base import BaseKintaroEntity
from kintaro_client.models.schema import KintaroSchema


class KintaroCollection(BaseKintaroEntity):
    folder: Optional[str] = None
    collection_id: Optional[str] = None
    schema_id: Optional[str] = None
    schema: Optional[KintaroSchema] = None
    total_document_count: int = 0
    published_document_count: int = 0
    description: Optional[str] = None

    def __init__(self, initial_data: Optional[Dict] = None):
        if not initial_data:
            return

        super().__init__(initial_data=initial_data)
        if "schema" in initial_data:
            self.schema = KintaroSchema(initial_data=initial_data["schema"])

    def __repr__(self) -> str:
        return f"KintaroCollection<{self.collection_id}>"
