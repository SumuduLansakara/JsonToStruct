from typing import List

from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_type_base import CppTypeBase
from schema_parser.reg_key import RegKey
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_defs.variant_alias import VariantAlias
from schema_parser.type_registry import TypeRegistry


class CppVariantAlias(CppTypeBase):
    type_def: VariantAlias

    def _element_type(self, element_def: TypeDefBase, type_registry: TypeRegistry) -> str:
        if isinstance(element_def, SimpleAlias):
            return element_def.actual_type
        if isinstance(element_def, ArrayAlias):
            return f"std::vector<{self._element_type(element_def.element_type_def, type_registry)}>"
        if isinstance(element_def, StructType):
            return element_def.type_name
        if isinstance(element_def, EnumType):
            return element_def.type_name
        if isinstance(element_def, RefType):
            key = RegKey.from_uri(element_def.target_uri)
            deref_type = type_registry.get(key)
            return deref_type.type_name
        raise TypeError(f"Unsupported array element type: {element_def}")

    def _var_element_type(self, element_def: VariantAlias, type_registry: TypeRegistry) -> str:
        mem_types: List[str] = []
        for mem_type_def in element_def.member_type_defs:
            if isinstance(mem_type_def, SimpleAlias):
                mem_types.append(mem_type_def.actual_type)
            elif isinstance(mem_type_def, ArrayAlias):
                mem_types.append(f"std::vector<{self._element_type(mem_type_def, type_registry)}>")
            elif isinstance(mem_type_def, VariantAlias):
                mem_types.append(f"std::variant<{self._var_element_type(mem_type_def, type_registry)}>")
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

    def write_header(self, buffer: LineBuffer, type_registry: TypeRegistry) -> None:
        buffer.append(f"using {self.type_def.type_name} = {self.actual_type(type_registry)};")

    def actual_type(self, type_registry: TypeRegistry):
        return self._var_element_type(self.type_def, type_registry)
