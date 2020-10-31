from typing import Dict

from schema_parser.reg_key import RegKey
from schema_parser.type_parser import create_typedef
from schema_parser.type_registry import TypeRegistry


class SchemaParser:
    _type_registry: TypeRegistry

    def __init__(self):
        self._type_registry = TypeRegistry()

    @property
    def type_registry(self):
        return self._type_registry

    def parse_root_level(self, base_uri: str, namespace: str, schema_def: Dict):
        self._type_registry.set_namespace(namespace)
        for name, definition in schema_def.items():
            key = RegKey(base_uri, name)
            try:
                type_defs = create_typedef(key, name, definition, self._type_registry)
                for type_def in type_defs:
                    self._type_registry.add(type_def)
            except KeyError as e:
                print(f"KeyError: {e}")
                raise
            except ValueError as e:
                print(f"ValueError: {e}")
            except Exception as e:
                print(f"Error: {e}")
                raise
