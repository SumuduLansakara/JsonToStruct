import os
from typing import Union

from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_array_alias import CppArrayAlias
from code_generator.type_generators.cpp_enum import CppEnum
from code_generator.type_generators.cpp_extended_variant import CppExtendedVariant
from code_generator.type_generators.cpp_ref_alias import CppRefAlias
from code_generator.type_generators.cpp_simple_alias import CppSimpleAlias
from code_generator.type_generators.cpp_struct import CppStruct
from code_generator.type_generators.cpp_variant_alias import CppVariantAlias
from schema_parser.reg_key import RegKey
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.extended_variant import ExtendedVariant
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_defs.variant_alias import VariantAlias
from schema_parser.type_registry import TypeRegistry


class CodeGenerator:
    type_registry: TypeRegistry
    src_root_dir: str
    header_dir: str
    cpp_dir: str

    def get_header_file_path(self, struct_def: StructType) -> str:
        return os.path.join(self.header_dir, *struct_def.namespaces, struct_def.type_name + '.h')

    def get_cpp_file_path(self, struct_def: StructType) -> str:
        return os.path.join(self.cpp_dir, *struct_def.namespaces, struct_def.type_name + '.cpp')

    def __init__(self, type_registry: TypeRegistry, src_root_dir: str, header_dir: str, cpp_dir: str):
        self.type_registry = type_registry
        self.src_root_dir = src_root_dir
        self.header_dir = header_dir
        self.cpp_dir = cpp_dir

    def _generate_header(self, cpp_type_meta, cpp_type, type_def: TypeDefBase):
        cpp_header_code = LineBuffer(0)
        if cpp_type_meta == CppStruct:
            cpp_type.add_base_class('ISerializable')
            cpp_type.add_member_method('[[nodiscard]] std::string ToJson() const override;')
            cpp_type.add_member_method('void FromJson(const std::string&) override;')

        try:
            cpp_type.write_header(cpp_header_code, self.type_registry)
        except Exception as ex:
            print(f"Failed writing header: {type_def.type_name} [{ex}]")
            raise

        # prepend include headers

        if cpp_type_meta in (CppStruct, CppExtendedVariant):
            prepend_lines = ['#pragma once']
            if cpp_type.header_includes:
                prepend_lines.append('')
                for include in cpp_type.header_includes:
                    prepend_lines.append(f"#include <{include}>")
            prepend_lines.append('')
            cpp_header_code.prepend(*prepend_lines)

        # with open(os.path.join(self.src_root_dir, self.get_header_file_path(type_def)), 'w') as header_file:
        #     header_file.write(cpp_header_code.str())
        print(cpp_header_code.str())

    def _generate_cpp(self, cpp_type: Union[CppStruct, CppExtendedVariant]):
        cpp_src_code = LineBuffer(0)
        if isinstance(cpp_type, CppStruct):
            cpp_type.add_base_class('ISerializable')
            cpp_type.add_member_method('[[nodiscard]] std::string ToJson() const override;')
            cpp_type.add_member_method('void FromJson(const std::string&) override;')
        cpp_type.write_source(cpp_src_code, self.type_registry)

        # prepend include headers
        prepend_lines = [f'#include <{self.get_header_file_path(cpp_type.type_def)}>']
        for include in cpp_type.cpp_includes:
            prepend_lines.append(f"#include <{include}>")
        prepend_lines.append('')
        cpp_src_code.prepend(*prepend_lines)

        # with open(os.path.join(self.src_root_dir, self.get_cpp_file_path(type_def)), 'w') as cpp_file:
        #     cpp_file.write(cpp_src_code.str())
        print(cpp_src_code.str())

    @staticmethod
    def get_cpp_type(type_def: TypeDefBase):
        cpp_type_map = {
            SimpleAlias: CppSimpleAlias,
            ArrayAlias: CppArrayAlias,
            VariantAlias: CppVariantAlias,
            EnumType: CppEnum,
            StructType: CppStruct,
            ExtendedVariant: CppExtendedVariant,
            RefType: CppRefAlias,
        }
        if type(type_def) not in cpp_type_map:
            raise TypeError(f"No supporting cpp type: {type_def}")
        return cpp_type_map[type(type_def)]

    def generate_selected(self, uri: str):
        type_def = self.type_registry.get(RegKey.from_uri(uri))
        cpp_type_meta = self.get_cpp_type(type_def)
        cpp_type = cpp_type_meta(type_def)
        self._generate_header(cpp_type_meta, cpp_type, type_def)
        if isinstance(type_def, StructType):
            self._generate_cpp(cpp_type)

    def generate_code(self):
        for type_def in self.type_registry:
            try:
                cpp_type_meta = self.get_cpp_type(type_def)
                cpp_type = cpp_type_meta(type_def)
                self._generate_header(cpp_type_meta, cpp_type, type_def)
                if isinstance(type_def, (StructType, ExtendedVariant)):
                    self._generate_cpp(cpp_type)
            except Exception as ex:
                print(ex)
                raise
