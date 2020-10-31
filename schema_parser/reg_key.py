from __future__ import annotations

import hashlib
from typing import List


class RegKey:
    _path: List[str]

    @classmethod
    def from_uri(cls, uri: str):
        return RegKey(*uri.split('/'))

    def __init__(self, *path):
        self._path = list(path)

    def __str__(self):
        return '/'.join(self._path)

    def __hash__(self):
        return int(hashlib.md5(str(self).encode()).hexdigest()[:8], 16)

    def __eq__(self, other):
        return str(self) == str(other)

    def parent(self) -> RegKey:
        return RegKey(*self._path[:-1])

    def add_leaf(self, leaf: str) -> RegKey:
        new_path = self._path + [leaf]
        return RegKey(*new_path)
