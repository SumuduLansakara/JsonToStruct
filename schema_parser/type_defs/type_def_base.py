from __future__ import annotations

import json
from abc import ABC
from enum import Enum
from typing import Dict, Callable, List

from schema_parser.reg_key import RegKey


class TypeDefKind(Enum):
    SimpleAlias = 0
    ArrayAlias = 1
    VariantAlias = 2
    EnumType = 3
    StructType = 4
    ExtendedVariantType = 5
    RefType = 6


class TypeDefBase(ABC):
    """Base class for all type definition classes"""
    namespaces: List[str]
    type_name: str
    reg_key: RegKey
    kind: TypeDefKind

    def __init__(self, namespaces: List[str], type_name: str, reg_key: RegKey, kind: TypeDefKind):
        self.namespaces = namespaces
        self.type_name = type_name
        self.reg_key = reg_key
        self.kind = kind

    def parse(self, definition: Dict, creator_fn: Callable, type_registry) -> List[TypeDefBase]:
        raise NotImplementedError

    def dict(self):
        return {
            'namespaces': '::'.join(self.namespaces),
            'type_name': self.type_name,
            'reg_key': str(self.reg_key),
            "kind": self.kind.name
        }

    def __str__(self):
        return json.dumps(self.dict(), indent=4)
