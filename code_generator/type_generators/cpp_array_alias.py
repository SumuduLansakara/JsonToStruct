from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_type_base import CppTypeBase
from code_generator.type_generators.inner_type_parser import array_element_type
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_registry import TypeRegistry


class CppArrayAlias(CppTypeBase):
    type_def: ArrayAlias

    def write_header(self, buffer: LineBuffer, type_registry: TypeRegistry) -> None:
        buffer.append(f"using {self.type_def.type_name} = {self.actual_type(type_registry)};")

    def actual_type(self, type_registry: TypeRegistry) -> str:
        return array_element_type(self.type_def, type_registry)
