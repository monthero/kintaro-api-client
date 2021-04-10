from os import environ
from typing import List


class KintaroFieldType:
    IMAGE_FILE = "ImageFileField"
    BLOB_FILE = "BlobFileField"
    NESTED = "NestedField"
    REFERENCE = "ReferenceField"
    NUMBER = "NumberField"
    BOOL = "BooleanField"
    STRING = "StringField"
    TEXT = "TextField"
    HTML = "HtmlField"
    MARKDOWN = "MarkdownField"
    SINGLE_CHOICE = "SingleChoiceField"
    MULTI_CHOICE = "MultiChoiceField"
    JSON = "JsonField"
    DATE = "DateField"
    DATETIME = "DateTimeField"
    LINK = "LinkField"
    IMAGE_LINK = "ImageLinkField"

    FILE_FIELDS = [IMAGE_FILE, BLOB_FILE]


class KintaroResourceType:
    UNKNOWN = "UNKNOWN"
    RASTER_IMAGE = "RASTER_IMAGE"
    BLOB_FILE = "BLOB_FILE"

    ALL_KNOWN = [RASTER_IMAGE, BLOB_FILE]


KINTARO_URI: str = environ["KINTARO_URI"]
KINTARO_BACKEND_URI: str = f"backend-dot-{KINTARO_URI}"
KINTARO_DISCOVERY_SERVICE_URL: str = (
    "https://[BASE_URL]/_ah/api/discovery/v1/apis/content/v1/rest"
)

GOOGLE_AUTH_SCOPES: List[str] = [
    "https://www.googleapis.com/auth/kintaro",
    "https://www.googleapis.com/auth/userinfo.email",
]
