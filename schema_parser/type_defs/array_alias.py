from typing import Dict, Callable, List

from schema_parser.reg_key import RegKey
from schema_parser.type_defs.type_def_base import TypeDefBase, TypeDefKind
from schema_parser.type_registry import TypeRegistry
from schema_parser.utils.attribute_reader import read_custom_attrib


class ArrayAlias(TypeDefBase):
    """Array type alias"""
    element_type_def: TypeDefBase

    def __init__(self, namespaces: List[str], type_name: str, reg_key: RegKey):
        super().__init__(namespaces, type_name, reg_key, TypeDefKind.ArrayAlias)

    def parse(self, array_def: Dict, creator_fn: Callable, type_registry: TypeRegistry) -> List[TypeDefBase]:
        mem_reg_key = self.reg_key.add_leaf('0')
        item_def = array_def['items']
        type_defs = creator_fn(mem_reg_key, self.namespaces, None, item_def, type_registry)
        assert len(type_defs) == 1  # TODO: can return many dependent types (e.g. inner array, variant)

        self.element_type_def = type_defs[0]
        # if array item has a complex type, that has to be registered as a sibling to array

        if self.element_type_def.kind in (TypeDefKind.StructType, TypeDefKind.EnumType):
            mem_name = read_custom_attrib(item_def, 'typename', self.type_name + '_sub')
            self.element_type_def.type_name = mem_name
            return type_defs

    def dict(self):
        return {
            **super().dict(),
            "element_type_def": self.element_type_def.dict(),
        }
