from code_generator.line_buffer import LineBuffer, IndentedBlock
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.extended_variant import ExtendedVariant
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


class ToJsonWriter:
    buffer: LineBuffer
    type_registry: TypeRegistry
    container_struct: StructType

    def __init__(self, buffer: LineBuffer, type_registry: TypeRegistry, container_struct: StructType):
        self.buffer = buffer
        self.type_registry = type_registry
        self.container_struct = container_struct

    def write_function(self):
        self.buffer.append(f"nlohmann::json ToJson({self.container_struct.type_name} const& m)")
        self.buffer.append("{")
        with IndentedBlock(self.buffer):
            self._write_body()
        self.buffer.append("}")
        self.buffer.new_line()

    def _write_body(self):
        self.buffer.append('nlohmann::json res {')
        with IndentedBlock(self.buffer):
            for member_def in self.container_struct.members:
                self.member_to_json(member_def)
        self.buffer.append('};')
        self.buffer.append('return res;')

    def member_to_json(self, member: TypeDefBase):
        if isinstance(member, (EnumType, StructType, ExtendedVariant)):
            return
        self.buffer.append(f'{{ "{member.type_name}", m.{member.type_name} }}')
