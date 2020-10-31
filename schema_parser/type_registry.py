from __future__ import annotations

from typing import Dict

from schema_parser.reg_key import RegKey
from schema_parser.type_defs.type_def_base import TypeDefBase


class TypeRegistry:
    _type_registry: Dict[RegKey, TypeDefBase]
    _namespace_map: Dict[RegKey, str]
    _current_namespace: str

    def __init__(self):
        self._type_registry = {}
        self._namespace_map = {}
        self._current_namespace = ''

    def __iter__(self):
        return iter(self._type_registry.items())

    def add(self, type_def: TypeDefBase):
        self._type_registry[type_def.reg_key] = type_def
        self._namespace_map[type_def.reg_key] = self._current_namespace

    def get(self, key: RegKey) -> TypeDefBase:
        if key not in self._type_registry:
            raise KeyError(f"No such key: {key}")
        return self._type_registry[key]

    def set_namespace(self, namespace: str):
        self._current_namespace = namespace

    def get_namespace(self, key: RegKey):
        return self._namespace_map[key]
