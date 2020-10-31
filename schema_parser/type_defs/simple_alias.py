from typing import Dict, Callable

from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


class SimpleAlias(TypeDefBase):
    """Simple type alias"""
    actual_type: str

    @staticmethod
    def is_parsable(alias_def: Dict[str, str]) -> bool:
        return 'type' in alias_def and alias_def['type'] in ['boolean', 'integer', 'number', 'string']

    def parse(self, definition: Dict, creator_fn: Callable, type_registry: TypeRegistry):
        self.actual_type = definition['type']

    def dict(self):
        return {
            **super().dict(),
            "kind": "type_alias",
            "actual_type": self.actual_type,
        }
