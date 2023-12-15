"""
Data structures for data containing node types.  Type of node determined by
the type of data it holds:
- data: Node --> A folder
- data: ParameterGroup --> a ParameterGroup
etc.

Nodes are shown in the tree view of the UI
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union
from uuid import UUID

from .parameters import Parameter, ParameterGroup

CFG_DATA = Union[Parameter, ParameterGroup]


@dataclass
class Node:
    _id: UUID
    data: List[CFG_DATA]
    parent: Optional[UUID] = None
    children: Optional[List[UUID]] = None

    @classmethod
    def from_data(cls, data: CFG_DATA) -> Node:
        raise NotImplementedError()
