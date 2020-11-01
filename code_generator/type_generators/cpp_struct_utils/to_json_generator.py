from typing import List

from code_generator.line_buffer import LineBuffer, IndentedBlock
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


def write_to_json_body(buffer: LineBuffer, type_registry: TypeRegistry, members: List[TypeDefBase]):
    buffer.append('return {')
    with IndentedBlock(buffer):
        for member_def in members:
            member_to_json(buffer, type_registry, member_def)
    buffer.append('};')


def member_to_json(buffer: LineBuffer, type_registry: TypeRegistry, member: TypeDefBase):
    if isinstance(member, (EnumType, StructType)):
        return
    buffer.append(f'{{ "{member.type_name}", m.{member.type_name} }}')
