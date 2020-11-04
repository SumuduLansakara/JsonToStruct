from typing import Set

from code_generator.line_buffer import LineBuffer, IndentedBlock
from code_generator.type_generators.cpp_array_alias import CppArrayAlias
from code_generator.type_generators.cpp_enum import CppEnum
from code_generator.type_generators.cpp_extended_variant_utils.from_json_generator import FromJsonWriter
from code_generator.type_generators.cpp_extended_variant_utils.to_json_generator import ToJsonWriter
from code_generator.type_generators.cpp_simple_alias import CppSimpleAlias
from code_generator.type_generators.cpp_type_base import CppTypeBase
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.extended_variant import ExtendedVariant
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_registry import TypeRegistry


class CppExtendedVariant(CppTypeBase):
    type_def: ExtendedVariant
    base_classes: Set[str]
    member_methods: Set[str]
    header_includes: Set[str]
    cpp_includes: Set[str]

    def __init__(self, type_def: ExtendedVariant):
        super().__init__(type_def)
        self.type_def = type_def
        self.base_classes = set()
        self.member_methods = set()
        self.header_includes = {'variant'}
        self.cpp_includes = {'nlohmann/json.hpp'}

    def add_base_class(self, class_name):
        self.base_classes.add(class_name)

    def add_member_method(self, method_declaration):
        self.member_methods.add(method_declaration)

    def write_header(self, buffer: LineBuffer, type_registry: TypeRegistry) -> None:
        # generate extended struct
        if self.type_def.namespaces:
            buffer.append('namespace ' + '::'.join(self.type_def.namespaces))
            buffer.append('{')
            buffer.indent_up()

        if self.base_classes:
            suffix = ' : ' + ', '.join(self.base_classes)
        else:
            suffix = ''
        variant_members = []
        for member_type_def in self.type_def.content_variant.member_type_defs:
            if isinstance(member_type_def, SimpleAlias):
                cpp_alias = CppSimpleAlias(member_type_def)
                variant_members.append(cpp_alias.actual_type())
            elif isinstance(member_type_def, ArrayAlias):
                cpp_array = CppArrayAlias(member_type_def)
                variant_members.append(cpp_array.actual_type(type_registry))
            # elif isinstance(member_type_def, StructType):
            #     cpp_struct = CppStruct(member_type_def)
            #     variant_members.append(cpp_struct.type_def.type_name)
            elif isinstance(member_type_def, RefType):
                target_type = type_registry.get_ref_target(member_type_def.target_uri)
                variant_members.append(target_type.type_name)
            else:
                raise TypeError(f"Unsupported struct member type: [{member_type_def}]")

        buffer.append(f"struct {self.type_def.type_name}{suffix} : std::variant<{','.join(variant_members)}>")
        buffer.append("{")

        with IndentedBlock(buffer):
            # write type enum
            cpp_enum = CppEnum(self.type_def.type_enum)
            cpp_enum.type_def.type_name = cpp_enum.type_def.type_name.capitalize()
            cpp_enum.write_header(buffer, type_registry)
            buffer.append('')

            # write setter
            buffer.append('template <Type MemberType, typename T>')
            buffer.append(f'void SetAs(T value)')
            buffer.append('{')
            with IndentedBlock(buffer):
                buffer.append(f'emplace<MemberType>(value);')
            buffer.append('}')
            buffer.append('')

            # write setter
            buffer.append('template <Type MemberType>')
            buffer.append(f'T GetAs()')
            buffer.append('{')
            with IndentedBlock(buffer):
                buffer.append(f'return std::get<MemberType>(*this);')
            buffer.append('}')

            # pre-defined methods
            with IndentedBlock(buffer):
                if self.member_methods:
                    for method in self.member_methods:
                        buffer.append(method)

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
            fjw = FromJsonWriter(buffer, type_registry, self.type_def)
            fjw.write_function()

            tjw = ToJsonWriter(buffer, type_registry, self.type_def)
            tjw.write_function()

        buffer.append("}")
        buffer.new_line()

        if self.type_def.namespaces:
            buffer.indent_down()
            buffer.append('}  // namespace ' + '::'.join(self.type_def.namespaces))
