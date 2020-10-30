from typing import List, Union, Dict

from schema_parser.type_defs import MemberVarDef, StructTypeDef, EnumTypeDef, BasicAliasDef, ArrayAliasDef, RefTypeDef, \
    ReferencedMemberVarDef
from schema_parser.type_registry import TypeRegistry, RegKey


class SchemaParser:
    _type_registry: TypeRegistry

    def __init__(self):
        self._type_registry = TypeRegistry()

    @property
    def type_registry(self):
        return self._type_registry

    def _get_struct_members(self, struct_reg_key: RegKey, obj_props: Dict[str, Dict]) \
            -> List[Union[MemberVarDef, StructTypeDef]]:
        members: List[Union[MemberVarDef, ReferencedMemberVarDef, StructTypeDef, EnumTypeDef]] = []

        for mem_name, mem_def in obj_props.items():
            mem_reg_key = struct_reg_key.add_leaf(mem_name)
            td = self._create_typedef(mem_reg_key, mem_name, mem_def)

            if isinstance(td, BasicAliasDef):
                m = MemberVarDef(mem_name, td.actual_type)
                members.append(m)

            if isinstance(td, ArrayAliasDef):
                m = MemberVarDef(mem_name, td.alias_name)
                members.append(m)

            if isinstance(td, RefTypeDef):
                m = ReferencedMemberVarDef(mem_name, td)
                members.append(m)

            if isinstance(td, StructTypeDef):
                m = MemberVarDef(mem_name, td.struct_name)
                members.append(td)
                members.append(m)

            if isinstance(td, EnumTypeDef):
                m = MemberVarDef(mem_name, td.enum_name)
                members.append(td)
                members.append(m)

        return members

    def _get_array_item_type(self, parent_reg_key: RegKey, array_name: str, item_def: Dict) -> str:
        if '$ref' in item_def:
            ref_uri = item_def['$ref']
            ref_key = RegKey(*ref_uri.split('/'))
            ref_def = self._type_registry.get(ref_key)

            if isinstance(ref_def, BasicAliasDef):
                return ref_def.alias_name

            if isinstance(ref_def, StructTypeDef):
                return ref_def.struct_name

            raise NotImplementedError(f"Unsupported reference type as array member [{ref_def}]")

        if 'type' not in item_def:
            raise ValueError(f"Property without type: {array_name} [{item_def}]")

        prop_type = item_def['type']
        if prop_type in ['boolean', 'integer', 'number', 'string']:
            return prop_type

        if prop_type == 'object':
            arr_mem_type = f"{array_name.capitalize()}_sub"
            arr_mem_reg_key = parent_reg_key.adjust_leaf(arr_mem_type)

            members = self._get_struct_members(arr_mem_reg_key, item_def['properties'])
            mem_struct_def = StructTypeDef(arr_mem_type, members)

            self._type_registry.add(arr_mem_reg_key, mem_struct_def)  # add inner member as a sibling type

            return mem_struct_def.struct_name

    def _create_typedef(self, reg_key: RegKey, prop_name: str, prop_def: Dict) \
            -> Union[RefTypeDef, EnumTypeDef, BasicAliasDef, ArrayAliasDef, StructTypeDef]:
        if '$ref' in prop_def:
            return RefTypeDef(prop_def['$ref'])

        if 'enum' in prop_def:
            enum_def = prop_def['enum']
            return EnumTypeDef(prop_name.capitalize(), [e for e in enum_def])

        if 'type' not in prop_def:
            raise ValueError(f"Property without type: {reg_key}")

        prop_type = prop_def['type']
        if prop_type in ['boolean', 'integer', 'number', 'string']:
            return BasicAliasDef(prop_name.capitalize(), prop_type)

        if prop_type == 'array':
            if 'items' not in prop_def:
                raise ValueError(f"Array definition without items [{reg_key}]")
            item_def = self._get_array_item_type(reg_key, prop_name, prop_def['items'])
            return ArrayAliasDef(prop_name.capitalize(), item_def)

        if prop_type == 'object':
            members = self._get_struct_members(reg_key, prop_def['properties'])
            return StructTypeDef(prop_name.capitalize(), members)

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
            except Exception as e:
                print(f"Error: {e}")
