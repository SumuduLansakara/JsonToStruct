from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_type_base import CppTypeBase
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_registry import TypeRegistry


class CppSimpleAlias(CppTypeBase):
    type_def: SimpleAlias

    _cpp_type_map = {
        "boolean": "bool",
        "integer": "std::int32",
        "number": "float",
        "string": "std::string",
    }

    @classmethod
    def get_cpp_type(cls, type_str: str) -> str:
        if type_str not in cls._cpp_type_map:
            return type_str
        return cls._cpp_type_map[type_str]

    def type_name(self) -> str:
        return self.type_def.type_name

    def actual_type(self) -> str:
        return self.get_cpp_type(self.type_def.actual_type)

    def write_header(self, buffer: LineBuffer, _type_registry: TypeRegistry) -> None:
        buffer.append(f"using {self.type_def.type_name} = {self.actual_type()};")
