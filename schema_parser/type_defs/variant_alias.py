from typing import Dict, Callable, List

from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


class VariantAlias(TypeDefBase):
    """Variant type alias"""
    member_type_defs: List[TypeDefBase]

    @staticmethod
    def is_parsable(variant_def: Dict[str, str]) -> bool:
        if 'oneOf' in variant_def:
            if not isinstance(variant_def['oneOf'], list):
                raise ValueError(f"Variant definition is not an array: [{variant_def}]")
            return True
        return False

    def parse(self, variant_def: Dict, creator_fn: Callable, type_registry: TypeRegistry) -> List[TypeDefBase]:
        self.member_type_defs = []
        dep_types: List[TypeDefBase] = []

        for i, mem_t_def in enumerate(variant_def['oneOf']):
            mem_reg_key = self.reg_key.add_leaf(str(i))
            type_defs = creator_fn(mem_reg_key, None, mem_t_def, type_registry)
            assert len(type_defs) == 1  # TODO: can return many dependent types (e.g. inner array, variant)

            self.member_type_defs.append(type_defs[0])

            # if member has a complex type, that has to be registered as a sibling to array
            if isinstance(type_defs[0], (StructType, EnumType)):
                mem_name = mem_t_def['$meta:typename'] if '$meta:typename' in mem_t_def else self.type_name + '_sub'
                type_defs[0].type_name = mem_name
                dep_types.append(type_defs[0])

        return dep_types

    def dict(self):
        return {
            **super().dict(),
            "kind": "variant_alias",
            "member_type_defs": [mem_t_def.dict() for mem_t_def in self.member_type_defs],
        }
