from typing import Dict, Union

from schema_parser import configs


def read_custom_attrib(schema_def: Dict, name: str, default: Union[Dict, str, None] = None) -> Union[Dict, str, None]:
    attr_name = configs.CUSTOM_ATTR_PREFIX + name
    if attr_name in schema_def:
        return schema_def[attr_name]
    return default


def is_custom_attr(name: str) -> bool:
    return name.startswith(configs.CUSTOM_ATTR_PREFIX)


def is_ignored_definition(schema_def: Dict[str, Dict]) -> bool:
    return configs.CUSTOM_ATTR_PREFIX + 'ignore' in schema_def and schema_def[configs.CUSTOM_ATTR_PREFIX + 'ignore']
