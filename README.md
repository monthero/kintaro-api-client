# Kintaro API Client
[![Package name][package-name]][package-name] [![Current package version][curr-version-badge]][curr-version-badge] [![Supported python versions][python-version-badge]][python-version-badge] [![MIT License Badge][license-badge]][license] [![Code style: black][black-badge]](https://github.com/psf/black)

A package to programatically work with Google's Kintaro CMS.
This package offers a set of models, services and utilities to simplify the process of interacting with Kintaro's API through python.

## Table of Contents
* [Installation](#installation)
* [Usage](#usage)
    * [Using a service](#using-a-service)
    * [Using the client](#using-the-client)
        * [Service names within the client](#service-names-within-the-client)
* [Tests](#tests)
* [Changelog](#changelog)
* [Roadmap](#roadmap)
* [License](#license)
* [Contributing](#contributing)

## Installation
Install the package using pip, or easy_install
```shell
$ pip install kintaro-api-client
```

## Usage
This package exposes a set of services, each representing a namespace in the kintaro API.
As well as a client that has access to all those clients.

### Using a service
```python
import json
from typing import List
from kintaro_client.services import KintaroSchemaService
from kintaro_client.models import KintaroSchema, KintaroSchemaField

schema_service: KintaroSchemaService = KintaroSchemaService(
    repo_id="YOUR_REPO_ID",
    workspace_id="YOUR_WORKSPACE_ID",
    use_backend_url=False
)

schema: KintaroSchema = schema_service.get_schema(schema_id="YOUR_SCHEMA_ID")
schema_fields: List[KintaroSchemaField] = schema.schema_fields

print(json.dumps(schema.to_json(), indent=4))
```

### Using the client
```python
from kintaro_client.models import KintaroCollection, KintaroResource
from kintaro_client.client import KintaroClient
from kintaro_client.constants import KintaroResourceType

client: KintaroClient = KintaroClient(
    repo_id="YOUR_REPO_ID",
    workspace_id="YOUR_WORKSPACE_ID",
    use_backend_url=False
)

resource: KintaroResource = client.resources.get_resource(
    resource_path="RESOURCE_PATH_STRING",
    resource_type=KintaroResourceType.RASTER_IMAGE,
)

print(resource.file_data, resource.mime_type)

collection: KintaroColletion = client.collections.get_collection(
    collection_id="YOUR_COLLECTION_ID",
    include_document_count=True,
)

print(f"Your collection has {collection.total_document_count} documents.")
```
---

service name | client property | description
-------------|-----------------|------------
`KintaroRepositoryService` | `repositories` | Contains the methods for the `repos` namespace
`KintaroWorkspaceService` | `workspaces` | Contains the methods for the `projects` namespace
`KintaroSchemaService` | `schemas` | Contains the methods for the `schemas` namespace
`KintaroCollectionService` | `collections` | Contains the methods for the `collections` namespace
`KintaroDocumentService` | `documents` | Contains the methods for the `documents` namespace
`KintaroResouceService` | `resources` | Contains the methods for the `resource` namespace
--------------------------------------------
You can check the available methods per service [here](./docs/available-methods.md).


## Tests
WIP

## Changelog
Keep up with the changes [here](CHANGELOG.md).

## Roadmap
- Implement the missing namespaces and methods
- Add/improve documentation
- Add tests
- Improve code quality
- Add utilities to improve the experience of working with each service

## Contributing
Question, comments and suggestions are all welcome. Please create an issue or email me.
I'll do my best to reply as soon as possible and to include every suggestion in any way that I can.

- Code should be linted using [black](https://github.com/psf/black), [isort](https://github.com/PyCQA/isort) and, finally, checked with [flake8](https://github.com/PyCQA/flake8). Or just use pre-commit with the settings in the project.
- All documentation should be done in [NumPy Style Python Docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_numpy.html).

## License
MIT

[package-name]: https://img.shields.io/badge/Kintaro%20API%20Client-teal.svg
[curr-version-badge]: https://img.shields.io/badge/version-0.1.0-green.svg
[python-version-badge]: https://img.shields.io/badge/python-%3E=%203.8-red.svg
[license]: ./LICENSE
[license-badge]: https://img.shields.io/badge/license-MIT-blue.svg
[black-badge]: https://img.shields.io/badge/code%20style-black-000000.svg
