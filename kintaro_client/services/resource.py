from base64 import b64encode
from io import BytesIO
from time import time
from typing import Dict, Optional, Union
from uuid import uuid4

from magic import from_buffer
from PIL import Image
from requests import get as http_get

from kintaro_client.constants import KintaroResourceType
from kintaro_client.models import KintaroResource
from kintaro_client.utils import ServiceError, api_request

from .base import KintaroBaseService


class KintaroResourceService(KintaroBaseService):
    """This class represents the service that will communicate with both the
    **repos** and the **projects** services of the kintaro API
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = self.service.resource()

    @api_request
    def get_resource(
        self,
        resource_path: str,
        resource_type: str = "RASTER_IMAGE",
        tmp: bool = True,
    ) -> Union[ServiceError, KintaroResource]:
        """Fetches a resource given its path and type

        Raises
        ------
        ValueError
            If resource type is neither **RASTER_IMAGE** nor **BLOB_FILE**
        """
        if resource_type not in KintaroResourceType.ALL_KNOWN:
            raise ValueError(f"Invalid resource type {resource_type}")

        return KintaroResource(
            initial_data=self.service.resourceGet(
                resource_path=resource_path,
                resource_type=resource_type,
                tmp=tmp,
            ).execute()
        )

    def create_resource_from_url_or_bytes(
        self,
        source: Union[bytes, str],
        collection_id: str,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Union[ServiceError, KintaroResource]:
        mime_type: str
        file_name: str = f"{int(time() * 1000)}-{uuid4()}"
        file_data: bytes = bytes("", encoding="utf-8")

        if isinstance(source, bytes):
            mime_type = from_buffer(source[:2049])
            file_data = source
        else:
            with http_get(source, allow_redirects=True, stream=True) as res:
                res.raise_for_status()
                mime_type = res.headers.get("content-type").lower()
                for chunk in res.iter_content(chunk_size=8192):
                    file_data += chunk

        if mime_type in ["image/jpeg", "image/png", "image/webp"]:
            img = Image.open(BytesIO(file_data))
            resulting_file_data = BytesIO()
            if mime_type == "image/jpeg":
                img.save(
                    resulting_file_data,
                    "JPEG",
                    quality=85,
                    progressive=True,
                    optimize=True,
                )
            else:
                if mime_type == "image/webp":
                    mime_type = "image/png"
                    img = img.convert("RGB")
                else:
                    img = img.convert(mode="P", palette=Image.ADAPTIVE)
                img.save(resulting_file_data, "PNG", optimize=True)

            file_data = resulting_file_data.getvalue()

        return self.create_resource(
            repo_id=repo_id or self.repo_id,
            project_id=workspace_id or self.workspace_id,
            collection_id=collection_id,
            file_info=dict(
                mimetype=mime_type,
                name=file_name,
                data=b64encode(file_data).decode("utf-8"),
            ),
        )

    @api_request
    def create_resource(
        self,
        collection_id: str,
        file_info: Dict[str, str],
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Union[ServiceError, KintaroResource]:
        """
        file_info should be a dict like
        file_info = dict(
            name="file name string, example: 'image.jpg'"
            data="file base64 string with base64.b64encode(image_byte_data)",
            mimetype="file mime type string, example: 'image/jpeg'",
        )

        resource_type should be one of:
        - BLOB_FILE
        - RASTER_IMAGE
        - UNKNOWN
        """
        expected_resource_keys = ["name", "data", "mimetype"]
        if any(field not in file_info for field in expected_resource_keys):
            missing_fields = ", ".join(
                [
                    key
                    for key in file_info.keys()
                    if key not in expected_resource_keys
                ]
            )
            raise ValueError(
                f"Missing field(s): {missing_fields}, for resource creation."
            )

        mimetype = file_info.get("mimetype").lower()
        resource_type = (
            KintaroResourceType.RASTER_IMAGE
            if mimetype.startswith("image") and "svg" not in mimetype
            else KintaroResourceType.BLOB_FILE
        )

        return KintaroResource(
            initial_data=dict(
                file_data=file_info.get("data"),
                **self.service.resourceCreate(
                    body=dict(
                        repo_id=repo_id or self.repo_id,
                        project_id=workspace_id or self.workspace_id,
                        collection_id=collection_id,
                        file_name=file_info.get("name"),
                        file_data=file_info.get("data"),
                        file_type=mimetype,
                        resource_type=resource_type,
                    )
                ).execute(),
            )
        )
