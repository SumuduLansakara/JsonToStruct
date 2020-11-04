from code_generator.line_buffer import LineBuffer, IndentedBlock
from code_generator.type_generators.cpp_type_base import CppTypeBase
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_registry import TypeRegistry


class CppEnum(CppTypeBase):
    type_def: EnumType

    def enum_name(self) -> str:
        return self.type_def.type_name

    def write_header(self, buffer: LineBuffer, _type_registry: TypeRegistry) -> None:
        buffer.append(f"enum class {self.enum_name()} : {self.type_def.underlying_type}")
        buffer.append('{')
        with IndentedBlock(buffer):
            if self.type_def.members:
                enum_members = self.type_def.members
                for m, i in enum_members.items():
                    comment = f"  //{self.type_def.comments[m]}" if m in self.type_def.comments else ''
                    buffer.append(f"{m} = {i},{comment}")
        buffer.append('};')
