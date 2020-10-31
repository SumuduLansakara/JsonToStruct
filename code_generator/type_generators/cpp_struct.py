from typing import Set

from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_array_alias import CppArrayAlias
from code_generator.type_generators.cpp_enum import CppEnum
from code_generator.type_generators.cpp_ref_alias import CppRefAlias
from code_generator.type_generators.cpp_simple_alias import CppSimpleAlias
from code_generator.type_generators.cpp_type_base import CppTypeBase
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_registry import TypeRegistry


class IndentedBlock:
    line_buffer: LineBuffer

    def __init__(self, line_buffer: LineBuffer):
        self.line_buffer = line_buffer

    def __enter__(self):
        self.line_buffer.indent_up()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.line_buffer.indent_down()


class CppStruct(CppTypeBase):
    type_def: StructType
    base_classes: Set[str]
    member_methods: Set[str]

    def __init__(self, type_def: StructType):
        super().__init__(type_def)
        self.type_def = type_def
        self.base_classes = set()
        self.member_methods = set()

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
            elif isinstance(type_def, ArrayAlias):
                cpp_array = CppArrayAlias(type_def)
                var_buffer.append(f"{cpp_array.actual_type(type_registry)} {type_def.type_name};")
            elif isinstance(type_def, EnumType):
                cpp_enum = CppEnum(type_def)
                cpp_enum.write_header(type_buffer, type_registry)
            elif isinstance(type_def, StructType):
                cpp_struct = CppStruct(type_def)
                cpp_struct.write_header(type_buffer, type_registry)
            elif isinstance(type_def, RefType):
                cpp_ref_alias = CppRefAlias(type_def)
                var_buffer.append(f"{cpp_ref_alias.target_type(type_registry)} {type_def.type_name};")
            else:
                raise TypeError(f"Unsupported struct member type: [{type_def}]")

        # write struct
        if self.base_classes:
            suffix = ' : ' + ', '.join(self.base_classes)
        else:
            suffix = ''
        buffer.append(f"struct {self.type_def.type_name}{suffix}")
        buffer.append("{")

        if type_buffer:
            buffer.append(type_buffer.str(1))
            buffer.new_line()

        if var_buffer:
            buffer.append(var_buffer.str(1))
            buffer.new_line()

        # pre-defined methods
        with IndentedBlock(buffer):
            if self.member_methods:
                for method in self.member_methods:
                    buffer.append(method)
            else:
                buffer.pop()

        buffer.append('}')

    def write_source(self, buffer: LineBuffer, type_registry: TypeRegistry):
        buffer.append(f"namespace foo")
        buffer.append("{")

        with IndentedBlock(buffer):
            buffer.append(f"namespace internal")
            buffer.append("{")
            with IndentedBlock(buffer):
                buffer.append(f"std::string ToJson({self.type_def.type_name} const& m)")
                buffer.append("{")
                buffer.append("}")
                buffer.new_line()

                buffer.append(f"void FromJson({self.type_def.type_name} const& m, nlohmann::json const& j)")
                buffer.append("{")
                buffer.append("}")

            buffer.append("}")
            buffer.new_line()

            buffer.append(f"std::string {self.type_def.type_name}::ToJson() const")
            buffer.append("{")
            with IndentedBlock(buffer):
                buffer.append('return internal::ToJson(*this).dump();')
            buffer.append("}")
            buffer.new_line()

            buffer.append(f"void {self.type_def.type_name}::FromJson(std::string const& js)")
            buffer.append("{")
            with IndentedBlock(buffer):
                buffer.append('internal::FromJson(*this, nlohmann::parse(js));')
            buffer.append("}")

        buffer.append("}")
