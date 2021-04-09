from typing import Dict, Optional

from kintaro_client.models.base import BaseKintaroEntity


class KintaroResource(BaseKintaroEntity):
    file_data: Optional[str] = None
    file_name: Optional[str] = None
    resource_path: Optional[str] = None
    mime_type: Optional[str] = None

    def __init__(self, initial_data: Optional[Dict] = None):
        if not initial_data:
            return

        for entry in initial_data.pop("metadata", []):
            if entry.get("key"):
                field_name: str = entry.get("key")
                if not field_name:
                    continue

                if field_name == "file_type":
                    field_name = "mime_type"

                field_value = entry.get("values", None)
                if isinstance(field_value, list):
                    if len(field_value) == 1:
                        field_value = field_value[0]

                initial_data[field_name] = field_value

        super().__init__(initial_data=initial_data)

    def __repr__(self) -> str:
        return f"KintaroResource<{self.resource_path}>"
