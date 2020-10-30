import json
from abc import ABC


class TypeDefBase(ABC):
    """Base class for all type definition classes"""

    def dict(self):
        raise NotImplementedError

    def __str__(self):
        return json.dumps(self.dict(), indent=4)
