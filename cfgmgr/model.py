"""
Data structures for data model.
A Node is an entity in the tree.  Type of node determined by
the type of data it holds:
- data: Node --> A folder
- data: ParameterGroup --> a ParameterGroup
etc.

Nodes are shown in the tree view of the UI

Parameters are the smallest bit of information in a configuration,
corresponding to a single PV-value pair (plus other metadata)

ParameterGroups hold multiple individual parameters or nested ParameterGroups.

"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, List, Optional, Union
from uuid import UUID, uuid4

from apischema.metadata import skip

from cfgmgr.backends.core import _Backend


@dataclass
class Metadata:
    """Base class for items in the datamodel.  Holds common metadata"""
    meta_id: UUID = field(default_factory=uuid4)
    name: str = ''
    creation: datetime = field(default_factory=datetime.utcnow, compare=False)
    description: str = ''

    # Assigned when loaded from a backend
    backend: Optional[_Backend] = field(default=None,
                                        metadata=skip(serialization=True))


@dataclass
class Node(Metadata):
    data: List[Union[UUID, CFG_DATA]] = field(default_factory=list)
    parent: Optional[Union[UUID, Node]] = None
    children: List[Union[UUID, Node]] = field(default_factory=list)

    @classmethod
    def from_data(cls, data: CFG_DATA) -> Node:
        raise NotImplementedError()


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


@dataclass
class Parameter(Metadata):
    pv_name: str = ''
    value: Optional[Any] = None
    type: str = 'str'
    read_only: bool = False

    def apply(self) -> None:
        # Apply this parameter to control layer
        raise NotImplementedError

    def store(self) -> None:
        # store current values into this value
        raise NotImplementedError


@dataclass
class ParameterGroup(Metadata):
    parameters: list[Union[UUID, Parameter]] = field(default_factory=list)
    prefix: Optional[str] = None

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


CFG_DATA = Union[Parameter, ParameterGroup]
