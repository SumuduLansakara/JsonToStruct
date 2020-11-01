from code_generator.line_buffer import LineBuffer
from code_generator.type_generators.cpp_type_base import CppTypeBase
from code_generator.type_generators.inner_type_parser import variant_element_type
from schema_parser.type_defs.variant_alias import VariantAlias
from schema_parser.type_registry import TypeRegistry


class CppVariantAlias(CppTypeBase):
    type_def: VariantAlias

    def write_header(self, buffer: LineBuffer, type_registry: TypeRegistry) -> None:
        buffer.append(f"using {self.type_def.type_name} = {self.actual_type(type_registry)};")

    def actual_type(self, type_registry: TypeRegistry):
        return variant_element_type(self.type_def, type_registry)

    def get_include_headers(self, _type_registry: TypeRegistry):
        return ["variant"]
