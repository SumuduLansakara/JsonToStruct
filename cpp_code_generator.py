from typing import Dict, List

from schema_parser.type_defs import BasicAliasDef, ArrayAliasDef, EnumTypeDef, StructTypeDef, MemberVarDef, \
    ReferencedMemberVarDef
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

    def generate_basic_type_alias(self, alias_def: BasicAliasDef) -> LineBuffer:
        code = LineBuffer(0)
        code.append(f"using {alias_def.alias_name} = {self.get_cpp_type(alias_def.actual_type)};")
        return code

    def generate_array_type_alias(self, array_def: ArrayAliasDef) -> LineBuffer:
        code = LineBuffer(0)
        code.append(f"using {array_def.alias_name} = std::vector<{self.get_cpp_type(array_def.element_type)}>;")
        return code

    def generate_enum(self, enum_def: EnumTypeDef) -> LineBuffer:
        code = LineBuffer(0)
        code.append(f"enum class {enum_def.enum_name}")
        code.append('{')
        for i, m in enumerate(enum_def.members):
            code.append(f"    {m} = {i},")
        code.append('}')
        return code

    def generate_struct(self, struct_def: StructTypeDef) -> LineBuffer:
        code = LineBuffer(0)
        code.append(f"struct {struct_def.struct_name} : ISerializable")
        code.append("{")
        for prop in struct_def.properties:
            if isinstance(prop, StructTypeDef):
                pass
            if isinstance(prop, EnumTypeDef):
                pass
            if isinstance(prop, ReferencedMemberVarDef):
                ref_key = RegKey(*prop.ref_type_def.ref_target_uri.split('/'))
                ref_type = self._type_registry.get(ref_key)
                type_name: str
                if isinstance(ref_type, StructTypeDef):
                    type_name = ref_type.struct_name
                elif isinstance(ref_type, EnumTypeDef):
                    type_name = ref_type.enum_name
                elif isinstance(ref_type, BasicAliasDef):
                    type_name = ref_type.alias_name
                elif isinstance(ref_type, ArrayAliasDef):
                    type_name = ref_type.alias_name
                else:
                    raise RuntimeError(f"Referenced type definition not found! {ref_key}")
                code.append(f"    {self.get_cpp_type(type_name)} {prop.member_var_name};")
            if isinstance(prop, MemberVarDef):
                code.append(f"    {self.get_cpp_type(prop.member_var_type)} {prop.member_var_name};")
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
            if isinstance(type_def, BasicAliasDef):
                c = self.generate_basic_type_alias(type_def)

                if ns not in basic_aliases:
                    basic_aliases[ns] = []
                basic_aliases[ns].append(c)
            elif isinstance(type_def, ArrayAliasDef):
                c = self.generate_array_type_alias(type_def)
                if ns not in array_aliases:
                    array_aliases[ns] = []
                array_aliases[ns].append(c)
            elif isinstance(type_def, EnumTypeDef):
                c = self.generate_enum(type_def)
                if ns not in enum_defs:
                    enum_defs[ns] = []
                enum_defs[ns].append(c)
            elif isinstance(type_def, StructTypeDef):
                c = self.generate_struct(type_def)
                if ns not in struct_defs:
                    struct_defs[ns] = []
                struct_defs[ns].append(c)
            else:
                raise NotImplementedError(f"Unsupported type definition: {key}")

        print("// basic type definitions")
        for ns, tdl in basic_aliases.items():
            print(f"namespace {ns}")
            print("{")
            for td in tdl:
                print(td)
            print("}")
        print()

        print("// array type definitions")
        for ns, tdl in array_aliases.items():
            print(f"namespace {ns}")
            print("{")
            for td in tdl:
                print(td)
            print("}")
        print()

        print("// enum type definitions")
        for ns, tdl in enum_defs.items():
            print(f"namespace {ns}")
            print("{")
            for td in tdl:
                print(td)
            print("}")
        print()

        print("// struct type definitions")
        for ns, tdl in struct_defs.items():
            print(f"namespace {ns}")
            print("{")
            for td in tdl:
                print(td)
            print("}")
        print()
