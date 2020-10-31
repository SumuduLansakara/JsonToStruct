from typing import Dict, Callable, List

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

    def parse(self, array_def: Dict, creator_fn: Callable, type_registry: TypeRegistry) -> List[TypeDefBase]:
        mem_reg_key = self.reg_key.add_leaf('0')
        item_def = array_def['items']
        type_defs = creator_fn(mem_reg_key, None, item_def, type_registry)

        assert len(type_defs) == 1
        self.element_type_def = type_defs[0]
        # if array item has a complex type, that has to be registered as a sibling to array
        if isinstance(self.element_type_def, (StructType, EnumType)):
            mem_name = item_def['$meta:typename'] if '$meta:typename' in item_def else self.type_name + '_sub'
            self.element_type_def.type_name = mem_name
            return type_defs

    def dict(self):
        return {
            **super().dict(),
            "kind": "array_alias",
            "element_type_def": self.element_type_def.dict(),
        }
