from typing import List, Optional, Union

from kintaro_client.models import KintaroRepository
from kintaro_client.utils import ServiceError, api_request

from .base import KintaroBaseService


class KintaroRepositoryService(KintaroBaseService):
    """This class represents the service that will communicate with both the
    **repos** and the **projects** services of the kintaro API
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.service = self.service.repos()

    @api_request
    def list_repositories(
        self,
        include_collections: bool = False,
        use_cache: bool = False,
    ) -> Union[ServiceError, List[KintaroRepository]]:
        return [
            KintaroRepository(initial_data=repository)
            for repository in self.service.listRepos(
                use_cache=use_cache,
                return_collections=include_collections,
            )
            .execute()
            .get("repos", [])
        ]

    @api_request
    def get_repository(
        self,
        repo_id: Optional[str] = None,
    ) -> Union[ServiceError, KintaroRepository]:
        return KintaroRepository(
            initial_data=(
                self.service.getRepo(
                    body=dict(repo_id=repo_id or self.repo_id)
                ).execute()
            )
        )
