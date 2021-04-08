from typing import Dict, List, Optional, Union

from kintaro_client.models import KintaroCollection
from kintaro_client.utils import ServiceError, api_request

from .base import KintaroBaseService


class KintaroCollectionService(KintaroBaseService):
    """This class represents the service that will communicate with the
    **collections** service of the kintaro API
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = self.service.collections()

    @api_request
    def list_collections(
        self, repo_id: Optional[str] = None, include_schema: bool = False
    ) -> Union[ServiceError, List[KintaroCollection]]:
        collection_list: List[Dict] = (
            self.service.listCollections(
                body=dict(
                    repo_id=repo_id or self.repo_id,
                    include_schema=include_schema,
                )
            ).execute()
        ).get("collections", [])

        return [
            KintaroCollection(initial_data=collection)
            for collection in collection_list
        ]

    @api_request
    def get_collection_usage(
        self,
        collection_id: str,
        repo_id: Optional[str] = None,
    ) -> Union[ServiceError, Dict]:
        return self.service.getCollectionUsage(
            body=dict(
                collection_id=collection_id,
                repo_id=repo_id or self.repo_id,
            )
        ).execute()

    @api_request
    def get_collection(
        self,
        collection_id: str,
        repo_id: Optional[str] = None,
        include_schema: bool = False,
        include_document_count: bool = False,
    ) -> Union[KintaroCollection, Dict]:
        return KintaroCollection(
            initial_data=(
                self.service.getCollection(
                    body=dict(
                        repo_id=repo_id or self.repo_id,
                        collection_id=collection_id,
                        include_schema=include_schema,
                        include_document_count=include_document_count,
                    )
                ).execute()
            )
        )

    @api_request
    def update_collection(
        self,
        current_collection_id: str,
        new_collection_id: Optional[str] = None,
        repo_id: Optional[str] = None,
        schema_id: Optional[str] = None,
        description: Optional[str] = None,
        folder: Optional[str] = None,
    ) -> Optional[Union[ServiceError, KintaroCollection]]:
        request_body: Dict[str, str] = dict(
            repo_id=repo_id or self.repo_id,
            collection_id=current_collection_id,
        )

        for field_name, field_value in [
            ("updated_collection_id", new_collection_id),
            ("description", description),
            ("folder", folder),
            ("schema_id", schema_id),
        ]:
            if not field_value:
                continue

            request_body[field_name] = field_value

        if len(request_body.keys()) == 2:
            return

        return KintaroCollection(
            initial_data=(
                self.service.updateCollection(body=request_body).execute()
            )
        )

    @api_request
    def create_collection(
        self,
        collection_id: str,
        schema_id: str,
        repo_id: Optional[str] = None,
        description: Optional[str] = None,
        folder: Optional[str] = None,
    ) -> Union[ServiceError, KintaroCollection]:
        request_body: Dict[str, str] = dict(
            repo_id=repo_id or self.repo_id,
            schema_id=schema_id,
            collection_id=collection_id,
        )

        for field_name, field_value in [
            ("description", description),
            ("folder", folder),
        ]:
            if not field_value:
                continue

            request_body[field_name] = field_value

        return KintaroCollection(
            initial_data=(self.service.createCollection(body=request_body))
        )

    @api_request
    def delete_collection(
        self, collection_id: str, repo_id: Optional[str]
    ) -> Optional[ServiceError]:
        return self.service.deleteCollection(
            body=dict(
                repo_id=repo_id or self.repo_id,
                collection_id=collection_id,
            )
        )
