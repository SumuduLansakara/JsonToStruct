from __future__ import annotations

import json
from typing import List, Union


class BasicAliasDef:
    alias_name: str
    actual_type: str

    def __init__(self, alias_name: str, actual_type: str):
        self.alias_name = alias_name
        self.actual_type = actual_type

    def dict(self):
        return {
            "kind": "type_alias",
            "alias": self.alias_name,
            "type": self.actual_type,
        }

    def __str__(self):
        return json.dumps(self.dict(), indent=4)


class ArrayAliasDef:
    alias_name: str
    element_type: str

    def __init__(self, alias_name: str, element_type: str):
        self.alias_name = alias_name
        self.element_type = element_type

    def dict(self):
        return {
            "kind": "array_alias",
            "name": self.alias_name,
            "element_type": self.element_type,
        }

    def __str__(self):
        return json.dumps(self.dict(), indent=4)


class EnumTypeDef:
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

    def __str__(self):
        return json.dumps(self.dict(), indent=4)


class MemberVarDef:
    member_var_name: str
    member_var_type: str

    def __init__(self, member_var_name: str, mem_var_type: str):
        self.member_var_name = member_var_name
        self.member_var_type = mem_var_type

    def dict(self):
        return {
            "kind": "member_variable",
            "type": self.member_var_type,
            "name": self.member_var_name,
        }

    def __str__(self):
        return json.dumps(self.dict(), indent=4)


class StructTypeDef:
    struct_name: str
    properties: List[Union[MemberVarDef, StructTypeDef, EnumTypeDef]]

    def __init__(self, struct_name: str, properties: List[MemberVarDef]):
        self.struct_name = struct_name
        self.properties = properties

    def dict(self):
        return {
            "kind": "struct",
            "name": self.struct_name,
            "properties": [e.dict() for e in self.properties]
        }

    def __str__(self):
        return json.dumps(self.dict(), indent=4)


class RefTypeDef:
    ref_target_uri: str

    def __init__(self, ref_target_uri: str):
        self.ref_target_uri = ref_target_uri

    def dict(self):
        return {
            "ref_target_uri": self.ref_target_uri
        }

    def __str__(self):
        return json.dumps(self.dict(), indent=4)
