import json
from abc import ABC


class MemberDefBase(ABC):
    """Base class for all member definition classes"""

    def dict(self):
        raise NotImplementedError

    def __str__(self):
        return json.dumps(self.dict(), indent=4)
