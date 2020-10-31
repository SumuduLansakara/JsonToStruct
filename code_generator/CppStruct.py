from typing import List, Set

from code_generator.cpp_array_alias import CppArrayAlias
from code_generator.cpp_enum import CppEnum
from code_generator.cpp_ref_alias import CppRefAlias
from code_generator.cpp_simple_alias import CppSimpleAlias
from code_generator.line_buffer import LineBuffer
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_registry import TypeRegistry


class CppStruct:
    type_def: StructType
    base_classes: Set[str]
    member_methods: Set[str]

    def __init__(self, type_def: StructType):
        self.type_def = type_def
        self.base_classes = set()
        self.member_methods = set()

    def add_base_class(self, class_name):
        self.base_classes.add(class_name)

    def add_member_method(self, method_declaration):
        self.member_methods.add(method_declaration)

    def write(self, buffer: LineBuffer, type_registry: TypeRegistry) -> None:
        var_buffer = LineBuffer(0)
        type_buffer = LineBuffer(0)
        for name, type_def in self.type_def.members:
            if isinstance(type_def, SimpleAlias):
                cpp_alias = CppSimpleAlias(type_def)
                var_buffer.append(f"{cpp_alias.actual_type()} {name};")
            elif isinstance(type_def, ArrayAlias):
                cpp_array = CppArrayAlias(type_def)
                var_buffer.append(f"{cpp_array.actual_type(type_registry)} {name};")
            elif isinstance(type_def, EnumType):
                cpp_enum = CppEnum(type_def)
                cpp_enum.write(type_buffer, type_registry)
                var_buffer.append(f"{cpp_enum.enum_name()} {name};")
            elif isinstance(type_def, StructType):
                cpp_struct = CppStruct(type_def)
                cpp_struct.write(type_buffer, type_registry)
                var_buffer.append(f"{type_def.type_name} {name};")
            elif isinstance(type_def, RefType):
                cpp_ref_alias = CppRefAlias(type_def)
                var_buffer.append(f"{cpp_ref_alias.target_type(type_registry)} {name};")
            else:
                raise TypeError(f"Unsupported struct member type: {name} [{type_def}]")

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
        buffer.indent_up()
        if self.member_methods:
            for method in self.member_methods:
                buffer.append(method)
        else:
            buffer.pop()
        buffer.indent_down()

        buffer.append('}')
