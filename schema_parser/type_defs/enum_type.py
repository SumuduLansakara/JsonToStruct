from typing import Dict, Callable, List

from schema_parser.reg_key import RegKey
from schema_parser.type_defs.type_def_base import TypeDefBase, TypeDefKind
from schema_parser.type_registry import TypeRegistry
from schema_parser.utils.attribute_reader import read_custom_attrib


class EnumType(TypeDefBase):
    """Enum definition"""
    members: Dict[str, int]
    comments: Dict[str, str]
    underlying_type: str

    def __init__(self, namespaces: List[str], type_name: str, reg_key: RegKey):
        super().__init__(namespaces, type_name, reg_key, TypeDefKind.EnumType)

    def parse(self, enum_def: Dict, creator_fn: Callable, type_registry: TypeRegistry):
        self.members = {e: i for i, e in enumerate(enum_def['enum'])}

        self.underlying_type = read_custom_attrib(enum_def, 'enum_underlying_type', 'int32_t')

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
            "members": self.members,
        }
