from __future__ import annotations

import hashlib
from typing import Dict, List, Union

from type_defs import RefTypeDef, EnumTypeDef, BasicAliasDef, ArrayAliasDef, StructTypeDef


class RegKey:
    _path: List[str]

    def __init__(self, *path):
        self._path = list(path)

    def __str__(self):
        return '/'.join(self._path)

    def __hash__(self):
        return int(hashlib.md5(str(self).encode()).hexdigest()[:8], 16)

    def __eq__(self, other):
        return str(self) == str(other)

    def adjust_leaf(self, leaf: str) -> RegKey:
        new_path = self._path[:-1] + [leaf]
        return RegKey(*new_path)

    def add_leaf(self, leaf: str) -> RegKey:
        new_path = self._path + [leaf]
        return RegKey(*new_path)


class TypeRegistry:
    _type_registry: Dict[RegKey, Union[RefTypeDef, EnumTypeDef, BasicAliasDef, ArrayAliasDef, StructTypeDef]]
    _namespace_map: Dict[RegKey, str]
    _current_namespace: str

    def __init__(self):
        self._type_registry = {}
        self._namespace_map = {}
        self._current_namespace = ''

    def __iter__(self):
        return iter(self._type_registry.items())

    def add(self, key: RegKey, type_def: Union[RefTypeDef, EnumTypeDef, BasicAliasDef, ArrayAliasDef, StructTypeDef]):
        self._type_registry[key] = type_def
        self._namespace_map[key] = self._current_namespace

    def get(self, key: RegKey) -> Union[RefTypeDef, EnumTypeDef, BasicAliasDef, ArrayAliasDef, StructTypeDef]:
        if key not in self._type_registry:
            raise KeyError(f"No such key: {key}")
        return self._type_registry[key]

    def set_namespace(self, namespace: str):
        self._current_namespace = namespace

    def get_namespace(self, key: RegKey):
        return self._namespace_map[key]
