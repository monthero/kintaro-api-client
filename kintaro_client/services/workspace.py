from typing import Dict, List, Optional, Union

from kintaro_client.models import KintaroWorkspace
from kintaro_client.utils import ServiceError, api_request

from .base import KintaroBaseService


class KintaroWorkspaceService(KintaroBaseService):
    """This class represents the service that will communicate with both the
    **projects** service of the kintaro API
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = self.service.projects()

    @api_request
    def list_workspaces(
        self,
        repo_id: Optional[str] = None,
        sort_by: str = "project_id",
        reverse_order: bool = False,
        include_archived: bool = False,
        include_owners: bool = True,
    ) -> Union[ServiceError, List[KintaroWorkspace]]:
        ws_list: List[Dict] = (
            self.service.listProjects(
                body=dict(
                    repo_id=repo_id or self.repo_id,
                    sort_by=sort_by,
                    include_owners=include_owners,
                    include_archived=include_archived,
                    reverse_order=reverse_order,
                )
            )
            .execute()
            .get("projects", [])
        )

        for ws in ws_list:
            ws["workspace_id"] = ws.pop("project_id")

            for key in [
                "archived",
                "project_locales_source",
                "repo_ids",
                "db_id",
            ]:
                if key in ws:
                    del ws[key]

            ws["repo_id"] = repo_id or self.repo_id

        return [KintaroWorkspace(ws) for ws in ws_list]

    @api_request
    def get_workspace(
        self,
        workspace_id: Optional[str] = None,
        include_last_modified_content: bool = False,
        include_document_counts: bool = False,
    ) -> Union[ServiceError, KintaroWorkspace]:
        ws: Dict = self.service.rpcGetProject(
            body=dict(
                project_id=workspace_id or self.workspace_id,
                include_content_last_modified=(include_last_modified_content),
                include_document_counts=include_document_counts,
            )
        ).execute()

        ws["workspace_id"] = ws.pop("project_id")
        try:
            ws["repo_id"] = ws.pop("repo_ids", [])[0] or self.repo_id
        except (ValueError, IndexError, TypeError):
            ws["repo_id"] = self.repo_id

        for key in [
            "archived",
            "project_locales_source",
            "db_id",
            "allowed_operations",
        ]:
            if key in ws:
                del ws[key]
        return KintaroWorkspace(initial_data=ws)

    @api_request
    def create_workspace(
        self,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        **kwargs,
    ) -> Union[ServiceError, KintaroWorkspace]:
        locales: List[str] = sorted(list(set(kwargs.get("locales", []))))
        return self.service.createProject(
            body=dict(
                repo_ids=[repo_id or self.repo_id],
                project_id=workspace_id or self.workspace_id,
                locales=locales,
                **kwargs,
            )
        ).execute()

    @api_request
    def update_workspace(
        self,
        repo_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        **kwargs,
    ) -> Union[ServiceError, KintaroWorkspace]:
        locales: List[str] = sorted(list(set(kwargs.get("locales", []))))
        return self.service.updateProject(
            body=dict(
                repo_ids=[repo_id or self.repo_id],
                project_id=workspace_id or self.workspace_id,
                locales=locales,
                **kwargs,
            )
        ).execute()
