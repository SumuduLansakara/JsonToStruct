from typing import List

from code_generator.type_generators.cpp_simple_alias import CppSimpleAlias
from schema_parser.reg_key import RegKey
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_defs.variant_alias import VariantAlias
from schema_parser.type_registry import TypeRegistry


def array_element_type(element_def: TypeDefBase, type_registry: TypeRegistry) -> str:
    if isinstance(element_def, SimpleAlias):
        cpp_alias = CppSimpleAlias(element_def)
        return cpp_alias.actual_type()
    if isinstance(element_def, ArrayAlias):
        return f"std::vector<{array_element_type(element_def.element_type_def, type_registry)}>"
    if isinstance(element_def, VariantAlias):
        return variant_element_type(element_def, type_registry)
    if isinstance(element_def, StructType):
        return element_def.type_name
    if isinstance(element_def, EnumType):
        return element_def.type_name
    if isinstance(element_def, RefType):
        key = RegKey.from_uri(element_def.target_uri)
        deref_type = type_registry.get(key)
        return deref_type.type_name
    raise TypeError(f"Unsupported array element type: {element_def}")


def variant_element_type(element_def: VariantAlias, type_registry: TypeRegistry) -> str:
    mem_types: List[str] = []
    for mem_type_def in element_def.member_type_defs:
        if isinstance(mem_type_def, SimpleAlias):
            cpp_alias = CppSimpleAlias(mem_type_def)
            mem_types.append(cpp_alias.actual_type())
        elif isinstance(mem_type_def, ArrayAlias):
            mem_types.append(array_element_type(mem_type_def, type_registry))
        elif isinstance(mem_type_def, VariantAlias):
            mem_types.append(f"std::variant<{variant_element_type(mem_type_def, type_registry)}>")
        elif isinstance(mem_type_def, StructType):
            mem_types.append(mem_type_def.type_name)
        elif isinstance(mem_type_def, EnumType):
            mem_types.append(mem_type_def.type_name)
        elif isinstance(mem_type_def, RefType):
            key = RegKey.from_uri(mem_type_def.target_uri)
            deref_type = type_registry.get(key)
            mem_types.append(deref_type.type_name)
        else:
            raise TypeError(f"Unsupported variant element type: {mem_type_def}")
    return f"std::variant<{','.join(mem_types)}>"
