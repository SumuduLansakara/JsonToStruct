from typing import List, Dict, Callable

from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


class EnumType(TypeDefBase):
    """Enum definition"""
    members: List[str]

    @staticmethod
    def is_parsable(enum_def: Dict) -> bool:
        return 'enum' in enum_def

    def parse(self, enum_def: Dict, creator_fn: Callable, type_registry: TypeRegistry):
        self.members = [e for e in enum_def['enum']]

    def dict(self):
        return {
            **super().dict(),
            "kind": "enum",
            "members": self.members,
        }
