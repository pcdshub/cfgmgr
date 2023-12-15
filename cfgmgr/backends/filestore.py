"""
Backend for configurations backed by files
"""

from cfgmgr.backends.core import _Backend
from cfgmgr.node import Node
from cfgmgr.parameters import Parameter, ParameterGroup

# write, copy/move mode
# serialize backends


class FilestoreBackend(_Backend):
    """
    Filestore configuration backend.
    """
    root: Node

    def __init__(self, path: str, initialize: bool = False) -> None:
        self.path = path

    def get_parameter(self, meta_id: str) -> Parameter:
        raise NotImplementedError

    def get_configuration(self, meta_id: str) -> ParameterGroup:
        raise NotImplementedError

    def refresh_cache(self) -> None:
        """refresh internal representations of data, store as root"""
        raise NotImplementedError

    def save(self) -> None:
        """Save entire config"""
        raise NotImplementedError

    def delete(self, meta_id: str) -> None:
        """Delete meta_id from the system (all instances)"""
        raise NotImplementedError

    def remove(self, node: Node) -> None:
        """
        Remove node from its position in the tree.
        Does not delete the held data, simply dereferences Node
        """
