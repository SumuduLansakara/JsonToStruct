from typing import List

from schema_parser.type_defs.type_def_base import TypeDefBase


class EnumType(TypeDefBase):
    """Enum definition"""
    enum_name: str
    members: List[str]

    def __init__(self, enum_name: str, enum_members: List[str]):
        self.enum_name = enum_name
        self.members = enum_members

    def dict(self):
        return {
            "kind": "enum",
            "name": self.enum_name,
            "members": self.members,
        }
