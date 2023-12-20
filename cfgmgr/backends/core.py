"""
Base configuration backend interface
"""
from typing import (Any, List, Sequence, Union, get_args, get_origin,
                    get_type_hints)
from uuid import UUID


class _Backend:
    """
    Base class for configuration backend.
    """
    root: Any  # Root Node

    def get_parameter(self, meta_id: str, fill: bool = False) -> Any:
        # Can't type hint due circular import, but later backends can
        raise NotImplementedError

    def get_configuration(self, meta_id: str, fill: bool = False) -> Any:
        raise NotImplementedError

    def _attach_source_md(self, entry: Any) -> Any:
        """
        Attach source / backend information so multi-backend works with read-write
        attaches fill method for replaceing uuids with dataclasses
        attaches save method for applying singular change
        """
        raise NotImplementedError

    def save(self) -> None:
        """Save entire config"""
        raise NotImplementedError

    def delete(self, meta_id: str) -> None:
        """Delete meta_id from the system (all instances)"""
        raise NotImplementedError

    def remove(self, node: Any) -> None:
        """
        Remove node from its position in the tree.
        Does not delete the held data, simply dereferences Node
        """
        raise NotImplementedError

    def validate(self, entry: Any) -> bool:
        """
        Fills UUID entries in ``entry`` and validates if ``entry``'s fields
        agree with the dataclass field types.  Uses uuid_matches_type helper.
        """
        # TODO: Actually finish and test this method
        for k, v in get_type_hints(type(entry)).items():
            field = getattr(entry, k)
            origin = get_origin(v)
            while origin:  # Drill down through nested types
                if origin is Union:
                    break
                elif origin in (List, Sequence):
                    v = get_args(v)[0]  # Lists only have one type
                    origin = get_origin(v)
                    # Mark list and check each entry in list?
                elif origin in dict:
                    break  # currently not supported, what's the usecase?
                else:
                    break

            if Any in get_args(v):
                continue
            elif ((origin is Union) and (UUID in get_args(v)) and
                  not isinstance(self.entries[field], get_args(v))):
                # Replace and verify if the options are either UUID or other
                # call self.uuid_matches_type
                return False

    def uuid_matches_type(self, meta_id: UUID, data_type: Any) -> bool:
        """
        Tries to verify that the entry corresponding to ``meta_id`` points to an
        instance of ``data_type``
        """
        # (dependant on backend)
        raise NotImplementedError
