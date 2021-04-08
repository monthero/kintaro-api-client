from json import JSONDecodeError, dumps as json_dumps, loads as json_loads
from typing import Dict, Optional


class BaseKintaroEntity:
    repo_id: Optional[str] = None
    workspace_id: Optional[str] = None
    modification_info: Optional[Dict] = None

    def __init__(self, initial_data: Optional[Dict] = None):
        if not initial_data:
            return

        for key in initial_data:
            if key == "mod_info":
                for field, new_field in [
                    ("created_on_millis", "created_at"),
                    ("updated_on_millis", "updated_at"),
                ]:
                    if field in initial_data[key]:
                        initial_data[key][new_field] = initial_data[key].pop(
                            field
                        )
                self.modification_info = initial_data[key]
            elif "json" in key:
                if key in ["metadata_json", "nested_metadata_json"]:
                    continue

                field_value = initial_data[key]
                try:
                    field_value = json_loads(field_value)
                except (TypeError, JSONDecodeError, ValueError):
                    pass
                setattr(self, key, field_value)
            elif key == "project_id":
                self.workspace_id = initial_data[key]
            else:
                setattr(self, key, initial_data[key])

    def to_json(self) -> Dict:
        """Returns json object respective to this class's instance"""
        return json_loads(
            json_dumps(
                self,
                default=lambda o: o.__dict__,
            )
        )
