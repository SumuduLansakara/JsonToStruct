from typing import Dict, List

from schema_parser.reg_key import RegKey
from schema_parser.type_defs.type_def_base import TypeDefBase
from schema_parser.type_registry import TypeRegistry
from schema_parser.utils.type_loader import get_object_type


def create_typedef(reg_key: RegKey, namespaces: List[str], name: str, definition: Dict, type_registry: TypeRegistry) \
        -> List[TypeDefBase]:
    obj_type_meta = get_object_type(definition)
    t_def = obj_type_meta(namespaces, name, reg_key)
    dependent_types = t_def.parse(definition, create_typedef, type_registry)

    res: List[TypeDefBase] = []
    if dependent_types:
        res.extend(dependent_types)
    res.append(t_def)  # last element is the target type
    return res
