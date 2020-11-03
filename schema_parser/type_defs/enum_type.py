from typing import Dict, Callable

from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry
from schema_parser.utils.attribute_reader import read_custom_attrib


class EnumType(TypeDefBase):
    """Enum definition"""
    members: Dict[str, int]
    comments: Dict[str, str]

    def parse(self, enum_def: Dict, creator_fn: Callable, type_registry: TypeRegistry):
        self.members = {e: i for i, e in enumerate(enum_def['enum'])}

        # use explicitly defined enum values
        enum_values = read_custom_attrib(enum_def, 'enum_values')
        if enum_values is not None:
            assert isinstance(enum_values, dict)
            last_val = 0
            for e in enum_def['enum']:
                if e in enum_values:
                    last_val = enum_values[e]
                self.members[e] = last_val
                last_val += 1

        self.comments = read_custom_attrib(enum_def, 'enum_comments', {})
        assert isinstance(self.comments, dict)
        assert all(c_key in self.members.keys() for c_key in self.comments.keys())

    def dict(self):
        return {
            **super().dict(),
            "kind": "enum",
            "members": self.members,
        }
