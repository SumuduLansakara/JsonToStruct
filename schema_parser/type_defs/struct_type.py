from __future__ import annotations

from typing import List, Union

from schema_parser.member_defs.array_mem_var import ArrayMemberVar
from schema_parser.member_defs.basic_mem_var import BasicMemberVar
from schema_parser.member_defs.inner_enum_member import InnerEnumMember
from schema_parser.member_defs.inner_struct_member import InnerStructMember
from schema_parser.member_defs.ref_mem_var import ReferencedMemberVar
from schema_parser.type_defs.type_def_base import TypeDefBase


class StructType(TypeDefBase):
    struct_name: str
    members: List[Union[BasicMemberVar, ArrayMemberVar, ReferencedMemberVar, InnerStructMember, InnerEnumMember]]

    def __init__(self, struct_name: str, properties: List[Union[BasicMemberVar, ArrayMemberVar, ReferencedMemberVar,
                                                                InnerStructMember, InnerEnumMember]]):
        self.struct_name = struct_name
        self.members = properties

    def dict(self):
        return {
            "kind": "struct",
            "name": self.struct_name,
            "members": [e.dict() for e in self.members]
        }
