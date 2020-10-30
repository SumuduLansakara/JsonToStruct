from schema_parser.member_defs.member_def_base import MemberDefBase


class BasicMemberVar(MemberDefBase):
    member_var_name: str
    member_var_type: str

    def __init__(self, member_var_name: str, mem_var_type: str):
        self.member_var_name = member_var_name
        self.member_var_type = mem_var_type

    def dict(self):
        return {
            "kind": "basic_member_variable",
            "type": self.member_var_type,
            "name": self.member_var_name,
        }
