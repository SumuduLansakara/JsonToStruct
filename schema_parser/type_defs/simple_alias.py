from schema_parser.type_defs.type_def_base import TypeDefBase


class SimpleAlias(TypeDefBase):
    """Simple type alias"""
    alias_name: str
    actual_type: str

    def __init__(self, alias_name: str, actual_type: str):
        self.alias_name = alias_name
        self.actual_type = actual_type

    def dict(self):
        return {
            "kind": "type_alias",
            "alias": self.alias_name,
            "type": self.actual_type,
        }
