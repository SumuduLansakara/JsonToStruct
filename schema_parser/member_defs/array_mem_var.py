from typing import Union

from schema_parser.member_defs.member_def_base import MemberDefBase
from schema_parser.type_defs.ref_type import RefType


class ArrayMemberVar(MemberDefBase):
    member_var_name: str
    element_type: Union[str, RefType]

    def __init__(self, member_var_name: str, element_type: Union[str, RefType]):
        self.member_var_name = member_var_name
        self.element_type = element_type

    def dict(self):
        return {
            "kind": "array_member_variable",
            "type": self.element_type,
            "name": self.member_var_name,
        }
