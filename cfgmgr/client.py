"""Client for cfgmgr"""

from typing import Any, List

from cfgmgr.backends.core import _Backend
from cfgmgr.model import Node


class Client:
    backend: _Backend

    def __init__(self, database=None, **kwargs) -> None:
        # get backend
        return

    @classmethod
    def from_config(cls, cfg=None):
        raise NotImplementedError

    def search(self, **post) -> List[Any]:
        """Search by key-value pair."""
        raise NotImplementedError

    def delete_entry(self, entry: Any) -> None:
        """Remove item from backend, depending on backend"""
        # item.backend.delete(item)
        raise NotImplementedError

    def get_tree(self) -> Node:
        """Return root Node of databases"""
        raise NotImplementedError

    def compare(self, entry_l, entry_r):
        """Compare two entries.  Should be of same type"""
        raise NotImplementedError

    def apply(self, entry):
        """Apply settings found in ``entry``.  If no values found, no-op"""
        raise NotImplementedError

    def copy(self, source):
        """Recursively copy ``source``, make new name, clear any stored values"""
        raise NotImplementedError

    def snapshot(self, entry, in_place=True):
        """
        Capture PV Values devfined by ``entry``.  do not save to database
        Return a `entry` with values filled if ``inplace``
        """
        raise NotImplementedError

    def save(self, entry):
        """Save information in ``entry`` to database"""
        raise NotImplementedError
