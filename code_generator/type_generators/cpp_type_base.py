from abc import ABC
from typing import List, Set

from code_generator.line_buffer import LineBuffer
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


class CppTypeBase(ABC):
    type_def: TypeDefBase
    header_includes: Set[str]

    def __init__(self, type_def: TypeDefBase):
        self.type_def = type_def
        self.header_includes = set()

    def write_header(self, buffer: LineBuffer, _type_registry: TypeRegistry) -> None:
        raise NotImplementedError

    def write_source(self, buffer: LineBuffer, _type_registry: TypeRegistry) -> None:
        pass

    def get_include_headers(self, _type_registry: TypeRegistry) -> List[str]:
        return []
