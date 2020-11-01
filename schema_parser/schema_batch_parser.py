import json
import os
from typing import List

from schema_parser.schema_parser import SchemaParser


class SchemaFile:
    file_path: str
    namespace: str

    def __init__(self, file_path: str, namespace: str):
        self.file_path = file_path
        self.namespace = namespace


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
                try:
                    schema_def = json.load(j_file)
                except:
                    print(f"failed loading file: {schema_file.file_path}", flush=True)
                    raise
                self._parser.parse_root_level('#/definitions', schema_file.namespace, schema_def["definitions"])

        # print('>' * 80)
        # for e in self.type_registry:
        #     print('>> ', e[0], flush=True)
        #     print(e[0], e[1])
        # print('<' * 80)

    def set_dir_offset(self, dir_path: str):
        if not os.path.isdir(dir_path):
            raise FileNotFoundError(f"Schema definition offset directory does not exist [{dir_path}]")
        self._file_directory_offset = dir_path
