import json
import os
from typing import List

from schema_parser.schema_parser import SchemaParser


class SchemaFile:
    _file_path: str
    _namespace: str

    def __init__(self, file_path: str, namespace: str):
        self._file_path = file_path
        self._namespace = namespace

    @property
    def file_path(self):
        return self._file_path

    @property
    def namespace(self):
        return self._namespace


class SchemaBatchParser:
    _build_order: List[SchemaFile]
    _parser: SchemaParser
    _file_directory_offset: str

    def __init__(self):
        self._build_order = []
        self._parser = SchemaParser()
        self._file_directory_offset = ''

    @property
    def type_registry(self):
        return self._parser.type_registry

    def add_schema_file(self, file_path: str, namespace: str):
        self._build_order.append(SchemaFile(file_path, namespace))

    def _get_abs_path(self, schema_file: SchemaFile) -> str:
        return os.path.join(self._file_directory_offset, schema_file.file_path)

    def parse(self):
        for schema_file in self._build_order:
            with open(self._get_abs_path(schema_file)) as j_file:
                schema_def = json.load(j_file)
                self._parser.parse_root_level('#/definitions', schema_file.namespace, schema_def["definitions"])

    def set_dir_offset(self, dir_path: str):
        if not os.path.isdir(dir_path):
            raise FileNotFoundError(f"Schema definition offset directory does not exist [{dir_path}]")
        self._file_directory_offset = dir_path
