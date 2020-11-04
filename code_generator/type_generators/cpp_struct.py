from typing import Set

from code_generator.line_buffer import LineBuffer, IndentedBlock
from code_generator.type_generators.cpp_array_alias import CppArrayAlias
from code_generator.type_generators.cpp_enum import CppEnum
from code_generator.type_generators.cpp_extended_variant import CppExtendedVariant
from code_generator.type_generators.cpp_ref_alias import CppRefAlias
from code_generator.type_generators.cpp_simple_alias import CppSimpleAlias
from code_generator.type_generators.cpp_struct_utils.from_json_generator import FromJsonWriter
from code_generator.type_generators.cpp_struct_utils.to_json_generator import ToJsonWriter
from code_generator.type_generators.cpp_type_base import CppTypeBase
from code_generator.type_generators.cpp_variant_alias import CppVariantAlias
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.extended_variant import ExtendedVariant
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.variant_alias import VariantAlias
from schema_parser.type_registry import TypeRegistry


class CppStruct(CppTypeBase):
    type_def: StructType
    base_classes: Set[str]
    member_methods: Set[str]
    header_includes: Set[str]
    cpp_includes: Set[str]

    def __init__(self, type_def: StructType):
        super().__init__(type_def)
        self.type_def = type_def
        self.base_classes = set()
        self.member_methods = set()
        self.header_includes = set()
        self.cpp_includes = {'nlohmann/json.hpp'}

    def add_base_class(self, class_name):
        self.base_classes.add(class_name)

    def add_member_method(self, method_declaration):
        self.member_methods.add(method_declaration)

    def write_header(self, buffer: LineBuffer, type_registry: TypeRegistry) -> None:
        var_buffer = LineBuffer(0)
        type_buffer = LineBuffer(0)
        for type_def in self.type_def.members:
            if isinstance(type_def, SimpleAlias):
                cpp_alias = CppSimpleAlias(type_def)
                var_buffer.append(f"{cpp_alias.actual_type()} {type_def.type_name};")
                self.header_includes.update(cpp_alias.get_include_headers(type_registry))
            elif isinstance(type_def, ArrayAlias):
                cpp_array = CppArrayAlias(type_def)
                var_buffer.append(f"{cpp_array.actual_type(type_registry)} {type_def.type_name};")
                self.header_includes.update(cpp_array.get_include_headers(type_registry))
            elif isinstance(type_def, VariantAlias):
                cpp_variant = CppVariantAlias(type_def)
                var_buffer.append(f"{cpp_variant.actual_type(type_registry)} {type_def.type_name};")
                self.header_includes.update(cpp_variant.get_include_headers(type_registry))
            elif isinstance(type_def, EnumType):
                cpp_enum = CppEnum(type_def)
                cpp_enum.write_header(type_buffer, type_registry)
                type_buffer.new_line()
            elif isinstance(type_def, StructType):
                cpp_struct = CppStruct(type_def)
                cpp_struct.write_header(type_buffer, type_registry)
                type_buffer.new_line()
                self.header_includes.update(cpp_struct.header_includes)
            elif isinstance(type_def, ExtendedVariant):
                cpp_struct = CppExtendedVariant(type_def)
                cpp_struct.write_header(type_buffer, type_registry)
                type_buffer.new_line()
                self.header_includes.update(cpp_struct.header_includes)
            elif isinstance(type_def, RefType):
                cpp_ref_alias = CppRefAlias(type_def)
                var_buffer.append(f"{cpp_ref_alias.target_type(type_registry)} {type_def.type_name};")
            else:
                raise TypeError(f"Unsupported struct member type: [{type_def}]")

        # generate struct
        if self.type_def.namespaces:
            buffer.append('namespace ' + '::'.join(self.type_def.namespaces))
            buffer.append('{')
            buffer.indent_up()

        if self.base_classes:
            suffix = ' : ' + ', '.join(self.base_classes)
        else:
            suffix = ''
        buffer.append(f"struct {self.type_def.type_name}{suffix}")
        buffer.append("{")

        if type_buffer:
            with IndentedBlock(buffer):
                buffer.append_buffer(type_buffer)

        if var_buffer:
            with IndentedBlock(buffer):
                buffer.append_buffer(var_buffer)
            buffer.new_line()

        # pre-defined methods
        with IndentedBlock(buffer):
            if self.member_methods:
                for method in self.member_methods:
                    buffer.append(method)
            else:
                buffer.pop()

        buffer.append('};')
        if self.type_def.namespaces:
            buffer.indent_down()
            buffer.append('}  // namespace ' + '::'.join(self.type_def.namespaces))

    def write_source(self, buffer: LineBuffer, type_registry: TypeRegistry):
        if self.type_def.namespaces:
            buffer.append('namespace ' + '::'.join(self.type_def.namespaces))
            buffer.append('{')
            buffer.indent_up()

        # internal namespace
        buffer.append(f"namespace internal")
        buffer.append("{")
        with IndentedBlock(buffer):
            # internal ToJson
            tjw = ToJsonWriter(buffer, type_registry, self.type_def)
            tjw.write_function()

            # internal FromJson
            fjw = FromJsonWriter(buffer, type_registry, self.type_def)
            fjw.write_function()

        buffer.append("}")
        buffer.new_line()

        # public ToJson
        buffer.append(f"std::string {self.type_def.type_name}::ToJson() const")
        buffer.append("{")
        with IndentedBlock(buffer):
            buffer.append('return internal::ToJson(*this).dump();')
        buffer.append("}")
        buffer.new_line()

        # public FromJson
        buffer.append(f"void {self.type_def.type_name}::FromJson(std::string const& js)")
        buffer.append("{")
        with IndentedBlock(buffer):
            buffer.append('internal::FromJson(*this, nlohmann::json::parse(js));')
        buffer.append("}")

        if self.type_def.namespaces:
            buffer.indent_down()
            buffer.append('}  // namespace ' + '::'.join(self.type_def.namespaces))
