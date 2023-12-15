"""
Base configuration backend interface
"""
from typing import (Any, Dict, List, Sequence, Union, get_args, get_origin,
                    get_type_hints)
from uuid import UUID

from cfgmgr.node import Node
from cfgmgr.parameters import Parameter, ParameterGroup


class _Backend:
    """
    Base class for configuration backend.
    """
    root: Node
    entries: Dict[str, Any]  # uuid to object mapping.  Flattens tree

    def get_parameter(self, meta_id: str) -> Parameter:
        raise NotImplementedError

    def get_configuration(self, meta_id: str) -> ParameterGroup:
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

    def validate(self, entry: Any) -> bool:
        """
        Fills UUID entries in ``entry`` and validates if ``entry``'s fields
        agree with the dataclass field types
        """
        # TODO: Actually finish and test this method
        for k, v in get_type_hints(type(entry)).items():
            field = getattr(entry, k)
            origin = get_origin(v)
            while origin:  # Drill down through nested types
                if origin is Union:
                    break
                elif origin in (List, Sequence):
                    v = get_args(v)[0]
                    origin = get_origin(v)
                elif origin in dict:
                    break  # currently not supported, what's the usecase?
                else:
                    break

            if Any in get_args(v):
                continue
            elif ((origin is Union) and (UUID in get_args(v)) and
                  not isinstance(self.entries[field], get_args(v))):
                # Replace and verify if the options are either UUID or other
                return False
