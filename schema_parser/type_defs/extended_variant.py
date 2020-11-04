from __future__ import annotations

from typing import Dict, Callable, List

from schema_parser.reg_key import RegKey
from schema_parser.type_defs.enum_type import EnumType
from schema_parser.type_defs.type_def_base import TypeDefBase, TypeDefKind
from schema_parser.type_defs.variant_alias import VariantAlias
from schema_parser.type_registry import TypeRegistry


class ExtendedVariant(TypeDefBase):
    type_enum: EnumType
    content_variant: VariantAlias

    def __init__(self, namespaces: List[str], type_name: str, reg_key: RegKey):
        super().__init__(namespaces, type_name, reg_key, TypeDefKind.ExtendedVariantType)

    def parse(self, struct_def: Dict, creator_fn: Callable, type_registry: TypeRegistry):
        # verify property count and names
        if 'type' not in struct_def['properties']:
            raise ValueError(f"Extended variant type without 'type' property: {struct_def}")
        if 'content' not in struct_def['properties']:
            raise ValueError(f"Extended variant type without 'content' property: {struct_def}")
        assert len(struct_def['properties']) == 2

        properties = struct_def['properties']

        enum_reg_key = self.reg_key.parent().add_leaf('type')
        tds = creator_fn(enum_reg_key, [], 'type', properties['type'], type_registry)
        if len(tds) != 1 or not isinstance(tds[0], EnumType):
            raise ValueError(f"Extended enum property 'type' must be an enum: {properties['type']}")
        self.type_enum = tds[0]

        variant_reg_key = self.reg_key.parent().add_leaf('content')
        tds = creator_fn(variant_reg_key, [], 'content', properties['content'], type_registry)
        if len(tds) != 1 or not isinstance(tds[0], VariantAlias):
            raise ValueError(f"Extended enum property 'content' must be a variant: {properties['content']}")
        self.content_variant = tds[0]

    def dict(self):
        return {
            **super().dict(),
            "type_enum": self.type_enum.members,
            "content_variant": [mem_t_def.dict() for mem_t_def in self.content_variant.member_type_defs],
        }
