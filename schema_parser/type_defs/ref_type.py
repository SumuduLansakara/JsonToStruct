from typing import Dict, Callable, List

from schema_parser.reg_key import RegKey
from schema_parser.type_defs.type_def_base import TypeDefBase, TypeDefKind


class RefType(TypeDefBase):
    """Virtual type holding reference to a concrete type. Used for late reference resolution"""
    target_uri: str

    def __init__(self, namespaces: List[str], type_name: str, reg_key: RegKey):
        super().__init__(namespaces, type_name, reg_key, TypeDefKind.RefType)

    def parse(self, ref_def: Dict, creator_fn: Callable, _type_registry):
        self.target_uri = ref_def['$ref']

    def dict(self):
        return {
            **super().dict(),
            "kind": "ref_type",
            "target_uri": self.target_uri
        }
