from schema_parser.type_defs.type_def_base import TypeDefBase


class RefType(TypeDefBase):
    """Virtual type holding reference to a concrete type. Used for late reference resolution"""
    ref_target_uri: str

    def __init__(self, ref_target_uri: str):
        self.ref_target_uri = ref_target_uri

    def dict(self):
        return {
            "ref_target_uri": self.ref_target_uri
        }
