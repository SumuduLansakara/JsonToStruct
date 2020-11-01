from typing import List

from code_generator.line_buffer import LineBuffer
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


def write_from_json_body(buffer: LineBuffer, type_registry: TypeRegistry, members: List[TypeDefBase]):
    for member_def in members:
        member_from_json(buffer, type_registry, member_def)


def member_from_json(buffer: LineBuffer, type_registry: TypeRegistry, member: TypeDefBase):
    if isinstance(member, (EnumType, StructType)):
        return
    buffer.append(f'm.{member.type_name} = j.at("{member.type_name}").get<decltype(m.{member.type_name})>();')
