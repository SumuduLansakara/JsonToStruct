from __future__ import annotations

from typing import List, Dict, Callable, Tuple

from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


class StructType(TypeDefBase):
    struct_name: str
    members: List[Tuple[str, TypeDefBase]]

    @staticmethod
    def is_parsable(struct_def: Dict[str, str]) -> bool:
        if 'type' in struct_def and struct_def['type'] == 'object':
            if 'properties' not in struct_def:
                raise ValueError(f"Struct definition without properties [{struct_def}]")
            return True
        return False

    def parse(self, struct_def: Dict, creator_fn: Callable, type_registry: TypeRegistry):
        self.members = []
        for mem_name, mem_def in struct_def['properties'].items():
            mem_reg_key = self.reg_key.parent().add_leaf(mem_name)
            td = creator_fn(mem_reg_key, mem_name, mem_def, type_registry)
            self.members.append((mem_name, td))

    def dict(self):
        return {
            **super().dict(),
            "kind": "struct",
            "members": [(name, t_def.dict()) for name, t_def in self.members]
        }
