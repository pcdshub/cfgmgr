"""
Backend for configurations backed by files
"""

import contextlib
import json
import logging
import os
import shutil
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from apischema import ValidationError, deserialize

from cfgmgr.backends.core import _Backend
from cfgmgr.model import Node, Parameter, ParameterGroup
from cfgmgr.utils import build_abs_path

# write, copy/move mode
# serialize backends

logger = logging.getLogger(__name__)

UUID_ATTR_MAP = {
    Parameter: [],
    ParameterGroup: ['parameters'],
    Node: ['data', 'parent', 'children']
}


class FilestoreBackend(_Backend):
    """
    Filestore configuration backend.
    Unique aspects:
    entry cache, filled with _load_or_initialize type method
    save method saves all dataclasses

    default method here is to store everything as a flattened dictionary
    """
    _entry_cache: Dict[UUID, Any] = {}
    root: Optional[Node] = None

    def __init__(
        self,
        path: str,
        initialize: bool = False,
        cfg_path: Optional[str] = None
    ) -> None:
        self.path = path
        if cfg_path is not None:
            cfg_dir = os.path.dirname(cfg_path)
            self.path = build_abs_path(cfg_dir, path)
        else:
            self.path = path

        if initialize:
            self.initialize()

    def clear_cache(self) -> None:
        """Clear the loaded cache and stored root node"""
        self._entry_cache = {}
        self.root = None

    def _load_or_initialize(self) -> Optional[dict[str, Any]]:
        """Load an existing database or initialize a new one."""
        if self.root is None:
            try:
                self.root = self.load()
            except FileNotFoundError:
                logger.debug("Initializing new database")
                self.initialize()
                self.root = self.load()
            finally:
                # flatten create entry cache
                self.flatten_and_cache(self.root)

        return self._entry_cache

    def flatten_and_cache(self, entry: Any):
        """
        Flatten ``node`` recursively, adding them to ``self._entry_cache``.
        Does not replace any dataclass with its uuid
        Currently hard codes structure of Parameters, could maybe refactor later
        """
        attrs = UUID_ATTR_MAP.get(type(entry), [])
        for attr in attrs:
            field = getattr(entry, attr)

            # dicts may need to be supported eventually, but not today
            if isinstance(field, list):
                for item in field:
                    self.maybe_add_to_cache(item)
                    self.flatten_and_cache(item)
            elif field is None:
                continue
            else:
                self.maybe_add_to_cache(field)
                self.flatten_and_cache(field)

    def maybe_add_to_cache(self, item: Any) -> None:
        if isinstance(item, UUID) or item is None:
            return
        meta_id = item.meta_id
        if meta_id in self._entry_cache:
            # duplicate uuids found
            return

        self._entry_cache[meta_id] = item

    def swap_dclass_for_uuids(self) -> None:
        for entry in self._entry_cache.values():
            for attr in UUID_ATTR_MAP.get(type(entry), []):
                field = getattr(entry, attr)
                if isinstance(field, list):
                    new_list = [getattr(item, 'meta_id', item) for item in field]
                    setattr(entry, attr, new_list)
                elif field is None:
                    continue
                else:
                    setattr(entry, attr, field.meta_id)

    def initialize(self):
        """
        Initialize a new JSON file database.

        Raises
        ------
        PermissionError
            If the JSON file specified by ``path`` already exists.

        Notes
        -----
        This exists because the `.store` and `.load` methods assume that the
        given path already points to a readable JSON file. In order to begin
        filling a new database, an empty but valid JSON file is created.
        """

        # Do not overwrite existing databases
        if os.path.exists(self.path) and os.stat(self.path).st_size > 0:
            raise PermissionError("File {} already exists. Can not initialize "
                                  "a new database.".format(self.path))
        # Dump an empty dictionary
        self.store({})

    def serialize_db(self, mode: str) -> Dict[str, Any]:
        """
        Serialize the cached database.  Can output with either:
        1: every entity in a flat dictionary (references replaced with meta_id)
        2: straight serialization of tree structure
        """
        if mode == 'flat':
            return {}
        elif mode == 'tree':
            return {}

    def store(self, db: Dict) -> None:
        """
        Stash the database in the JSON file.

        This is a two-step process:

        1. Write the database out to a temporary file
        2. Move the temporary file over the previous database.

        Step 2 is an atomic operation, ensuring that the database
        does not get corrupted by an interrupted json.dump.

        Parameters
        ----------
        db : dict
            Dictionary to store in JSON.
        """
        temp_path = self._temp_path()
        try:
            with open(temp_path, 'w') as fd:
                json.dump(db, fd, sort_keys=True, indent=4)

            if os.path.exists(self.path):
                shutil.copymode(self.path, temp_path)
            shutil.move(temp_path, self.path)
        except BaseException as ex:
            logger.debug('JSON db move failed: %s', ex, exc_info=ex)
            # remove temporary file
            if os.path.exists(temp_path):
                os.remove(temp_path)
            raise

    def _temp_path(self) -> str:
        """
        Return a temporary path to write the json file to during "store".

        Includes a hash for uniqueness
        (in the cases where multiple temp files are written at once).
        """
        directory = os.path.dirname(self.path)
        filename = (
            f"_{str(uuid4())[:8]}"
            f"_{os.path.basename(self.path)}"
        )
        return os.path.join(directory, filename)

    def load(self) -> Optional[Node]:
        """
        Load database from stored path as a nested structure (deserialize as Node)
        Flattens into entry_dict
        """
        with open(self.path) as fp:
            serialized = json.load(fp)

        try:
            return deserialize(Node, serialized)
        except ValidationError:
            logger.info('Could not deserialize database, loading empty database')
            return Node()

    def get_parameter(self, meta_id: str, fill: bool = False) -> Parameter:
        return self._entry_cache[meta_id]

    def get_configuration(self, meta_id: str, fill: bool = False) -> ParameterGroup:
        return self._entry_cache[meta_id]

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
        raise NotImplementedError


@contextlib.contextmanager
def _load_and_store_context(backend: FilestoreBackend):
    """Context manager used to load, and optionally store the JSON database."""
    db = backend._load_or_initialize()
    yield db
    backend.store(db)
