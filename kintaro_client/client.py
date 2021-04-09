import logging
from typing import Optional

from .exceptions import KintaroClientInitError
from .services import (
    KintaroCollectionService,
    KintaroDocumentService,
    KintaroRepositoryService,
    KintaroResourceService,
    KintaroSchemaService,
    KintaroWorkspaceService,
)
from .utils import create_kintaro_service


logger = logging.getLogger(__name__)


class KintaroClient:
    repo_id: Optional[str] = None
    workspace_id: Optional[str] = None
    repositories: Optional[KintaroRepositoryService] = None
    workspaces: Optional[KintaroWorkspaceService] = None
    schemas: Optional[KintaroSchemaService] = None
    collections: Optional[KintaroCollectionService] = None
    documents: Optional[KintaroDocumentService] = None
    resources: Optional[KintaroResourceService] = None

    def __init__(
        self,
        repo_id: str,
        workspace_id: str,
        use_backend_url: bool = False,
        **kwargs,
    ):
        """
        Parameters
        ----------
        repo_id : str
            The repository/site's string id
        workspace_id : str
            The project/workspace's string id
        **kwargs : Dict
            Arbitrary keyword arguments.
        """
        if any(not attr for attr in [repo_id, workspace_id]):
            raise KintaroClientInitError(
                "Missing one of the following attributes: repo_id,"
                " and/or workspace_id."
            )

        self.repo_id = repo_id
        self.workspace_id = workspace_id
        service = create_kintaro_service(use_backend_url=use_backend_url)

        for kwarg in kwargs:
            setattr(self, kwarg, kwargs.get(kwarg))

        for attr, cls in [
            ("repositories", KintaroRepositoryService),
            ("workspaces", KintaroWorkspaceService),
            ("schemas", KintaroSchemaService),
            ("collections", KintaroCollectionService),
            ("documents", KintaroDocumentService),
            ("resources", KintaroResourceService),
        ]:
            setattr(
                self,
                attr,
                cls(
                    **dict(
                        service=service,
                        repo_id=self.repo_id,
                        workspace_id=self.workspace_id,
                        use_backend_url=use_backend_url,
                        **kwargs,
                    )
                ),
            )

        logger.info("-------- Kintaro client created -------")
