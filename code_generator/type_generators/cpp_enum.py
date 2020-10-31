from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_type_base import CppTypeBase
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_registry import TypeRegistry


class CppEnum(CppTypeBase):
    type_def: EnumType

    def enum_name(self) -> str:
        return self.type_def.type_name

    def write_header(self, buffer: LineBuffer, _type_registry: TypeRegistry) -> None:
        buffer.append(f"enum class {self.enum_name()}")
        buffer.append('{')
        buffer.indent_up()
        if self.type_def.members:
            enum_members = self.type_def.members
            for i, m in enumerate(enum_members[:-1]):
                buffer.append(f"{m} = {i},")
            buffer.append(f"{enum_members[-1]} = {len(enum_members) - 1}")
        buffer.indent_down()
        buffer.append('}')

    def write_source(self, buffer: LineBuffer, _type_registry: TypeRegistry) -> None:
        pass
