from typing import Dict, List

from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_array_alias import CppArrayAlias
from code_generator.type_generators.cpp_enum import CppEnum
from code_generator.type_generators.cpp_ref_alias import CppRefAlias
from code_generator.type_generators.cpp_simple_alias import CppSimpleAlias
from code_generator.type_generators.cpp_struct import CppStruct
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_registry import TypeRegistry


class CodeGenerator:
    _cpp_type_map: Dict[str, str]
    _type_registry: TypeRegistry

    def __init__(self, type_registry: TypeRegistry):
        self._type_registry = type_registry

    def generate(self):
        header_lines: List[List] = []

        cpp_typy_map = {
            SimpleAlias: CppSimpleAlias,
            ArrayAlias: CppArrayAlias,
            EnumType: CppEnum,
            StructType: CppStruct,
            RefType: CppRefAlias,
        }

        for type_def in self._type_registry:
            code = LineBuffer(0)
            cpp_type = cpp_typy_map[type(type_def)]
            cpp_type_writer = cpp_type(type_def)
            if cpp_type == CppStruct:
                cpp_type_writer.add_base_class('ISerializable')
                cpp_type_writer.add_member_method('[[nodiscard]] std::string ToJson() const override;')
                cpp_type_writer.add_member_method('void FromJson(const std::string&) override;')
            cpp_type_writer.write_header(code, self._type_registry)
            header_lines.append(code.str())

        for td in header_lines:
            print(td)
