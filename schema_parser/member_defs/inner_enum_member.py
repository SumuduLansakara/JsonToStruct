from schema_parser.member_defs.member_def_base import MemberDefBase
from schema_parser.type_defs.enum_type import EnumType


class InnerEnumMember(MemberDefBase):
    member_var_name: str
    enum_def: EnumType

    def __init__(self, member_var_name: str, enum_def: EnumType):
        self.member_var_name = member_var_name
        self.enum_def = enum_def

    def dict(self):
        return {
            "kind": "enum_member",
            "variable_name": self.member_var_name,
            "def": self.enum_def.dict(),
        }
