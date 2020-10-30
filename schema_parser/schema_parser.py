from typing import List, Union, Dict

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


class SchemaParser:
    _type_registry: TypeRegistry

    def __init__(self):
        self._type_registry = TypeRegistry()

    @property
    def type_registry(self):
        return self._type_registry

    def _get_struct_members(self, struct_reg_key: RegKey, struct_members: Dict[str, Dict]) \
            -> List[Union[BasicMemberVar, ArrayMemberVar, ReferencedMemberVar, InnerStructMember, InnerEnumMember]]:
        members: List[
            Union[BasicMemberVar, ArrayMemberVar, ReferencedMemberVar, InnerStructMember, InnerEnumMember]] = []

        for mem_name, mem_def in struct_members.items():
            mem_reg_key = struct_reg_key.add_leaf(mem_name)
            td = self._create_typedef(mem_reg_key, mem_name, mem_def)

            if isinstance(td, SimpleAlias):
                members.append(BasicMemberVar(mem_name, td.actual_type))
            elif isinstance(td, ArrayAlias):
                members.append(ArrayMemberVar(mem_name, td.element_type))
            elif isinstance(td, RefType):
                members.append(ReferencedMemberVar(mem_name, td))
            elif isinstance(td, StructType):
                members.append(InnerStructMember(mem_name, td))
            elif isinstance(td, EnumType):
                members.append(InnerEnumMember(mem_name, td))
            else:
                raise TypeError(f"Unsupported struct member: {td}")

        return members

    def _get_array_item_type(self, parent_reg_key: RegKey, array_name: str, item_def: Dict) -> Union[str, RefType]:
        if '$ref' in item_def:
            return RefType(item_def['$ref'])

        if 'type' not in item_def:
            raise ValueError(f"Property without type: {array_name} [{item_def}]")

        prop_type = item_def['type']
        if prop_type in ['boolean', 'integer', 'number', 'string']:
            return prop_type

        if prop_type == 'object':
            arr_mem_type = f"{array_name.capitalize()}_sub"
            arr_mem_reg_key = parent_reg_key.adjust_leaf(arr_mem_type)

            members = self._get_struct_members(arr_mem_reg_key, item_def['properties'])
            mem_struct_def = StructType(arr_mem_type, members)

            self._type_registry.add(arr_mem_reg_key, mem_struct_def)  # add inner member as a sibling type

            return mem_struct_def.struct_name

    def _create_typedef(self, reg_key: RegKey, prop_name: str, prop_def: Dict) \
            -> Union[RefType, EnumType, SimpleAlias, ArrayAlias, StructType]:
        if '$ref' in prop_def:
            return RefType(prop_def['$ref'])

        if 'enum' in prop_def:
            enum_def = prop_def['enum']
            return EnumType(prop_name.capitalize(), [e for e in enum_def])

        if 'type' not in prop_def:
            raise ValueError(f"Property without type: {reg_key}")

        prop_type = prop_def['type']
        if prop_type in ['boolean', 'integer', 'number', 'string']:
            return SimpleAlias(prop_name.capitalize(), prop_type)

        if prop_type == 'array':
            if 'items' not in prop_def:
                raise ValueError(f"Array definition without items [{reg_key}]")
            item_def = self._get_array_item_type(reg_key, prop_name, prop_def['items'])
            return ArrayAlias(prop_name.capitalize(), item_def)

        if prop_type == 'object':
            members = self._get_struct_members(reg_key, prop_def['properties'])
            return StructType(prop_name.capitalize(), members)

    def parse_root_level(self, base_uri: str, namespace: str, schema_def: Dict):
        self._type_registry.set_namespace(namespace)
        for k, v in schema_def.items():
            key = RegKey(base_uri, k)
            try:
                type_def = self._create_typedef(key, k, v)
                self._type_registry.add(key, type_def)
            except KeyError as e:
                print(f"KeyError: {e}")
                raise
            except ValueError as e:
                print(f"ValueError: {e}")
                raise
            except Exception as e:
                print(f"Error: {e}")
