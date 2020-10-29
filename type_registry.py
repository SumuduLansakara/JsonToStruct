from __future__ import annotations
from typing import Dict, List, Union

from type_defs import RefTypeDef, EnumTypeDef, BasicAliasDef, ArrayAliasDef, StructTypeDef


class RegKey:
    _path: List[str]

    def __init__(self, *path):
        self._path = list(path)

    def __str__(self):
        return '/'.join(self._path)

    def adjust_leaf(self, leaf: str) -> RegKey:
        new_path = self._path[:-1] + [leaf]
        return RegKey(*new_path)

    def add_leaf(self, leaf: str) -> RegKey:
        new_path = self._path + [leaf]
        return RegKey(*new_path)


class TypeRegistry:
    _registry: Dict[str, Union[RefTypeDef, EnumTypeDef, BasicAliasDef, ArrayAliasDef, StructTypeDef]]

    def __init__(self):
        self._registry = {}

    def __iter__(self):
        return iter(self._registry.items())

    def add(self, key: RegKey, type_def: Union[RefTypeDef, EnumTypeDef, BasicAliasDef, ArrayAliasDef, StructTypeDef]):
        self._registry[str(key)] = type_def

    def get(self, key: RegKey) -> Union[RefTypeDef, EnumTypeDef, BasicAliasDef, ArrayAliasDef, StructTypeDef]:
        return self._registry[str(key)]
