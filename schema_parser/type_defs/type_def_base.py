import json
from abc import ABC
from typing import Dict, Callable

from schema_parser.reg_key import RegKey


class TypeDefBase(ABC):
    """Base class for all type definition classes"""

    type_name: str
    reg_key: RegKey

    def __init__(self, type_name: str, reg_key: RegKey):
        self.type_name = type_name
        self.reg_key = reg_key

    @staticmethod
    def is_parsable(array_def: Dict[str, str]) -> bool:
        raise NotImplementedError

    def parse(self, definition: Dict, creator_fn: Callable, type_registry):
        raise NotImplementedError

    def dict(self):
        return {
            'type_name': self.type_name,
            'reg_key': str(self.reg_key)
        }

    def __str__(self):
        return json.dumps(self.dict(), indent=4)
