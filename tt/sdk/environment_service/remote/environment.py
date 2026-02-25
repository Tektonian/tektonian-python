from __future__ import annotations  # 3.7+ 에서 필요
from typing import TYPE_CHECKING

from dataclasses import dataclass
from urllib.parse import urlsplit

from tt.base.error.error import TektonianBaseError

from tt.sdk.environment_service.common.environment import IEnvironment


@dataclass
class RemoteEnvironment(IEnvironment):

    def snapshop(self):
        return

    def load_env(self):
        return

    def __post_init__(self):
        url = (
            urlsplit(self.env_json_uri)
            if isinstance(self.env_json_uri, str)
            else self.env_json_uri
        )

        if url.scheme not in ["http", "https"]:
            raise TektonianBaseError(
                "Remote environment url should include http or https"
            )
        return super().__post_init__()
