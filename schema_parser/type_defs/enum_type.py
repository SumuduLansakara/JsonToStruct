from typing import Dict, Callable

from schema_parser import configs
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


class EnumType(TypeDefBase):
    """Enum definition"""
    members: Dict[str, int]

    def parse(self, enum_def: Dict, creator_fn: Callable, type_registry: TypeRegistry):
        self.members = {e: i for i, e in enumerate(enum_def['enum'])}

        # handle if enum values are explicitly defined
        if configs.CUSTOM_ATTR_PREFIX + 'enum_values' in enum_def:
            explicit_enum_vals = enum_def[configs.CUSTOM_ATTR_PREFIX + 'enum_values']
            last_val = 0
            for e in enum_def['enum']:
                if e in explicit_enum_vals:
                    last_val = explicit_enum_vals[e]
                self.members[e] = last_val
                last_val += 1

    def dict(self):
        return {
            **super().dict(),
            "kind": "enum",
            "members": self.members,
        }
