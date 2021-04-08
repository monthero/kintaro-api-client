from typing import Dict, List, Optional, Union

from kintaro_client.models import KintaroSchema
from kintaro_client.utils import ServiceError, api_request

from .base import KintaroBaseService


class KintaroSchemaService(KintaroBaseService):
    """This class represents the service that will communicate with the
    **schemas** service of the kintaro API
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = self.service.schemas()

    @api_request
    def list_schemas(
        self, repo_id: Optional[str] = None
    ) -> Union[ServiceError, List[KintaroSchema]]:
        schemas: List[Dict] = (
            self.service.listSchemas(
                body=dict(
                    repo_id=repo_id or self.repo_id,
                )
            ).execute()
        ).get("schemas", [])

        return [KintaroSchema(initial_data=schema) for schema in schemas]

    @api_request
    def get_schema(
        self,
        schema_id: str,
        repo_id: Optional[str] = None,
    ) -> Union[ServiceError, KintaroSchema]:
        return KintaroSchema(
            initial_data=(
                self.service.getSchema(
                    body=dict(
                        repo_id=repo_id or self.repo_id,
                        schema_id=schema_id,
                    )
                ).execute()
            )
        )

    # @api_request
    def create_schema(
        self,
        name: str,
        fields: List[Dict],
        repo_id: Optional[str] = None,
    ):
        # TODO: logic for create_schema
        raise NotImplementedError()

    @api_request
    def delete_schema(
        self, name: str, repo_id: Optional[str] = None
    ) -> Optional[ServiceError]:
        return self.service.deleteSchema(
            body=dict(
                repo_id=repo_id or self.repo_id,
                name=name,
            )
        ).execute()
