from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_type_base import CppTypeBase
from schema_parser.reg_key import RegKey
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_registry import TypeRegistry


class CppRefAlias(CppTypeBase):
    type_def: RefType

    def target_type(self, type_registry: TypeRegistry) -> str:
        ref_key = RegKey.from_uri(self.type_def.target_uri)
        ref_type = type_registry.get(ref_key)
        return ref_type.type_name

    def write_header(self, buffer: LineBuffer, type_registry: TypeRegistry) -> None:
        buffer.append(f"using {self.type_def.type_name} = {self.target_type(type_registry)};")

    def write_source(self, buffer: LineBuffer, _type_registry: TypeRegistry) -> None:
        pass
