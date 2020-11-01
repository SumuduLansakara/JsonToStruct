from typing import Dict, List

from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_array_alias import CppArrayAlias
from code_generator.type_generators.cpp_enum import CppEnum
from code_generator.type_generators.cpp_ref_alias import CppRefAlias
from code_generator.type_generators.cpp_simple_alias import CppSimpleAlias
from code_generator.type_generators.cpp_struct import CppStruct
from code_generator.type_generators.cpp_variant_alias import CppVariantAlias
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.variant_alias import VariantAlias
from schema_parser.type_registry import TypeRegistry


class CodeGenerator:
    _cpp_type_map: Dict[str, str]
    _type_registry: TypeRegistry

    def __init__(self, type_registry: TypeRegistry):
        self._type_registry = type_registry

    def generate_headers(self):
        header_lines: List[List] = []

        cpp_type_map = {
            SimpleAlias: CppSimpleAlias,
            ArrayAlias: CppArrayAlias,
            VariantAlias: CppVariantAlias,
            EnumType: CppEnum,
            StructType: CppStruct,
            RefType: CppRefAlias,
        }

        for type_def in self._type_registry:
            code = LineBuffer(0)
            if type(type_def) not in cpp_type_map:
                raise TypeError(f"No supporting cpp type: {type_def}")
            cpp_type = cpp_type_map[type(type_def)]
            cpp_type_writer = cpp_type(type_def)
            if cpp_type == CppStruct:
                cpp_type_writer.add_base_class('ISerializable')
                cpp_type_writer.add_member_method('[[nodiscard]] std::string ToJson() const override;')
                cpp_type_writer.add_member_method('void FromJson(const std::string&) override;')

            try:
                cpp_type_writer.write_header(code, self._type_registry)
            except Exception as ex:
                print(f"Failed writing header: {type_def.type_name} [{ex}]")
            header_lines.append(code.str())

        for td in header_lines:
            print(td)

    def generate_sources(self):
        src_lines: List[List] = []
        for type_def in self._type_registry:
            if not isinstance(type_def, StructType):
                continue
            code = LineBuffer(0)
            cpp_type_writer = CppStruct(type_def)
            cpp_type_writer.add_base_class('ISerializable')
            cpp_type_writer.add_member_method('[[nodiscard]] std::string ToJson() const override;')
            cpp_type_writer.add_member_method('void FromJson(const std::string&) override;')
            cpp_type_writer.write_source(code, self._type_registry)
            src_lines.append(code.str())

        for td in src_lines:
            print(td)
