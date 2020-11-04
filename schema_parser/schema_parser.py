from typing import Dict, List

from schema_parser.reg_key import RegKey
from schema_parser.type_registry import TypeRegistry
from schema_parser.utils import attribute_reader
from schema_parser.utils.type_parser import create_typedef


class SchemaParser:
    _type_registry: TypeRegistry

    def __init__(self):
        self._type_registry = TypeRegistry()

    @property
    def type_registry(self):
        return self._type_registry

    def parse_root_level(self, base_uri: str, namespaces: List[str], schema_def: Dict[str, Dict]):
        for name, definition in schema_def.items():
            if attribute_reader.is_custom_attr(name):
                continue

            if attribute_reader.is_ignored_definition(definition):
                continue

            key = RegKey(base_uri, name)
            try:
                type_defs = create_typedef(key, namespaces, name, definition, self._type_registry)
                for type_def in type_defs:
                    self._type_registry.add(type_def)
            except KeyError as e:
                print(f"KeyError in parsing schema: {name} [{e}]")
                raise
            except ValueError as e:
                print(f"Value error in parsing schema: {name} [{e}]")
                raise
            except Exception as e:
                print(f"Error in parsing schema: {name} [{e}]")
                raise
