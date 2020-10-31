from code_generator.cpp_type_mapper import get_cpp_type
from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_type_base import CppTypeBase
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_registry import TypeRegistry


class CppSimpleAlias(CppTypeBase):
    type_def: SimpleAlias

    def type_name(self) -> str:
        return self.type_def.type_name

    def actual_type(self) -> str:
        return get_cpp_type(self.type_def.actual_type)

    def write_header(self, buffer: LineBuffer, _type_registry: TypeRegistry) -> None:
        buffer.append(f"using {self.type_def.type_name} = {self.actual_type()};")
