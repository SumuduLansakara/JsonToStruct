from schema_parser.member_defs.member_def_base import MemberDefBase
from schema_parser.type_defs.ref_type import RefType


class ReferencedMemberVar(MemberDefBase):
    member_var_name: str
    ref_type_def: RefType

    def __init__(self, member_var_name: str, ref_type: RefType):
        self.member_var_name = member_var_name
        self.ref_type_def = ref_type

    def dict(self):
        return {
            "kind": "referenced_member_variable",
            "ref_type_def": self.ref_type_def.dict(),
            "name": self.member_var_name,
        }
