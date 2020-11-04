from typing import Dict, Callable, List

from schema_parser.reg_key import RegKey
from schema_parser.type_defs.type_def_base import TypeDefBase, TypeDefKind
from schema_parser.type_registry import TypeRegistry
from schema_parser.utils.attribute_reader import read_custom_attrib


class SimpleAlias(TypeDefBase):
    """Simple type alias"""
    actual_type: str

    def __init__(self, namespaces: List[str], type_name: str, reg_key: RegKey):
        super().__init__(namespaces, type_name, reg_key, TypeDefKind.SimpleAlias)

    def parse(self, definition: Dict, creator_fn: Callable, type_registry: TypeRegistry):
        self.actual_type = read_custom_attrib(definition, 'cpp_type', definition['type'])

    def dict(self):
        return {
            **super().dict(),
            "actual_type": self.actual_type,
        }
