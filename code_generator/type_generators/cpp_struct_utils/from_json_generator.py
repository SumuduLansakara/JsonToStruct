from typing import Union

from code_generator.line_buffer import LineBuffer, IndentedBlock
from code_generator.type_generators.cpp_array_alias import CppArrayAlias
from code_generator.type_generators.cpp_simple_alias import CppSimpleAlias
from schema_parser.type_defs.array_alias import ArrayAlias
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_defs.struct_type import StructType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_defs.variant_alias import VariantAlias
from schema_parser.type_registry import TypeRegistry


class FromJsonWriter:
    buffer: LineBuffer
    type_registry: TypeRegistry
    container_struct: StructType

    def __init__(self, buffer: LineBuffer, type_registry: TypeRegistry, container_struct: StructType):
        self.buffer = buffer
        self.type_registry = type_registry
        self.container_struct = container_struct

    def write_function(self):
        self.buffer.append(f"void FromJson({self.container_struct.type_name}& m, nlohmann::json const& j)")
        self.buffer.append("{")
        with IndentedBlock(self.buffer):
            self._write_body()
        self.buffer.append("}")

    def _get_variant_type_enum(self) -> Union[EnumType, None]:
        type_enums = [m for m in self.container_struct.members if isinstance(m, EnumType) and m.type_name == 'Type']
        if type_enums:
            assert len(type_enums) == 1
            return type_enums[0]
        return None

    def _get_variant_case_type_member(self, case_id: int) -> Union[str, int]:
        var_type_enum = self._get_variant_type_enum()
        if not var_type_enum:
            return case_id
        return f"{self.container_struct.type_name}::{var_type_enum.type_name}::{var_type_enum.members[case_id]}"

    def _write_body(self):
        for member_def in self.container_struct.members:
            if isinstance(member_def, SimpleAlias):
                self._load_simple_member(member_def.type_name)
            elif isinstance(member_def, ArrayAlias):
                self._load_simple_member(member_def.type_name)
            elif isinstance(member_def, RefType):
                self._load_ref_member(member_def)
            elif isinstance(member_def, VariantAlias):
                self._load_variant_member(member_def)
            elif isinstance(member_def, (EnumType, StructType)):
                pass
            else:
                raise TypeError(f"Unsupported member type: {member_def}")

    def _load_simple_member(self, member_name: str):
        self.buffer.append(f'm.{member_name} = j.at("{member_name}").get<decltype(m.{member_name})>();')

    def _load_ref_member(self, member: RefType):
        target_type = self.type_registry.get_ref_target(member.target_uri)
        if isinstance(target_type, EnumType):
            self._load_simple_member(member.type_name)
        elif isinstance(target_type, StructType):
            self.buffer.append(f'internal::FromJson(m.{member.type_name}, j.at("{member.type_name}"))')

    def _load_variant_member(self, variant: VariantAlias):
        var_type_enum = self._get_variant_type_enum()
        if var_type_enum:
            self.buffer.append(f"switch(static_cast<{var_type_enum.type_name}>(m.type))")
        else:
            self.buffer.append(f"switch(m.{variant.type_name}.index())")

        self.buffer.append('{')
        with IndentedBlock(self.buffer):
            for i, var_member in enumerate(variant.member_type_defs):
                self.buffer.append(f'case {self._get_variant_case_type_member(i)}:')
                self.buffer.append('{')
                with IndentedBlock(self.buffer):
                    self._load_variant_member_case(variant, var_member)
                    self.buffer.append('break;')
                self.buffer.append('}')
            # default case
            self.buffer.append('default:')
            self.buffer.append('{')
            with IndentedBlock(self.buffer):
                self.buffer.append('throw std::runtime_error(std::string() + "Unsupported variant type: " + '
                                   'std::to_string(m.content.index()));')
            self.buffer.append('}')
        self.buffer.append('}')

    def _load_ref_variant_member_case(self, variant: VariantAlias, member: RefType):
        target_type = self.type_registry.get_ref_target(member.target_uri)
        if isinstance(target_type, SimpleAlias):
            self._load_simple_member(variant.type_name)
        elif isinstance(target_type, EnumType):
            self._load_simple_member(variant.type_name)
        elif isinstance(target_type, StructType):
            self.buffer.append(f'internal::FromJson(m.{variant.type_name}, j.at("{target_type.type_name}"))')

    def _load_variant_member_case(self, variant: VariantAlias, member: TypeDefBase):
        if isinstance(member, SimpleAlias):
            cpp_simple_alias = CppSimpleAlias(member)
            self.buffer.append(
                f'm.{variant.type_name} = j.at("{variant.type_name}").get<{cpp_simple_alias.actual_type()}>();')
        elif isinstance(member, ArrayAlias):
            cpp_array_alias = CppArrayAlias(member)
            self.buffer.append(f'm.{variant.type_name} = j.at("{variant.type_name}").'
                               f'get<{cpp_array_alias.actual_type(self.type_registry)}>();')
        elif isinstance(member, StructType):
            self.buffer.append(f'internal::FromJson(m.{member.type_name}, j.at("{member.type_name}"))')
        elif isinstance(member, RefType):
            self._load_ref_variant_member_case(variant, member)
