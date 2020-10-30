from typing import Union

from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_defs.ref_type import RefType


class ArrayAlias(TypeDefBase):
    """Array type alias"""
    alias_name: str
    element_type: Union[str, RefType]

    def __init__(self, alias_name: str, element_type: Union[str, RefType]):
        self.alias_name = alias_name
        self.element_type = element_type

    def dict(self):
        return {
            "kind": "array_alias",
            "name": self.alias_name,
            "element_type": self.element_type,
        }
