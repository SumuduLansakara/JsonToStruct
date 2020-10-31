from typing import Dict, Callable

from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


class RefType(TypeDefBase):
    """Virtual type holding reference to a concrete type. Used for late reference resolution"""
    target_uri: str

    @staticmethod
    def is_parsable(ref_def: Dict) -> bool:
        return '$ref' in ref_def

    def parse(self, ref_def: Dict, creator_fn: Callable, type_registry: TypeRegistry):
        self.target_uri = ref_def['$ref']

    def dict(self):
        return {
            **super().dict(),
            "kind": "ref_type",
            "target_uri": self.target_uri
        }
