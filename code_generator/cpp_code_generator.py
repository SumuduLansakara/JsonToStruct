from typing import Dict, List

from code_generator.CppStruct import CppStruct
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


class CodeGenerator:
    _cpp_type_map: Dict[str, str]
    _type_registry: TypeRegistry

    def __init__(self, type_registry: TypeRegistry):
        self._type_registry = type_registry

    def generate_ref_type_alias(self, ref_def: RefType) -> LineBuffer:
        code = LineBuffer(0)
        cpp_alias = CppRefAlias(ref_def)
        code.append(cpp_alias.code(self._type_registry))
        return code

    def generate_basic_type_alias(self, alias_def: SimpleAlias) -> LineBuffer:
        code = LineBuffer(0)
        cpp_alias = CppSimpleAlias(alias_def)
        code.append(cpp_alias.code(self._type_registry))
        return code

    def generate_array_type_alias(self, array_def: ArrayAlias) -> LineBuffer:
        code = LineBuffer(0)
        cpp_array = CppArrayAlias(array_def)
        code.append(cpp_array.code(self._type_registry))
        return code

    def generate_enum(self, enum_def: EnumType) -> LineBuffer:
        code = LineBuffer(0)
        cpp_enum = CppEnum(enum_def)
        cpp_enum.write(code, self._type_registry)
        return code

    def generate_struct(self, struct_def: StructType) -> LineBuffer:
        code = LineBuffer(0)
        cpp_struct = CppStruct(struct_def)
        cpp_struct.add_base_class('ISerializable')
        cpp_struct.add_member_method('[[nodiscard]] std::string ToJson() const override;')
        cpp_struct.add_member_method('void FromJson(const std::string&) override;')
        cpp_struct.write(code, self._type_registry)
        return code

    def generate(self):
        basic_aliases: Dict[str, List] = {}
        array_aliases: Dict[str, List] = {}
        enum_defs: Dict[str, List] = {}
        struct_defs: Dict[str, List] = {}

        for key, type_def in self._type_registry:
            ns = self._type_registry.get_namespace(key)
            if isinstance(type_def, SimpleAlias):
                c = self.generate_basic_type_alias(type_def)

                if ns not in basic_aliases:
                    basic_aliases[ns] = []
                basic_aliases[ns].append(c.str())
            elif isinstance(type_def, ArrayAlias):
                c = self.generate_array_type_alias(type_def)
                if ns not in array_aliases:
                    array_aliases[ns] = []
                array_aliases[ns].append(c.str())
            elif isinstance(type_def, EnumType):
                c = self.generate_enum(type_def)
                if ns not in enum_defs:
                    enum_defs[ns] = []
                enum_defs[ns].append(c.str())
            elif isinstance(type_def, StructType):
                c = self.generate_struct(type_def)
                if ns not in struct_defs:
                    struct_defs[ns] = []
                struct_defs[ns].append(c.str())
            elif isinstance(type_def, RefType):
                c = self.generate_ref_type_alias(type_def)
                if ns not in basic_aliases:
                    basic_aliases[ns] = []
                basic_aliases[ns].append(c.str())
                continue
            else:
                raise NotImplementedError(f"Unsupported type definition: {key} [{type_def}]")

        for ns, tdl in basic_aliases.items():
            print(f"namespace {ns}")
            print("{")
            for td in tdl:
                print(td)
            print("}")

        for ns, tdl in array_aliases.items():
            print(f"namespace {ns}")
            print("{")
            for td in tdl:
                print(td)
            print("}")

        for ns, tdl in enum_defs.items():
            print(f"namespace {ns}")
            print("{")
            for td in tdl:
                print(td)
            print("}")

        for ns, tdl in struct_defs.items():
            print(f"namespace {ns}")
            print("{")
            for td in tdl:
                print(td)
            print("}")
