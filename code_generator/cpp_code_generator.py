import os
import pathlib
from typing import Union, Dict, List, Set

from code_generator.code_writers.header_code_writer import HeaderCodeWriter
from code_generator.line_buffer import LineBuffer, IndentedBlock
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


class TypeHeaderWriter:
    namespaces: Dict[str, List[str]]
    buffers: Dict[str, List[LineBuffer]]
    include_headers: Dict[str, List[str]]

    def __init__(self):
        self.namespaces = {}
        self.buffers = {}
        self.include_headers = {}

    @staticmethod
    def _make_ns_key(namespaces: List[str]) -> str:
        return '/'.join(namespaces)

    def add_to_namespace(self, namespaces: List[str], buffer: LineBuffer, headers: Set[str]):
        ns_key = self._make_ns_key(namespaces)
        if ns_key not in self.namespaces:
            self.namespaces[ns_key] = namespaces
            self.buffers[ns_key] = []
            self.include_headers[ns_key] = []
        self.buffers[ns_key].append(buffer)
        self.include_headers[ns_key].extend(headers)

    def get_type_header_buffer(self, namespaces: List[str]) -> LineBuffer:
        ns_key = self._make_ns_key(namespaces)
        if ns_key not in self.include_headers:
            raise NameError(f"No namespace type info: {ns_key}")

        buffer = LineBuffer(0)
        if self.include_headers[ns_key]:
            buffer.new_line()
            for include in self.include_headers[ns_key]:
                buffer.append(f"#include <{include}>")
        buffer.new_line()
        ns_str = "::".join(namespaces)
        buffer.append(f'namespace {ns_str}')
        buffer.append('{')
        with IndentedBlock(buffer):
            for buf in self.buffers[ns_key]:
                buffer.append_buffer(buf)
        buffer.append(f'}} // {ns_str}')

        return buffer

    def get_type_header_includes(self, namespaces: List[str]) -> List[str]:
        ns_key = self._make_ns_key(namespaces)
        if ns_key not in self.include_headers:
            raise NameError(f"No namespace type info: {ns_key}")
        return self.include_headers[ns_key]


class CodeGenerator:
    type_registry: TypeRegistry
    src_root_dir: str
    header_dir: str
    cpp_dir: str
    type_header_writer: TypeHeaderWriter

    def get_header_file_path(self, namespaces: List[str], file_name_prefix: str) -> pathlib.Path:
        return pathlib.Path(
            os.path.join(self.src_root_dir, self.header_dir, *namespaces, f"{file_name_prefix}.h"))

    def get_cpp_file_path(self, struct_def: StructType) -> pathlib.Path:
        return pathlib.Path(
            os.path.join(self.src_root_dir, self.cpp_dir, *struct_def.namespaces, struct_def.type_name + '.cpp'))

    def __init__(self, type_registry: TypeRegistry, src_root_dir: str, header_dir: str, cpp_dir: str):
        self.type_registry = type_registry
        self.src_root_dir = src_root_dir
        self.header_dir = header_dir
        self.cpp_dir = cpp_dir
        self.type_header_writer = TypeHeaderWriter()

    def _generate_header(self, cpp_type_meta, cpp_type, type_def: TypeDefBase):
        if cpp_type_meta == CppStruct:
            cpp_type.add_base_class('ISerializable')
            cpp_type.add_member_method('[[nodiscard]] std::string ToJson() const override;')
            cpp_type.add_member_method('void FromJson(const std::string&) override;')

        header_code = LineBuffer(0)

        try:
            cpp_type.write_header(header_code, self.type_registry)
        except Exception as ex:
            print(f"Failed writing header: {type_def.type_name} [{ex}]")
            raise

        # prepend include headers
        if cpp_type_meta in (CppStruct, CppExtendedVariant):
            header_writer = HeaderCodeWriter(header_code)
            header_writer.include_headers.extend(cpp_type.header_includes)

            header_path = self.get_header_file_path(type_def.namespaces, type_def.type_name)
            pathlib.Path(header_path.parent).mkdir(parents=True, exist_ok=True)
            with open(header_path, 'w') as header_file:
                header_file.write(header_writer.str())
        else:
            self.type_header_writer.add_to_namespace(cpp_type.type_def.namespaces, header_code,
                                                     cpp_type.header_includes)

    def _generate_cpp(self, cpp_type: Union[CppStruct, CppExtendedVariant]):
        cpp_src_code = LineBuffer(0)
        if isinstance(cpp_type, CppStruct):
            cpp_type.add_base_class('ISerializable')
            cpp_type.add_member_method('[[nodiscard]] std::string ToJson() const override;')
            cpp_type.add_member_method('void FromJson(const std::string&) override;')
        cpp_type.write_source(cpp_src_code, self.type_registry)

        # prepend include headers
        header_path = self.get_header_file_path(cpp_type.type_def.namespaces, cpp_type.type_def.type_name)
        prepend_lines = [f'#include <{header_path}>']
        for include in cpp_type.cpp_includes:
            prepend_lines.append(f"#include <{include}>")
        prepend_lines.append('')
        cpp_src_code.prepend(*prepend_lines)

        cpp_path = self.get_cpp_file_path(cpp_type.type_def)
        pathlib.Path(cpp_path.parent).mkdir(parents=True, exist_ok=True)
        with open(cpp_path, 'w') as header_file:
            header_file.write(cpp_src_code.str())

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
        build_order = [EnumType, SimpleAlias, StructType, RefType, ArrayAlias, VariantAlias, ExtendedVariant]
        for bo in build_order:
            for type_def in self.type_registry:
                if not isinstance(type_def, bo):
                    continue

                try:
                    cpp_type_meta = self.get_cpp_type(type_def)
                    cpp_type = cpp_type_meta(type_def)
                    self._generate_header(cpp_type_meta, cpp_type, type_def)
                    if isinstance(type_def, (StructType, ExtendedVariant)):
                        self._generate_cpp(cpp_type)
                except Exception as ex:
                    if 'AudioPatchConfigId' in str(ex):
                        continue
                    print(ex)

        # write shared type header
        for ns_key, namespaces in self.type_header_writer.namespaces.items():
            header_writer = HeaderCodeWriter(self.type_header_writer.get_type_header_buffer(namespaces))
            header_writer.include_headers.extend(self.type_header_writer.get_type_header_includes(namespaces))
            header_path = self.get_header_file_path(namespaces, f'Types{namespaces[-1].capitalize()}')
            pathlib.Path(header_path.parent).mkdir(parents=True, exist_ok=True)
            with open(header_path, 'w') as header_file:
                header_file.write(header_writer.str())
