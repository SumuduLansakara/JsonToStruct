from __future__ import annotations

from typing import List, Dict, Callable

from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.ref_type import RefType
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry


class StructType(TypeDefBase):
    members: List[TypeDefBase]

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
            # handle special attributes
            if mem_name == "additionalProperties":
                if mem_def is False and len(struct_def["properties"]) != 1:
                    raise ValueError("Struct marked as 'additionalProperties=false' has properties")
                if mem_def is True and len(struct_def["properties"]) == 1:
                    raise ValueError("Struct marked as 'additionalProperties=true' has no properties")
                continue

            mem_reg_key = self.reg_key.parent().add_leaf(mem_name)
            tds = creator_fn(mem_reg_key, [], mem_name, mem_def, type_registry)

            if len(tds) > 1:
                # if more than one member is created, that must be an array with complex inner types
                for td in tds:
                    if isinstance(td, (StructType, EnumType)):
                        type_registry.add(td, True)
                    self.members.append(td)
            else:
                assert len(tds) == 1
                td = tds[0]
                # if a single complex inner type is created, it must be a struct or an enum.
                # - a member variable must be created from that type
                # - need special care to prevent name collisions as two members are defined from single definition
                # -- provided name is given to the member variable
                # -- if the provided name starts with a lower-case letter, upper cased form is taken as type name.
                #    Otherwise it typename must have been explicitly provided via '@meta:typename' property
                if isinstance(td, (StructType, EnumType)):
                    mem_type_name = mem_def['@meta:typename'] if '@meta:typename' in mem_def \
                        else mem_name[0].upper() + mem_name[1:]
                    if mem_name == mem_type_name:
                        raise NameError(f"Unable to deduce a non colliding name for inner type of struct: "
                                        f"{self.type_name} [{mem_type_name}]")

                    td.type_name = mem_type_name
                    self.members.append(td)
                    type_registry.add(td, True)

                    # add a member variable of complex type ?
                    inner_member_ref_key = self.reg_key.parent().add_leaf(mem_name + '_var')
                    inner_member_ref = RefType([], mem_name, inner_member_ref_key)
                    inner_member_ref.target_uri = str(td.reg_key)
                    self.members.append(inner_member_ref)
                else:
                    self.members.append(td)

    def dict(self):
        return {
            **super().dict(),
            "kind": "struct",
            "members": [t_def.dict() for t_def in self.members]
        }
