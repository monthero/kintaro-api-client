from functools import update_wrapper
from json import loads as json_loads
from typing import Any, Dict, List, NewType, Union

from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError as GoogleApiHttpError

from .exceptions import KintaroServiceInitError


ServiceError = NewType("ServiceError", Dict)  # error from kintaro


def create_kintaro_service():
    """Creates the google service `Resource` object that will handle the
    kintaro api calls.
    """
    # host = "backend-dot-kintaro-content-server.appspot.com"
    host = "kintaro-content-server.appspot.com"
    doc_url = f"https://{host}/_ah/api/discovery/v1/apis/content/v1/rest"

    scopes: List[str] = [
        "https://www.googleapis.com/auth/kintaro",
        "https://www.googleapis.com/auth/userinfo.email",
    ]

    credentials, project = default(scopes=scopes)

    service = build(
        "content",
        "v1",
        credentials=credentials,
        discoveryServiceUrl=doc_url,
    )

    if not service:
        raise KintaroServiceInitError(
            "Failed to create Kintaro Service, check "
            "'create_kintaro_service', your auth credentials or connection."
        )

    return service


def parse_google_api_error_dict(obj: Any):
    if isinstance(obj, (list, tuple)):
        return [parse_google_api_error_dict(obj=entry) for entry in obj]
    elif isinstance(obj, dict):
        return {
            key: parse_google_api_error_dict(obj=obj[key]) for key in obj.keys()
        }
    else:
        try:
            new_obj = json_loads(obj)
            return parse_google_api_error_dict(obj=new_obj)
        except (ValueError, TypeError):
            return obj


def prepare_google_api_error_response(
    error: Union[bytes, str, Dict]
) -> ServiceError:
    if isinstance(error, bytes):
        error = error.decode("utf-8")
    if isinstance(error, str):
        error = json_loads(error)
    if (
        isinstance(error, dict)
        and "error" in error
        and isinstance(error.get("error", {}), dict)
    ):
        error["errors"] = [error.pop("error", {})]
    return parse_google_api_error_dict(obj=error)


def api_request(fn):
    def wrapper_function(self, *args, **kwargs):
        try:
            return fn(self, *args, **kwargs)
        except GoogleApiHttpError as e:
            return prepare_google_api_error_response(error=e.content)

    return update_wrapper(wrapper_function, fn)
