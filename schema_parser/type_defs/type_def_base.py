from __future__ import annotations

import json
from abc import ABC
from typing import Dict, Callable, List

from schema_parser.reg_key import RegKey


class TypeDefBase(ABC):
    """Base class for all type definition classes"""
    namespaces: List[str]
    type_name: str
    reg_key: RegKey

    def __init__(self, namespaces: List[str], type_name: str, reg_key: RegKey):
        self.namespaces = namespaces
        self.type_name = type_name
        self.reg_key = reg_key

    def parse(self, definition: Dict, creator_fn: Callable, type_registry) -> List[TypeDefBase]:
        raise NotImplementedError

    def dict(self):
        return {
            'type_name': self.type_name,
            'reg_key': str(self.reg_key)
        }

    def __str__(self):
        return json.dumps(self.dict(), indent=4)
