from typing import Dict, Callable

from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


class ArrayAlias(TypeDefBase):
    """Array type alias"""
    element_type_def: TypeDefBase

    @staticmethod
    def is_parsable(array_def: Dict[str, str]) -> bool:
        if 'type' in array_def and array_def['type'] == 'array':
            if 'items' not in array_def:
                raise ValueError(f"Array definition without items [{array_def}]")
            return True
        return False

    def parse(self, item_def: Dict, creator_fn: Callable, type_registry: TypeRegistry):
        mem_name = self.type_name + '_sub'
        mem_reg_key = self.reg_key.parent().add_leaf(mem_name)
        self.element_type_def = creator_fn(mem_reg_key, mem_name, item_def['items'], type_registry)

        # if array item has a complex type, that has to be registered as a sibling to array
        if isinstance(self.element_type_def, (StructType, EnumType)):
            type_registry.add(self.element_type_def)

    def dict(self):
        return {
            **super().dict(),
            "kind": "array_alias",
            "element_type_def": self.element_type_def.dict(),
        }
