# Available Services

## Table of Contents
* [Repository Methods](#repository-service)
* [Workspace Methods](#workspace-service)
* [Schema Methods](#schema-service)
* [Collection Methods](#collection-service)
* [Document Methods](#document-service)
* [Resource Methods](#resource-service)

## Repository Service
```python
# get list of repositories
list_repositories(
    include_collections: bool = False, 
    use_cache: bool = False
) -> Union[ServiceError, List[KintaroRepository]]
```
```python
# get specified repository information
get_repository(
    repo_id: Optional[str] = None
) -> Union[ServiceError, KintaroRepository]
```

## Workspace Service
```python
# list workspaces within repository
list_workspaces(
    repo_id: Optional[str] = None,
    sort_by: str = "project_id",
    reverse_order: bool = False,
    include_archived: bool = False,
    include_owners: bool = True
) -> Union[ServiceError, List[KintaroWorkspace]]
```

```python
# get specified workspace
get_workspace(
    workspace_id: Optional[str] = None,
    include_last_modified_content: bool = False,
    include_document_counts: bool = False
) -> Union[ServiceError, KintaroWorkspace]
```
```python
# create a new workspace within the specified repository
create_workspace(
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    locales: Optional[List[str]] = None,
    **kwargs
) -> Union[ServiceError, KintaroWorkspace]
```

```python
# update specified workspace
update_workspace(
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    locales: Optional[List[str]] = None,
    **kwargs
) -> Union[ServiceError, KintaroWorkspace]
```

## Schema Service
```python
# list of schemas within repository
list_schemas(
    repo_id: Optional[str] = None
) -> Union[ServiceError, List[KintaroSchema]]
```

```python
# get specified repository schema
get_schema(
    schema_id: str,
    repo_id: Optional[str] = None
) -> Union[ServiceError, KintaroSchema]
```

```python
# create a new schema within the repository
create_schema(
    schema_id: str,
    fields: List[Dict],
    repo_id: Optional[str] = None
) -> Union[ServiceError, KintaroSchema]
```

```python
# update specified schema
update_schema(
    schema_id: str,
    fields: List[Dict],
    new_schema_id: Optional[str] = None,
    repo_id: Optional[str] = None,
) -> Union[ServiceError, KintaroSchema]
```

```python
# delete specified schema
delete_schema(
    schema_id: str, 
    repo_id: Optional[str] = None
) -> Optional[ServiceError]
```

## Collection Service
```python

# list of collections within repository
list_collections(
    repo_id: Optional[str] = None, 
    include_schema: bool = False
) -> Union[ServiceError, List[KintaroCollection]]

# get a short summary of the collection usage, like total document count
get_collection_usage(
    collection_id: str,
    repo_id: Optional[str] = None
) -> Union[ServiceError, Dict]

# get specified collection
get_collection(
    collection_id: str,
    repo_id: Optional[str] = None,
    include_schema: bool = False,
    include_document_count: bool = False
) -> Union[ServiceError, KintaroCollection]

# create a new collection within the repository
create_collection(
    collection_id: str,
    schema_id: str,
    repo_id: Optional[str] = None,
    description: Optional[str] = None,
    folder: Optional[str] = None
) -> Union[ServiceError, KintaroCollection]

# update specified collection
update_collection(
    current_collection_id: str,
    new_collection_id: Optional[str] = None,
    repo_id: Optional[str] = None,
    schema_id: Optional[str] = None,
    description: Optional[str] = None,
    folder: Optional[str] = None
) -> Optional[Union[ServiceError, KintaroCollection]]

# delete specified collection
delete_collection(
    collection_id: str, 
    repo_id: Optional[str]
) -> Optional[ServiceError]
```

## Document Service

```python
# get a list of (paginated) documents from a specific collection
get_collection_documents(
    collection_id: str,
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    locale: str = "root",
    take: int = 0,
    skip: int = 0,
) -> Union[ServiceError, List[KintaroDocument]]
```

```python
# get a list of (paginated) document summary objects from specified collection
get_document_summaries(
    collection_id: str,
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    take: int = 0,
    skip: int = 0
) -> Union[ServiceError, List[KintaroDocumentSummary]]
```

```python
# get a list of (paginate) document version objects
get_document_versions(
    collection_id: str,
    document_id: str,
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    take: int = 0,
    skip: int = 0
) -> Union[ServiceError, List[KintaroDocumentVersion]]
```

```python
# get specified document in requested locale
get_document(
    document_id: str,
    collection_id: str,
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    depth: int = 6,
    include_schema: bool = False,
    include_translation_status: bool = False,
    include_validation_errors: bool = False,
    include_document_versions: bool = False,
    locale: str = "root"
) -> Union[ServiceError, KintaroDocument]
```

```python
# get the current value of the requested document field in the specified locale
get_document_current_field_value(
    collection_id: str,
    document_id: str,
    field_name: str,
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    locale: str = "root",
) -> Any
```

```python
# update the value of a document field in multiple languages
update_document_field(
    collection_id: str,
    document_id: str,
    field_name: str,
    field_values: Dict[str, Any],
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> Optional[ServiceError]
```

```python
# copy the document's content in a specific locale to the requested 
# destination locales
copy_document_content_to_other_locales(
    document_id: str,
    collection_id: str,
    to_locales: List[str],
    source_locale: str = "root",
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> Optional[ServiceError]
```

```python
# create a copy of an existing document with a new, unique, id
clone_document(
    collection_id: str,
    document_id: str,
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> Union[ServiceError, KintaroDocument]
```

```python
# create a new document for the specified schema_id and collection_id within 
# the specified repository and workspace
create_document(
    collection_id: str,
    content: Dict,
    schema_id: Optional[str] = None,
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> Union[ServiceError, KintaroDocument]
```

```python
# update a document
update_document(
    document_id: str,
    collection_id: str,
    content: Dict,
    schema_id: Optional[str] = None,
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> Union[ServiceError, KintaroDocument]
```

```python
# delete a document
delete_document(
    collection_id: str,
    document_id: str,
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> Optional[ServiceError]
```

```python
# convert a readable json document content into the complex kintaro required 
# format
convert_document_content_to_kintaro_format(
    collection_id: str,
    content: Dict,
    schema_info: List[KintaroSchemaField],
    root_md5_info: Optional[Dict] = None,
    field_name_structure: Optional[Dict] = None,
    locale: str = "root",
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> List[Dict]
```

```python
# returns dictionary that is a flattened representation of the translatable
#  fields in the input doc_content dictionary
get_structured_content_values(
    doc_content: Dict,
    schema_info: List[KintaroSchemaField],
    md5_results: bool = False
) -> Dict
```

## Resource Service

```python
# get a specified resource
get_resource(
    resource_path: str,
    resource_type: str = "RASTER_IMAGE",
    tmp: bool = True,
) -> Union[ServiceError, KintaroResource]
```

```python
# create a resource (image or non-image file) in kintaro
create_resource(
    collection_id: str,
    file_info: Dict[str, str],
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> Union[ServiceError, KintaroResource]
```

```python
# create a resource (image or non-image file) in kintaro from an url or bytes
create_resource_from_url_or_bytes(
    source: Union[bytes, str],
    collection_id: str,
    repo_id: Optional[str] = None,
    workspace_id: Optional[str] = None
) -> Union[ServiceError, KintaroResource]
```
