# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2] - 2021-04-10

### Changed
- Get kintaro uri from environment variables instead of hardcode

## [0.1.1] - 2021-04-09

### Added
- Methods `convert_basic_field`, `convert_reference_field` and `convert_file_field` to `KintaroDocumentService`

### Changed
- Refactor `convert_document_content_to_kintaro_format` method of `KintaroDocumentService` to make
  it less complex and easier to read


## [0.1.0] - 2021-04-08

### Added

- Models **KintaroRepository**, **KintaroWorkspace**, **KintaroSchema**, **KintaroSchemaField**, **KintaroCollection**, **KintaroDocument**, **KintaroDocumentSummary**, **KintaroDocumentVersion** and **KintaroResource**. To map the API's json responses and customize their attributes to be more readable.


- Services for working with **repositories**, **workspaces**, **schemas**, **collections**, **documents** and **resources**. Each has some of the most used methods (NOT ALL) of the respective namespaces in the kintaro API.
These services can be used individually, if needed.


- **KintaroClient** class that has all the above mentioned services as attributes


- Some utility methods to make interacting with the API easier, specially when creating and updating documents.

[0.1.1]: https://github.com/monthero/kintaro-api-client/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/monthero/kintaro-api-client/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/monthero/kintaro-api-client/releases/tag/v0.1.0
