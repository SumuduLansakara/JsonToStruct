from typing import Dict, List

from schema_parser.member_defs.array_mem_var import ArrayMemberVar
from schema_parser.member_defs.basic_mem_var import BasicMemberVar
from schema_parser.member_defs.inner_enum_member import InnerEnumMember
from schema_parser.member_defs.inner_struct_member import InnerStructMember
from schema_parser.member_defs.ref_mem_var import ReferencedMemberVar
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_registry import TypeRegistry, RegKey


class LineBuffer:
    _lines: List[str]
    _indent: int

    def __init__(self, indent: int, *lines):
        self._lines = list(lines)
        self._indent = indent

    def prepend(self, *lines):
        for line in reversed(lines):
            self._lines.insert(0, line)

    def append(self, line: str):
        self._lines.append(line)

    def set_indentation(self, indent: int):
        self._indent = indent

    def __str__(self):
        prefix = ' ' * self._indent
        return '\n'.join([prefix + line for line in self._lines])


class CodeGenerator:
    _cpp_type_map: Dict[str, str]
    _type_registry: TypeRegistry

    def __init__(self, type_registry: TypeRegistry):
        self._type_registry = type_registry
        self._cpp_type_map = {
            "boolean": "bool",
            "integer": "std::int64",
            "number": "float",
            "string": "std::string",
        }

    def get_cpp_type(self, type_str: str):
        if type_str not in self._cpp_type_map:
            return type_str
        return self._cpp_type_map[type_str]

    def generate_basic_type_alias(self, alias_def: SimpleAlias) -> LineBuffer:
        code = LineBuffer(0)
        code.append(f"using {alias_def.alias_name} = {self.get_cpp_type(alias_def.actual_type)};")
        return code

    def generate_array_type_alias(self, array_def: ArrayAlias) -> LineBuffer:
        code = LineBuffer(0)
        ele_type_def = array_def.element_type
        if isinstance(ele_type_def, str):
            code.append(f"using {array_def.alias_name} = std::vector<{self.get_cpp_type(ele_type_def)}>;")
        elif isinstance(ele_type_def, RefType):
            ref_key = RegKey(*ele_type_def.ref_target_uri.split('/'))
            ref_type = self._type_registry.get(ref_key)
            type_name: str
            if isinstance(ref_type, StructType):
                type_name = ref_type.struct_name
            elif isinstance(ref_type, EnumType):
                type_name = ref_type.enum_name
            elif isinstance(ref_type, SimpleAlias):
                type_name = ref_type.alias_name
            elif isinstance(ref_type, ArrayAlias):
                type_name = ref_type.alias_name
            else:
                raise RuntimeError(f"Referenced type definition not found! {ref_key}")
            code.append(f"using {array_def.alias_name} = std::vector<{self.get_cpp_type(type_name)}>;")
        else:
            raise TypeError(f"Unsupported array element type: {array_def}")
        return code

    def generate_enum(self, enum_def: EnumType) -> LineBuffer:
        code = LineBuffer(0)
        code.append(f"enum class {enum_def.enum_name}")
        code.append('{')
        for i, m in enumerate(enum_def.members):
            code.append(f"    {m} = {i},")
        code.append('}')
        return code

    def generate_struct(self, struct_def: StructType) -> LineBuffer:
        code = LineBuffer(0)
        code.append(f"struct {struct_def.struct_name} : ISerializable")
        code.append("{")
        for prop in struct_def.members:
            if isinstance(prop, BasicMemberVar):
                code.append(f"    {self.get_cpp_type(prop.member_var_type)} {prop.member_var_name};")
            elif isinstance(prop, ArrayMemberVar):
                code.append(f"    std::vector<{prop.element_type}> {prop.member_var_name};")
            elif isinstance(prop, InnerStructMember):
                inner_struct = self.generate_struct(prop.struct_def)
                inner_struct.set_indentation(4)
                code.append(str(inner_struct))
                code.append(f"    {prop.struct_def.struct_name} {prop.member_var_name};")
            elif isinstance(prop, InnerEnumMember):
                inner_enum = self.generate_enum(prop.enum_def)
                inner_enum.set_indentation(4)
                code.append(str(inner_enum))
                code.append(f"    {prop.enum_def.enum_name} {prop.member_var_name};")
            elif isinstance(prop, ReferencedMemberVar):
                ref_key = RegKey(*prop.ref_type_def.ref_target_uri.split('/'))
                ref_type = self._type_registry.get(ref_key)
                type_name: str
                if isinstance(ref_type, StructType):
                    type_name = ref_type.struct_name
                elif isinstance(ref_type, EnumType):
                    type_name = ref_type.enum_name
                elif isinstance(ref_type, SimpleAlias):
                    type_name = ref_type.alias_name
                elif isinstance(ref_type, ArrayAlias):
                    type_name = ref_type.alias_name
                else:
                    raise RuntimeError(f"Referenced type definition not found! {ref_key}")
                code.append(f"    {self.get_cpp_type(type_name)} {prop.member_var_name};")
            else:
                raise TypeError(f"Unsupported struct member type: [{prop}]")
        code.append("")
        code.append("    [[nodiscard]] std::string ToJson() const override;")
        code.append("    void FromJson(const std::string&) override;")
        code.append("}")
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
                basic_aliases[ns].append(c)
            elif isinstance(type_def, ArrayAlias):
                c = self.generate_array_type_alias(type_def)
                if ns not in array_aliases:
                    array_aliases[ns] = []
                array_aliases[ns].append(c)
            elif isinstance(type_def, EnumType):
                c = self.generate_enum(type_def)
                if ns not in enum_defs:
                    enum_defs[ns] = []
                enum_defs[ns].append(c)
            elif isinstance(type_def, StructType):
                c = self.generate_struct(type_def)
                if ns not in struct_defs:
                    struct_defs[ns] = []
                struct_defs[ns].append(c)
            else:
                raise NotImplementedError(f"Unsupported type definition: {key}")

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
