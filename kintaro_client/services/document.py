from hashlib import md5
from multiprocessing import cpu_count
from typing import Any, Dict, List, Optional, Union

from dry_pyutils import convert_dict_keys_case, convert_string_case
from googleapiclient.errors import HttpError as GoogleApiHttpError
from joblib import Parallel, delayed

from kintaro_client.constants import KintaroFieldType
from kintaro_client.exceptions import (
    KintaroCreateDocumentError,
    KintaroWrongContentFormatError,
    NoResourcePathFoundError,
)
from kintaro_client.models import (
    KintaroDocument,
    KintaroDocumentSummary,
    KintaroDocumentVersion,
    KintaroSchema,
    KintaroSchemaField,
)
from kintaro_client.services.base import KintaroBaseService
from kintaro_client.services.collection import KintaroCollectionService
from kintaro_client.services.resource import KintaroResourceService
from kintaro_client.services.schema import KintaroSchemaService
from kintaro_client.utils import (
    ServiceError,
    api_request,
    prepare_google_api_error_response,
)


NUM_CORES = cpu_count()


class KintaroDocumentService(KintaroBaseService):
    """This class represents the service that will communicate with the
    **documents** service of the kintaro API
    """

    schema_service: Optional[KintaroSchemaService] = None
    collection_service: Optional[KintaroCollectionService] = None
    resource_service: Optional[KintaroResourceService] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.collection_service = KintaroCollectionService(**kwargs)
        self.resource_service = KintaroResourceService(**kwargs)
        self.schema_service = KintaroSchemaService(**kwargs)
        self.service = self.service.documents()

    @api_request
    def get_collection_documents(
        self,
        collection_id: str,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        locale: str = "root",
        take: int = 0,
        skip: int = 0,
    ) -> Union[ServiceError, List[KintaroDocument]]:
        """Gets the documents, in the requested locale, from the requested
        collection_id, workspace_id and repo_id

        Parameters
        ----------
        collection_id : str
            The collection id string.
        repo_id : Optional[str]
            The repo id string. If not provided, the **repo_id**
            attribute from
             the class will be used.
        workspace_id : Optional[str]
            The workspace id string. If not provided,
            the **workspace_id**
             attribute from the class will be used.
        locale : str
            The kintaro locale string that specifies the language of
            the fetched
             documents.
        take : int
            Works as a pagination parameter, will take X documents
            from result.
            If take == 0 it will take all.
        skip : int
            Works as a pagination parameter, will skip X documents
            from result.
            If take == 0 it will take all.

        Returns
        -------
        Union[ServiceError, List[KintaroDocument]]
            A list of KintaroDocument objects when successful,
            an error dict
             otherwise
        """
        documents: List[Dict] = (
            (
                self.service.searchDocuments(
                    body=dict(
                        collection_id=collection_id,
                        repo_id=repo_id or self.repo_id,
                        project_id=workspace_id or self.workspace_id,
                        result_options=dict(
                            limit=take,
                            offset=skip,
                            return_schema=False,
                            return_json=True,
                        ),
                        locale=locale,
                    )
                ).execute()
            )
            .get("document_list", {})
            .get("documents", [])
        )

        return [KintaroDocument(initial_data=doc) for doc in documents]

    @api_request
    def get_document_summaries(
        self,
        collection_id: str,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        take: int = 0,
        skip: int = 0,
    ) -> Union[ServiceError, List[KintaroDocumentSummary]]:
        """Gets document summaries from the requested **collection_id**,
         **workspace_id** and **repo_id**.

        Parameters
        ----------
        collection_id : str
            The collection id string.
        repo_id : Optional[str]
            The repo id string. If not provided, the **repo_id** attribute from
             the class will be used.
        workspace_id : Optional[str]
            The workspace id string. If not provided, the **workspace_id**
             attribute from the class will be used.
        take : int
            Works as a pagination parameter, will take X documents from result.
            If take == 0 it will take all.
        skip : int
            Works as a pagination parameter, will skip X documents from result.
            If take == 0 it will take all.

        Returns
        -------
        Union[ServiceError, List[KintaroDocumentSummary]]
            A list of document summary objects when successful, an error dict
             otherwise
        """
        return [
            KintaroDocumentSummary(doc_summary)
            for doc_summary in (
                self.service.listDocumentSummaries(
                    collection_id=collection_id,
                    repo_id=repo_id or self.repo_id,
                    project_id=workspace_id or self.workspace_id,
                    limit=take,
                    offset=skip,
                    return_json=True,
                )
                .execute()
                .get("documents", [])
            )
        ]

    @api_request
    def get_document_versions(
        self,
        collection_id: str,
        document_id: str,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        take: int = 0,
        skip: int = 0,
    ) -> Union[ServiceError, List[KintaroDocumentVersion]]:
        doc_versions: List[Dict] = sorted(
            self.service.listDocumentVersions(
                body=dict(
                    repo_id=repo_id or self.repo_id,
                    project_id=workspace_id or self.workspace_id,
                    collection_id=collection_id,
                    document_id=document_id,
                    limit=take,
                    offset=skip,
                )
            )
            .execute()
            .get("versions", []),
            key=lambda v: v.get("mod_info", {}).get("updated_on_millis"),
            reverse=True,
        )

        return [
            KintaroDocumentVersion(initial_data=version)
            for version in doc_versions
        ]

    @api_request
    def get_document(
        self,
        document_id: str,
        collection_id: str,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        depth: int = 6,
        include_schema: bool = False,
        include_translation_status: bool = False,
        include_validation_errors: bool = False,
        include_document_versions: bool = False,
        locale: str = "root",
    ) -> Union[ServiceError, KintaroDocument]:
        document_dict: Dict = (
            self.service.rpcDocumentGet(
                body=dict(
                    repo_id=repo_id or self.repo_id,
                    project_id=workspace_id or self.workspace_id,
                    collection_id=collection_id,
                    document_id=document_id,
                    use_json=True,
                    include_schema=include_schema,
                    include_translation_status=include_translation_status,
                    include_validation_errors=include_validation_errors,
                    depth=depth,
                    locale=locale,
                )
            )
        ).execute()

        if include_document_versions:
            versions: List[
                KintaroDocumentVersion
            ] = self.get_document_versions(
                repo_id=repo_id or self.repo_id,
                workspace_id=workspace_id or self.workspace_id,
                collection_id=collection_id,
                document_id=document_id,
            )

            if isinstance(versions, list):
                document_dict["versions"] = versions

        if not include_schema and "schema" in document_dict:
            del document_dict["schema"]

        return KintaroDocument(initial_data=document_dict)

    def get_document_current_field_value(
        self,
        collection_id: str,
        document_id: str,
        field_name: str,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        locale: str = "root",
    ) -> Any:
        error_msg = None
        current_field_value: Any = None
        try:
            current_field_value = next(
                iter(
                    (
                        self.service.getFieldsByDescriptor(
                            body=dict(
                                field_headers=[
                                    dict(
                                        repo_id=repo_id or self.repo_id,
                                        project_id=workspace_id
                                        or self.workspace_id,
                                        collection_id=collection_id,
                                        document_id=document_id,
                                        field_descriptor=field_name,
                                        locale=locale,
                                    )
                                ]
                            )
                        )
                        .execute()
                        .get("field_values", [])
                    )
                ),
                {},
            ).get("value")
        except GoogleApiHttpError as e:
            error = prepare_google_api_error_response(error=e.content)
            error_msg = next(iter(error.get("errors", [])), {}).get("message")

        if current_field_value and not error_msg:
            return current_field_value

        if error_msg:
            if "is repeated and should be followed by an index" in error_msg:
                i = 0
                current_values: List = []
                while True:
                    try:
                        values = iter(
                            self.service.documents()
                            .getFieldsByDescriptor(
                                body=dict(
                                    field_headers=[
                                        dict(
                                            repo_id=self.repo_id,
                                            project_id=self.workspace_id,
                                            collection_id=collection_id,
                                            document_id=document_id,
                                            field_descriptor=(
                                                f"{field_name}.{i}"
                                            ),
                                            locale=locale,
                                        )
                                    ]
                                )
                            )
                            .execute()
                            .get("field_values", [])
                        )

                        current_values.append(next(values, {}).get("value"))
                        i += 1
                    except (AttributeError, ValueError, IndexError, TypeError):
                        break
                return current_values

    @api_request
    def execute_update_document_field(
        self,
        collection_id: str,
        document_id: str,
        field_name: str,
        field_value: Dict[str, Any],
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        locale: str = "root",
    ) -> Optional[ServiceError]:
        self.service.editField(
            body=dict(
                document_id=document_id,
                collection_id=collection_id,
                repo_id=repo_id or self.repo_id,
                project_id=workspace_id or self.workspace_id,
                locale=locale,
                field_descriptor=field_name,
                field_value=field_value,
            )
        ).execute()
        return

    def update_document_field(
        self,
        collection_id: str,
        document_id: str,
        field_name: str,
        field_values: Dict[str, Any],
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Optional[ServiceError]:
        """Updates the value of a document's field, in one or more locales.

        {
            "root": "New title",
            "nl_nl": "Nieuwe titel",
            "ja_jp": "新しいタイトル",
            "ko_kr": "새 제목",
            "pt-PT_pt": "Novo título",
            "es_ar": "Nuevo título"
        }
        """
        field_name = convert_string_case(
            (
                ".".join(field_name.split("--"))
                if "--" in field_name
                else field_name
            ),
            case_style="SNAKE",
        )

        # Convert case of possible nested fields
        for key in field_values.keys():
            field_values[key] = convert_dict_keys_case(
                field_values[key], case_style="SNAKE"
            )

        if "root" in field_values:
            # update root first if it's present because the other locales
            #  depend on it
            root_value = field_values["root"]
            self.execute_update_document_field(
                document_id=document_id,
                collection_id=collection_id,
                repo_id=repo_id or self.repo_id,
                workspace_id=workspace_id or self.workspace_id,
                locale="root",
                field_name=field_name,
                field_value=dict(value=root_value),
            )
        else:
            root_value = self.get_document_current_field_value(
                document_id=document_id,
                collection_id=collection_id,
                repo_id=repo_id or self.repo_id,
                workspace_id=workspace_id or self.workspace_id,
                locale="root",
                field_name=field_name,
            )

        # check if root_value is error
        if isinstance(root_value, ServiceError) and "errors" in root_value:
            return root_value

        non_root_locales: List[str] = [
            loc for loc in field_values.keys() if loc != "root"
        ]

        if len(non_root_locales) == 0:
            return

        root_md5 = md5(root_value.encode("utf-8")).hexdigest()

        for locale in non_root_locales:
            self.execute_update_document_field(
                document_id=document_id,
                collection_id=collection_id,
                repo_id=repo_id or self.repo_id,
                workspace_id=workspace_id or self.workspace_id,
                locale=locale,
                field_name=field_name,
                field_value=dict(
                    value=field_values[locale], root_md5=root_md5
                ),
            )

    @api_request
    def copy_document_content_to_other_locales(
        self,
        document_id: str,
        collection_id: str,
        to_locales: List[str],
        source_locale: str = "root",
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Optional[ServiceError]:
        """Copies the contents of the document from the specified source locale
        to the requested destination locales
        """
        if not to_locales:
            return

        self.service.copyDocumentLocaleContent(
            body=dict(
                repo_id=repo_id or self.repo_id,
                project_id=workspace_id or self.workspace_id,
                collection_id=collection_id,
                document_id=document_id,
                from_locale=source_locale,
                to_locales=to_locales,
            )
        ).execute()

        # TODO: Missing logic for recursively copying nested
        #  ReferenceField documents

    @api_request
    def clone_document(
        self,
        collection_id: str,
        document_id: str,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Union[ServiceError, KintaroDocument]:
        """Creates a copy of the requested document and assigns it a new id"""
        return KintaroDocument(
            initial_data=self.service.copyDocument(
                body=dict(
                    repo_id=repo_id or self.repo_id,
                    project_id=workspace_id or self.workspace_id,
                    collection_id=collection_id,
                    document_id=document_id,
                )
            ).execute()
        )

    @api_request
    def create_document(
        self,
        collection_id: str,
        content: Dict,
        schema_id: Optional[str] = None,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Union[ServiceError, KintaroDocument]:
        if "root" not in content.keys():
            raise KintaroCreateDocumentError(
                "Can not create document without content for root locale"
            )

        schema: KintaroSchema
        if schema_id:
            schema = self.schema_service.get_schema(
                schema_id=schema_id,
                repo_id=repo_id or self.repo_id,
            )
        else:
            schema = self.collection_service.get_collection(
                collection_id=collection_id,
                repo_id=repo_id or self.repo_id,
                include_schema=True,
            ).schema

        if not isinstance(schema, KintaroSchema):
            raise ValueError("Failed to retrieve schema")

        # create first for "root" and then update other locales
        root_fields = self.convert_document_content_to_kintaro_format(
            collection_id=collection_id,
            content=content.get("root", {}),
            schema_info=schema.schema_fields,
            locale="root",
        )

        document_dict: Dict = self.service.createDocument(
            body=dict(
                collection_id=collection_id,
                repo_id=repo_id or self.repo_id,
                project_id=workspace_id or self.workspace_id,
                use_json=True,
                contents=dict(locale="root", fields=root_fields),
            )
        ).execute()

        if "document_id" not in document_dict:
            raise KintaroCreateDocumentError("Failed to create document")

        non_root_locales_contents: Dict[str, Dict] = {
            loc: loc_content
            for loc, loc_content in content.items()
            if loc != "root"
        }

        if non_root_locales_contents:
            self.update_document(
                repo_id=repo_id or self.repo_id,
                project_id=workspace_id or self.workspace_id,
                collection_id=collection_id,
                document_id=document_dict.get("document_id"),
                content=non_root_locales_contents,
            )

        return self.get_document(
            document_id=document_dict.get("document_id"),
            collection_id=collection_id,
            repo_id=repo_id or self.repo_id,
            project_id=workspace_id or self.workspace_id,
            locale="root",
        )

    @api_request
    def execute_update_command(self, request_body: Dict):
        self.service.multiDocumentUpdate(body=request_body).execute()

    @api_request
    def update_document(
        self,
        document_id: str,
        collection_id: str,
        content: Dict,
        schema_id: Optional[str] = None,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Union[ServiceError, KintaroDocument]:
        schema: KintaroSchema
        if schema_id:
            schema = self.schema_service.get_schema(
                repo_id=repo_id or self.repo_id,
                schema_id=schema_id,
            )
        else:
            schema = self.collection_service.get_collection(
                collection_id=collection_id,
                repo_id=repo_id or self.repo_id,
                include_schema=True,
            ).schema

        if not isinstance(schema, KintaroSchema):
            raise ValueError("Failed to retrieve schema")

        root_content: Dict = {}

        if "root" in content.keys():
            root_content = content.get("root", {})

            # processing root content
            fields = self.convert_document_content_to_kintaro_format(
                repo_id=repo_id or self.repo_id,
                workspace_id=workspace_id or self.workspace_id,
                collection_id=collection_id,
                content=root_content,
                schema_info=schema.schema_fields,
                locale="root",
            )

            result = self.execute_update_command(
                request_body=dict(
                    collection_id=collection_id,
                    repo_id=repo_id or self.repo_id,
                    project_id=workspace_id or self.workspace_id,
                    updated_content=[
                        dict(
                            document_id=document_id,
                            contents=[dict(locale="root", fields=fields)],
                        )
                    ],
                )
            )
            if result is not None:
                return result

        non_root_locales = [loc for loc in content.keys() if loc != "root"]
        root_md5_info = None
        if non_root_locales:
            if "root" not in content.keys():
                root_content = self.get_document(
                    repo_id=repo_id or self.repo_id,
                    workspace_id=workspace_id or self.workspace_id,
                    document_id=document_id,
                    collection_id=collection_id,
                    locale="root",
                ).content.get("root")

            root_md5_info = self.get_structured_content_values(
                doc_content=root_content,
                schema_info=schema.schema_fields,
                md5_results=True,
            )

        locale_contents_list: List[Dict] = []
        for locale in non_root_locales:
            locale_contents_list.append(
                dict(
                    locale=locale,
                    fields=self.convert_document_content_to_kintaro_format(
                        repo_id=repo_id or self.repo_id,
                        workspace_id=workspace_id or self.workspace_id,
                        collection_id=collection_id,
                        content=content[locale],
                        schema_info=schema.schema_fields,
                        locale=locale,
                        root_md5_info=root_md5_info,
                        field_name_structure=(
                            self.get_structured_content_values(
                                doc_content=content[locale],
                                schema_info=schema.schema_fields,
                                md5_results=False,
                            )
                        ),
                    ),
                )
            )

        if locale_contents_list:
            self.execute_update_command(
                request_body=dict(
                    repo_id=repo_id or self.repo_id,
                    project_id=workspace_id or self.workspace_id,
                    collection_id=collection_id,
                    updated_content=[
                        dict(
                            document_id=document_id,
                            contents=locale_contents_list,
                        )
                    ],
                )
            )

        return self.get_document(
            repo_id=repo_id or self.repo_id,
            workspace_id=workspace_id or self.workspace_id,
            document_id=document_id,
            collection_id=collection_id,
            locale="root",
        )

    @api_request
    def delete_document(
        self,
        collection_id: str,
        document_id: str,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Optional[ServiceError]:
        """Deletes the requested document"""
        self.service.deleteDocument(
            body=dict(
                repo_id=repo_id or self.repo_id,
                project_id=workspace_id or self.workspace_id,
                collection_id=collection_id,
                document_id=document_id,
            )
        ).execute()
        return

    def multi_document_action(
        self,
        request_bodies: List[Dict],
        action: str = "create",
    ) -> List[Union[ServiceError, KintaroDocument]]:
        """Creates or updates documents in batches of 20"""
        if action not in ["create", "update"]:
            raise ValueError(f'Invalid action provided "{action}"')
        return Parallel(n_jobs=NUM_CORES - 1, batch_size=20)(
            delayed(getattr(self, f"{action}_document"))(**request)
            for request in request_bodies
        )

    def convert_document_content_to_kintaro_format(
        self,
        collection_id: str,
        content: Dict,
        schema_info: List[KintaroSchemaField],
        root_md5_info: Optional[Dict] = None,
        field_name_structure: Optional[Dict] = None,
        locale: str = "root",
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[Dict]:
        """
        Converts the request body to the format that is accepted by kintaro
        """
        is_update: bool = isinstance(root_md5_info, dict) and isinstance(
            field_name_structure, dict
        )

        schema_info: Dict = {field.name: field for field in schema_info}

        fields = []
        if not content:
            content = {}

        for field_name in content.keys():
            if field_name not in schema_info:
                continue

            field_value = content[field_name]
            schema_field_info: KintaroSchemaField = schema_info.get(field_name)

            if not isinstance(field_value, list):
                field_value = [field_value]

            if schema_field_info.type in KintaroFieldType.FILE_FIELDS:
                fields.extend(
                    self.convert_file_field(
                        field_name=field_name,
                        field_value=field_value,
                        repo_id=repo_id or self.repo_id,
                        workspace_id=workspace_id or self.workspace_id,
                        collection_id=collection_id,
                    )
                )
            elif schema_field_info.type == KintaroFieldType.NESTED:
                nested_fields_info_list = [
                    self.convert_document_content_to_kintaro_format(
                        repo_id=repo_id or self.repo_id,
                        workspace_id=workspace_id or self.workspace_id,
                        collection_id=collection_id,
                        content=item,
                        schema_info=schema_info.get(
                            field_name
                        ).schema_fields,  # NOQA
                        locale=locale,
                        root_md5_info=root_md5_info,
                        field_name_structure=field_name_structure,
                    )
                    for item in field_value
                ]

                fields.append(
                    dict(
                        field_name=field_name,
                        nested_field_values=[
                            dict(fields=entry)
                            for entry in nested_fields_info_list
                        ],
                    )
                )
            elif schema_field_info.type == KintaroFieldType.REFERENCE:
                fields.append(
                    self.convert_reference_field(
                        field_name=field_name,
                        field_value=field_value,
                        repo_id=repo_id or self.repo_id,
                        workspace_id=workspace_id or self.workspace_id,
                        locale=locale,
                    )
                )
            else:
                fields.append(
                    self.convert_basic_field(
                        schema_field_info=schema_field_info,
                        field_name=field_name,
                        field_value=field_value,
                        field_name_structure=field_name_structure,
                        root_md5_info=root_md5_info,
                        is_update=is_update,
                    )
                )
        return fields

    def convert_file_field(
        self,
        collection_id: str,
        field_name: str,
        field_value: List,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> List[Dict]:
        fields: List[Dict] = []

        for entry in field_value:
            if not entry:
                continue

            expected_file_fields: List[str] = ["mimetype", "name", "data"]
            resource_path = None

            if isinstance(entry, dict):
                if any(field in entry for field in expected_file_fields):
                    result = self.resource_service.create_resource(
                        repo_id=repo_id or self.repo_id,
                        workspace_id=workspace_id or self.workspace_id,
                        collection_id=collection_id,
                        file_info=entry,
                    )

                    if isinstance(result, dict) and "errors" in result:
                        raise KintaroWrongContentFormatError(result)

                    resource_path = result.resource_path
                else:
                    for alternative_field_name in [
                        "image_path",
                        "file_path",
                        "resource_path",
                        "path",
                    ]:
                        if alternative_field_name in entry:
                            resource_path = entry.get(alternative_field_name)
                            if resource_path:
                                break

            else:
                resource_path = entry

            if not resource_path:
                if isinstance(entry, dict) and entry.get("url"):
                    result = self.resource_service.create_resource_from_url_or_bytes(  # NOQA
                        repo_id=repo_id or self.repo_id,
                        workspace_id=(workspace_id or self.workspace_id),
                        collection_id=collection_id,
                        source=entry["url"],
                    )

                    if isinstance(result, dict) and "errors" in result:
                        raise KintaroWrongContentFormatError(result)

                    resource_path = result.resource_path
                else:
                    raise NoResourcePathFoundError(
                        "No information available to create resource"
                    )

            fields.append(
                dict(
                    field_name=field_name,
                    nested_field_values=[
                        dict(
                            fields=[
                                dict(
                                    field_name="file_path",
                                    field_values=[
                                        dict(
                                            type="STRING", value=resource_path
                                        )
                                    ],
                                )
                            ]
                        )
                    ],
                )
            )
        return fields

    def convert_reference_field(
        self,
        field_name: str,
        field_value: List,
        locale: str = "root",
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict:
        to_create_list: List = []
        to_update_list: List = []

        for entry in field_value:
            if not entry:
                continue

            if not entry.get("collection_id") or "content" not in entry:
                continue

            request_body: Dict = dict(
                repo_id=repo_id or self.repo_id,
                workspace_id=workspace_id or self.workspace_id,
                collection_id=entry["collection_id"],
                content={locale: entry["content"]},
            )

            if entry.get("document_id"):
                to_update_list.append(
                    dict(
                        document_id=entry["document_id"],
                        **request_body,
                    )
                )
            else:
                to_create_list.append(request_body)

        nested_documents: List = []
        if to_create_list:
            nested_documents.extend(
                self.multi_document_action(
                    action="create",
                    request_bodies=to_create_list,
                )
            )
        if to_update_list:
            nested_documents.extend(
                self.multi_document_action(
                    action="update",
                    request_bodies=to_update_list,
                )
            )

        referred_document: Union[KintaroDocument, ServiceError]
        field_entries: List = []

        for referred_document in nested_documents:
            if (
                isinstance(referred_document, dict)
                and "errors" in referred_document
            ):
                raise KintaroWrongContentFormatError(referred_document)

            referred_document_id: Optional[str]
            referred_collection_id: Optional[str]

            if isinstance(referred_document, dict):
                referred_collection_id = referred_document.get("collection_id")
                referred_document_id = referred_document.get("document_id")
            else:
                referred_collection_id = referred_document.collection_id
                referred_document_id = referred_document.document_id

            if not referred_document_id:
                raise AttributeError(
                    f"Impossible to read property 'document_id' from "
                    f"type {type(referred_document)}"
                )

            field_entries.append(
                dict(
                    fields=[
                        dict(
                            field_name="repo_id",
                            field_values=[
                                dict(
                                    type="STRING",
                                    value=repo_id or self.repo_id,
                                )
                            ],
                        ),
                        dict(
                            field_name="collection_id",
                            field_values=[
                                dict(
                                    type="STRING",
                                    value=referred_collection_id,
                                )
                            ],
                        ),
                        dict(
                            field_name="document_id",
                            field_values=[
                                dict(type="STRING", value=referred_document_id)
                            ],
                        ),
                    ]
                )
            )

        return dict(
            field_name=field_name,
            nested_field_values=field_entries,
        )

    @staticmethod
    def convert_basic_field(
        schema_field_info: KintaroSchemaField,
        field_name: str,
        field_value: List,
        is_update: bool,
        root_md5_info: Optional[Dict] = None,
        field_name_structure: Optional[Dict] = None,
    ) -> Dict:
        field_type = KintaroFieldType.STRING
        if schema_field_info.type == KintaroFieldType.NUMBER:
            field_type = "INT"
        elif schema_field_info.type == KintaroFieldType.BOOL:
            field_type = "BOOL"

        prepared_field_value = []
        for entry in field_value:
            entry = str(entry) if entry is not None else None
            field_value = dict(
                value=entry,
                type=field_type,
            )
            if is_update and isinstance(field_name_structure, dict):
                for key in field_name_structure.keys():
                    val = (
                        str(field_name_structure[key])
                        if field_name_structure[key] is not None
                        else None
                    )
                    if val == entry:
                        if (
                            isinstance(root_md5_info, dict)
                            and key in root_md5_info
                        ):
                            field_value["root_md5"] = root_md5_info.get(key)
                        break
            prepared_field_value.append(field_value)

        return dict(
            field_name=field_name,
            field_values=prepared_field_value,
        )

    def get_structured_content_values(
        self,
        doc_content: Dict,
        schema_info: List[KintaroSchemaField],
        md5_results: bool = False,
    ) -> Dict:
        """Recursively builds a flattened version of the content dictionary
        to allow updating non-root locales's contents. Only grabs translatable
        or locale-varied fields. For example if the original content is:
        {
            "field_one": "string",  # <---- translatable
            "nested_field": {
                "field_one": "string",
                "field_two": "string",  # <---- translatable
            },
            "nested_list_field": [
                {
                    "field_one": "string",
                    "field_two": "string",  # <---- translatable
                },
            ],
            "list_field": ["uno", "dos", "tres"]  # <---- translatable
        }

        Returns
        -------
        Dict
            A dictionary that is a flattened representation of the translatable
             fields in the input ``doc_content`` dictionary. Example:
            {
                "field_one": "string",
                "nested_field.field_two": "string",
                "nested_list_field.0.field_two": "string",
                "list_field.0": "string",
                "list_field.1": "string",
                "list_field.2": "string",
            }
        """

        result: Dict = {}
        schema_info: Dict[str, KintaroSchemaField] = {
            field.name: field for field in schema_info
        }

        for field_name in doc_content.keys():
            field_value = doc_content[field_name]
            schema_field: KintaroSchemaField = schema_info.get(field_name)

            is_repeated: bool = schema_field.repeated
            field_type: str = schema_field.type

            if field_type in [
                KintaroFieldType.REFERENCE,
                KintaroFieldType.BLOB_FILE,
                KintaroFieldType.IMAGE_FILE,
            ]:
                pass

            elif field_type == KintaroFieldType.NESTED:
                if not isinstance(field_value, list):
                    field_value = [field_value]

                for eidx, entry in enumerate(field_value):
                    nested_result = self.get_structured_content_values(
                        doc_content=entry,
                        schema_info=schema_field_info.schema_fields,  # noqa
                        md5_results=md5_results,
                    )

                    if is_repeated:
                        for nested_key in nested_result.keys():
                            result[
                                f"{field_name}.{eidx}.{nested_key}"
                            ] = nested_result[nested_key]

                    else:
                        for nested_key in nested_result.keys():
                            result[
                                f"{field_name}.{nested_key}"
                            ] = nested_result[nested_key]

            else:
                if not any(
                    getattr(schema_field, field)
                    for field in [
                        "translatable",
                        "locale_varied",
                    ]
                ):
                    # if field is not translatable continue
                    continue

                if is_repeated:
                    if not isinstance(field_value, list):
                        field_value = [field_value]

                    for eidx, entry in enumerate(field_value):
                        if entry is not None:
                            result[f"{field_name}.{eidx}"] = (
                                md5(entry.encode("utf-8")).hexdigest()
                                if md5_results
                                else entry
                            )
                else:
                    if field_value is not None:
                        result[field_name] = (
                            md5(field_value.encode("utf-8")).hexdigest()
                            if md5_results
                            else field_value
                        )

        return result
