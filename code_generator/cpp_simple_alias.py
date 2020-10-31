from code_generator.cpp_type_mapper import get_cpp_type
from schema_parser.type_defs.simple_alias import SimpleAlias
from schema_parser.type_registry import TypeRegistry


class CppSimpleAlias:
    type_def: SimpleAlias

    def __init__(self, type_def: SimpleAlias):
        self.type_def = type_def

    def code(self, _type_registry: TypeRegistry) -> str:
        return f"using {self.type_def.type_name} = {self.actual_type()};"

    def type_name(self) -> str:
        return self.type_def.type_name

    def actual_type(self) -> str:
        return get_cpp_type(self.type_def.actual_type)
