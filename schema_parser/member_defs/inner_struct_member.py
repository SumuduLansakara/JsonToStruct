from schema_parser.member_defs.member_def_base import MemberDefBase


class InnerStructMember(MemberDefBase):
    member_var_name: str
    struct_def: "StructType"

    def __init__(self, member_var_name: str, struct_def):
        self.member_var_name = member_var_name
        self.struct_def = struct_def

    def dict(self):
        return {
            "kind": "enum_member",
            "variable_name": self.member_var_name,
            "def": self.struct_def.dict(),
        }
