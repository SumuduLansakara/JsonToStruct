import json


def add_prop(parent, prop_name, prop_content):
    parent[prop_name] = prop_content


def get_type(content) -> str:
    if isinstance(content, bool):
        return "boolean"
    if isinstance(content, int):
        return "integer"
    if isinstance(content, str):
        return "string"
    if isinstance(content, list):
        return "array"
    if isinstance(content, float):
        return "number"
    if isinstance(content, dict):
        return "object"
    raise ValueError(f"Unhandled type: {type(content)} [{content}]")


def generate_array_schema(arr: list) -> dict:
    e_types = {}  # ordered dict has to be used because sets are not ordered
    for e in arr:
        e_types[get_type(e)] = True  # value is not needed

    if len(e_types) == 0:
        return {"type": "string"}

    if len(e_types) == 1:
        return {"type": list(e_types.keys())[0]}

    return {"anyOf": list(e_types.keys())}


def generate_object_schema(obj: dict) -> dict:
    properties = {}

    for i, v in obj.items():
        c_type = get_type(v)
        properties[i] = {
            "type": c_type,
        }
        if c_type == "array":
            properties[i]["items"] = generate_array_schema(v)
        if c_type == "object":
            properties[i]["properties"] = generate_object_schema(v)

    return properties


def start():
    schema = {
        "$schema": "http://json-schema.org/draft-07/schema",
        "$id": "http://example.com/root.json",
        "type": "object",
        "description": "",
        "properties": {}
    }
    with open('../sample_json/sample_json1.json') as json_file:
        data = json.load(json_file)
        schema["properties"] = generate_object_schema(data)

    print(json.dumps(schema, indent=4))


start()
