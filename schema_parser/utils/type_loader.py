from typing import Dict, Type

from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_defs.variant_alias import VariantAlias


def get_object_type(schema_def: Dict) -> Type[TypeDefBase]:
    if 'enum' in schema_def:
        return EnumType

    if '$ref' in schema_def:
        return RefType

    if 'oneOf' in schema_def:
        if not isinstance(schema_def['oneOf'], list):
            raise ValueError(f"Variant definition is not an array: [{schema_def}]")
        return VariantAlias

    if 'type' not in schema_def:
        raise TypeError(f"Object definition without type [{schema_def}]")

    type_str = schema_def['type']

    if type_str in ['boolean', 'integer', 'number', 'string']:
        return SimpleAlias

    if type_str == 'array':
        if 'items' not in schema_def:
            raise ValueError(f"Array definition without items [{schema_def}]")
        return ArrayAlias

    if type_str == 'object':
        if 'properties' not in schema_def:
            raise ValueError(f"Struct definition without properties [{schema_def}]")
        return StructType

    raise TypeError(f"Unsupported type: [{schema_def}]")
