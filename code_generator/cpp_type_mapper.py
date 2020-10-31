_cpp_type_map = {
    "boolean": "bool",
    "integer": "std::int64",
    "number": "float",
    "string": "std::string",
}


def get_cpp_type(type_str: str) -> str:
    if type_str not in _cpp_type_map:
        return type_str
    return _cpp_type_map[type_str]
