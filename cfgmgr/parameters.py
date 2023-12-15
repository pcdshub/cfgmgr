"""
Serializable Dataclasses for parameters and groups thereof.

Parameters are the smallest bit of information in a configuration,
corresponding to a single PV-value pair (plus other metadata)

ParameterGroups hold multiple individual parameters or nested ParameterGroups.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Union
from uuid import UUID

# TODO:
# - how to let parameter groups set information in their children?
#   prefixes?
#   - store parent pointers?
#   - >> Or just "initialize" and fill the prefixes one level down
#   - how to deserialize from json or whatever?
# - define arbitrary groups via user templates
# - mutexes (dependent fields)?
#   - simple string looking for _ids?
#   - >> apply method of parametergroup?


# class SetMode(Enum):
#     clear_then_write: 0
#     always_write: 1


@dataclass
class Parameter:
    _id: UUID
    pv_name: str
    timestamp: datetime = field(default_factory=datetime.utcnow, compare=False)
    value: Optional[Any] = None
    type: str = 'str'
    read_only: bool = False

    description: str = ''

    def apply(self) -> None:
        # Apply this parameter to control layer
        raise NotImplementedError

    def store(self) -> None:
        # store current values into this value
        raise NotImplementedError


@dataclass
class ParameterGroup:
    _id: UUID
    parameters: list[Union[UUID, Parameter]] = field(default_factory=list)

    timestamp: datetime = field(default_factory=datetime.utcnow, compare=False)
    prefix: Optional[str] = None
    description: str = ''
    # # if the parameters listed are mutually exclusive, as in if one
    # # is set, the others will not.
    # mutually_exclusive: bool = False

    def initialize(self) -> None:
        # fill the contained parameters with the prefix in this group
        raise NotImplementedError

    def apply(self) -> None:
        # apply each parameter, observing mutual exclusion and order
        # apply each group afterwards
        raise NotImplementedError

    def store(self) -> None:
        # store current values into this configuration
        raise NotImplementedError
