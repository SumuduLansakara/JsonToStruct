from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_type_base import CppTypeBase
from schema_parser.reg_key import RegKey
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


def element_type(element_def: TypeDefBase, type_registry: TypeRegistry):
    if isinstance(element_def, SimpleAlias):
        return element_def.actual_type
    if isinstance(element_def, ArrayAlias):
        return f"std::vector<{element_type(element_def.element_type_def, type_registry)}>"
    if isinstance(element_def, StructType):
        return element_def.type_name
    if isinstance(element_def, EnumType):
        return element_def.type_name
    if isinstance(element_def, RefType):
        key = RegKey.from_uri(element_def.target_uri)
        deref_type = type_registry.get(key)
        return deref_type.type_name
    raise TypeError(f"Unsupported array element type: {element_def}")


class CppArrayAlias(CppTypeBase):
    type_def: ArrayAlias

    def write_header(self, buffer: LineBuffer, type_registry: TypeRegistry) -> None:
        buffer.append(f"using {self.type_def.type_name} = {self.actual_type(type_registry)};")

    def write_source(self, buffer: LineBuffer, type_registry: TypeRegistry) -> None:
        pass

    def actual_type(self, type_registry: TypeRegistry):
        return element_type(self.type_def, type_registry)