from schema_parser.reg_key import RegKey
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_registry import TypeRegistry


class CppRefAlias:
    type_def: RefType

    def __init__(self, type_def: RefType):
        self.type_def = type_def

    def code(self, type_registry: TypeRegistry) -> str:
        return f"using {self.type_def.type_name} = {self.target_type(type_registry)};"

    def target_type(self, type_registry: TypeRegistry) -> str:
        ref_key = RegKey.from_uri(self.type_def.target_uri)
        ref_type = type_registry.get(ref_key)
        return ref_type.type_name
