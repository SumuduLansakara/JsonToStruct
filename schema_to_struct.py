import json

object_cache = {}
struct_cache = {}


def get_prop_type(prop_def: dict):
    if "type" not in prop_def:
        raise ValueError(f"Property definition without type: {prop_def}")

    basic_types = {
        "integer": "std::int64",
        "number": "float",
        "string": "std::string",
        "boolean": "bool"
    }
    value_type = prop_def['type']
    if value_type == "array":
        if "items" not in prop_def:
            raise ValueError("Array definition without items")
        return generate_array(prop_def["items"])
    if value_type not in basic_types:
        raise ValueError(f"Unhandled value type: {value_type}")
    return basic_types[value_type]


def generate_array(arr_def: dict) -> str:
    if "type" in arr_def:
        return f"std::vector<{get_prop_type(arr_def)}>"
    if "oneOf" in arr_def:
        types = []
        for e in arr_def["oneOf"]:
            types.append(get_prop_type(e))

        return "std::variant<" + ", ".join(types) + ">"

    if "anyOf" in arr_def:
        raise TypeError("AnyOf is not supported")

    raise ValueError(f"Unsupported array item type: {arr_def}")


def generate_property(name: str, prop_def: dict) -> dict:
    if "type" not in prop_def:
        raise ValueError(f"Property without type: {name} [{prop_def}]")

    if "$ref" in prop_def:
        raise NotImplementedError("references are not yet supported")

    if prop_def["type"] == "object":
        obj_type = name.capitalize()
        struct_cache[obj_type] = generate_object(prop_def)
        return {
            "name": name,
            "type": obj_type
        }

    return {
        "name": name,
        "type": get_prop_type(prop_def)
    }


def generate_properties(prop_defs: dict) -> list:
    props = []
    for k, v in prop_defs.items():
        props.append(generate_property(k, v))
    return props


def generate_object(obj_def: dict) -> dict:
    if "type" not in obj_def:
        raise ValueError(f"Invalid schema: {obj_def}")

    if obj_def["type"] != "object":
        raise ValueError(f"Invalid object type: {obj_def}")

    if "properties" not in obj_def:
        raise ValueError(f"Object without properties: {obj_def}")

    if "$id" in obj_def:
        object_cache[obj_def["$id"]] = obj_def

    if "$schema" in obj_def:
        pass

    return {"properties": generate_properties(obj_def["properties"])}


def generate_struct_code(name: str, struct_def: dict):
    print(f"struct {name} : ISerializable")
    print("{")
    for prop in struct_def["properties"]:
        print(f"    {prop['type']} {prop['name']};")
    print()
    print("    [[nodiscard]] std::string ToJson() const override;")
    print("    void FromJson(const std::string&) override;")
    print("}")


def start():
    with open('sample_definition1.json') as json_file:
        data = json.load(json_file)
        struct_def = generate_object(data)
        struct_cache["Struct"] = struct_def

    for name, struct_def in struct_cache.items():
        generate_struct_code(name, struct_def)


start()
