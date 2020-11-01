import os
from typing import Dict

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
    header_dir: str
    cpp_dir: str

    def get_header_file_path(self, struct_def: StructType) -> str:
        return os.path.join(self.header_dir, *struct_def.namespaces, struct_def.type_name + '.h')

    def get_cpp_file_path(self, struct_def: StructType) -> str:
        return os.path.join(self.cpp_dir, *struct_def.namespaces, struct_def.type_name + '.cpp')

    def __init__(self, type_registry: TypeRegistry, header_dir: str, cpp_dir: str):
        self._type_registry = type_registry
        self.header_dir = header_dir
        self.cpp_dir = cpp_dir

    def generate_headers(self):
        cpp_type_map = {
            SimpleAlias: CppSimpleAlias,
            ArrayAlias: CppArrayAlias,
            VariantAlias: CppVariantAlias,
            EnumType: CppEnum,
            StructType: CppStruct,
            RefType: CppRefAlias,
        }

        for type_def in self._type_registry:
            if type(type_def) not in cpp_type_map:
                raise TypeError(f"No supporting cpp type: {type_def}")

            cpp_type_meta = cpp_type_map[type(type_def)]
            cpp_type = cpp_type_meta(type_def)

            cpp_header_code = LineBuffer(0)
            if cpp_type_meta == CppStruct:
                cpp_type.add_base_class('ISerializable')
                cpp_type.add_member_method('[[nodiscard]] std::string ToJson() const override;')
                cpp_type.add_member_method('void FromJson(const std::string&) override;')

            try:
                cpp_type.write_header(cpp_header_code, self._type_registry)
            except Exception as ex:
                print(f"Failed writing header: {type_def.type_name} [{ex}]")

            # prepend include headers
            if cpp_type_meta == CppStruct:
                prepend_lines = ['#pragma once']
                if cpp_type.header_includes:
                    prepend_lines.append('')
                    for include in cpp_type.header_includes:
                        prepend_lines.append(f"#include <{include}>")
                prepend_lines.append('')
                cpp_header_code.prepend(*prepend_lines)

            print(':: header path: ' + self.get_header_file_path(type_def))
            print()
            print(cpp_header_code.str())

    def generate_sources(self):
        for type_def in self._type_registry:
            if not isinstance(type_def, StructType):
                continue

            cpp_src_code = LineBuffer(0)
            cpp_struct = CppStruct(type_def)
            cpp_struct.add_base_class('ISerializable')
            cpp_struct.add_member_method('[[nodiscard]] std::string ToJson() const override;')
            cpp_struct.add_member_method('void FromJson(const std::string&) override;')
            cpp_struct.write_source(cpp_src_code, self._type_registry)

            # prepend include headers
            prepend_lines = [f'#include <{self.get_header_file_path(type_def)}>']
            for include in cpp_struct.cpp_includes:
                prepend_lines.append(f"#include <{include}>")
            prepend_lines.append('')
            cpp_src_code.prepend(*prepend_lines)

            print(':: cpp path: ' + self.get_cpp_file_path(type_def))
            print()
            print(cpp_src_code.str())
