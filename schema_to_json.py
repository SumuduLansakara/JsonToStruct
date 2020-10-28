import json

object_cache = {}


def get_sample_value(prop_def: dict):
    if "type" not in prop_def:
        raise ValueError(f"Property definition without type: {prop_def}")

    sample_values = {
        "integer": 1,
        "number": 1.2,
        "string": "hello",
        "boolean": True
    }
    value_type = prop_def['type']
    if value_type == "array":
        if "items" not in prop_def:
            raise ValueError("Array definition without items")
        return generate_array(prop_def["items"])
    if value_type not in sample_values:
        raise ValueError(f"Unhandled value type: {value_type}")
    return sample_values[value_type]


def generate_array(arr_def: dict) -> list:
    if "type" in arr_def:
        return [get_sample_value(arr_def)]
    if "anyOf" in arr_def:
        content = []
        for e in arr_def["anyOf"]:
            content.append(get_sample_value(e))
        return content

    raise ValueError(f"Unsupported array item type: {arr_def}")


def generate_property(name: str, prop_def: dict) -> dict:
    if "$ref" in prop_def:
        return {name: {}}

    if "type" not in prop_def:
        raise ValueError(f"Property without type: {name} [{prop_def}]")

    if prop_def["type"] == "object":
        return {name: generate_object(prop_def)}

    return {name: get_sample_value(prop_def)}


def generate_properties(prop_defs: dict) -> dict:
    props = {}
    for k, v in prop_defs.items():
        props.update(generate_property(k, v))
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

    return generate_properties(obj_def["properties"])


def start():
    with open('sample_definition1.json') as json_file:
        data = json.load(json_file)
        sample_json = generate_object(data)

    print(json.dumps(sample_json, indent=4))


start()
