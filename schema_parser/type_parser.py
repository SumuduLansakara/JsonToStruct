from typing import Dict

from schema_parser.reg_key import RegKey
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


def create_typedef(reg_key: RegKey, name: str, definition: Dict, type_registry: TypeRegistry) -> TypeDefBase:
    types: [TypeDefBase] = [SimpleAlias, ArrayAlias, EnumType, StructType, RefType]
    for Type in types:
        if Type.is_parsable(definition):
            t_def = Type(name, reg_key)
            t_def.parse(definition, create_typedef, type_registry)
            return t_def
    raise ValueError(f"Unsupported type: {reg_key} [{definition}]")
