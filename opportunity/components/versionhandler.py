from git.repo import Repo
from os import path

class VersionHandler:
    def __init__(self):
        self._repo = Repo(path.dirname(path.dirname(path.dirname(__file__))))
        self._remote = self._repo.remote("origin")
        self._commitcount = f"{self._remote.fetch()[0].commit.count():,}"

    @property
    def local_version(self) -> str:
        """ Returns current version info"""
        return self._repo.commit().hexsha[:7]

    @property
    def remote_version(self) -> str:
        """ Returns remote version info """
        return self._remote.fetch()[0].commit.hexsha[:7]

    @property
    def is_latest(self) -> bool:
        """
        Checks if the current version is the latest version.

        Returns
        --------
        :class:`bool`
            Whether current version is the latest
        """
        return self._repo.commit() == self._remote.fetch()[0].commit

    def update_version(self) -> None:
        """ Pulls the latest version from github. """
        self._remote.pull()
