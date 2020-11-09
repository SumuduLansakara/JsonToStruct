import json
import os
from typing import List

from schema_parser import configs
from schema_parser.schema_parser import SchemaParser


class SchemaBatchParser:
    _build_order: List[str]
    _parser: SchemaParser
    _file_directory_offset: str

    def __init__(self):
        self._build_order = []
        self._parser = SchemaParser()
        self._file_directory_offset = ''

    @property
    def type_registry(self):
        return self._parser.type_registry

    def add_schema_file(self, file_path: str):
        self._build_order.append(file_path)

    def _get_abs_path(self, file_path: str) -> str:
        return os.path.join(self._file_directory_offset, file_path)

    def parse(self, ns_offset: List[str]):
        for schema_file_path in self._build_order:
            with open(self._get_abs_path(schema_file_path)) as j_file:
                try:
                    schema_def = json.load(j_file)
                except:
                    print(f"failed loading file: {schema_file_path}", flush=True)
                    raise
                ns_key = configs.CUSTOM_ATTR_PREFIX + 'namespace'
                namespaces = ns_offset + schema_def[ns_key].split('::') if ns_key in schema_def else ns_offset
                try:
                    self._parser.parse_root_level('#/definitions', namespaces, schema_def["definitions"])
                except Exception as ex:
                    print(f"Failed parsing schema file [{schema_file_path}]")
                    raise

    def set_input_dir(self, dir_path: str):
        if not os.path.isdir(dir_path):
            raise FileNotFoundError(f"Schema definition directory does not exist [{dir_path}]")
        self._file_directory_offset = dir_path
