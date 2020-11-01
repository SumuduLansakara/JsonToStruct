from typing import Dict, List

from schema_parser.reg_key import RegKey
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_defs.variant_alias import VariantAlias
from schema_parser.type_registry import TypeRegistry


def create_typedef(reg_key: RegKey, name: str, definition: Dict, type_registry: TypeRegistry) -> List[TypeDefBase]:
    types: [TypeDefBase] = [SimpleAlias, ArrayAlias, VariantAlias, EnumType, StructType, RefType]
    res: List[TypeDefBase] = []
    for Type in types:
        if Type.is_parsable(definition):
            t_def = Type(name, reg_key)
            dependent_types = t_def.parse(definition, create_typedef, type_registry)
            if dependent_types:
                res.extend(dependent_types)
            res.append(t_def)  # last element is the target type
            return res
    raise ValueError(f"Unsupported type: {reg_key} [{definition}]")
