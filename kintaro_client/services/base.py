from typing import Optional

from kintaro_client.exceptions import KintaroServiceInitError
from kintaro_client.utils import create_kintaro_service


class KintaroBaseService:
    repo_id: Optional[str] = None
    workspace_id: Optional[str] = None
    service = None

    def __init__(self, **kwargs):
        for param in ["repo_id", "workspace_id"]:
            if param not in kwargs:
                raise KintaroServiceInitError(f"Missing {param} param")

        if "service" not in kwargs or not kwargs.get("service"):
            kwargs["service"] = create_kintaro_service(
                use_backend_url=kwargs.get("use_backend_url", False),
            )

        for key in kwargs:
            setattr(self, key, kwargs[key])
