import json


class CodeGenerator:
    def generate(self, struct_definitions):
        for name, struct_def in struct_definitions.items():
            self.generate_struct(name, struct_def)

    @staticmethod
    def generate_struct(name: str, struct_def: dict):
        print(f"struct {name} : ISerializable")
        print("{")
        for prop in struct_def["properties"]:
            print(f"    {prop['type']} {prop['name']};")
        print()
        print("    [[nodiscard]] std::string ToJson() const override;")
        print("    void FromJson(const std::string&) override;")
        print("}")


class SchemaDecoder:
    def __init__(self):
        self._struct_defs = {}
        self._reference_registry = {}

    @property
    def struct_definitions(self) -> dict:
        return self._struct_defs

    def load_from_file(self, file_path: str):
        with open(file_path) as json_file:
            data = json.load(json_file)
            self.load(data)

    def load(self, data: dict):
        struct_def = self.generate_object_definition(data)
        self._struct_defs["Struct"] = struct_def

    def generate_object_definition(self, obj_def: dict) -> dict:
        if "type" not in obj_def:
            raise ValueError(f"Invalid schema: {obj_def}")

        if obj_def["type"] != "object":
            raise ValueError(f"Invalid object type: {obj_def}")

        if "properties" not in obj_def:
            raise ValueError(f"Object without properties: {obj_def}")

        if "$id" in obj_def:
            self._reference_registry[obj_def["$id"]] = obj_def

        if "$schema" in obj_def:
            pass

        return {"properties": self.generate_properties(obj_def["properties"])}

    def generate_properties(self, prop_defs: dict) -> list:
        props = []
        for k, v in prop_defs.items():
            props.append(self.generate_property_definition(k, v))
        return props

    def generate_property_definition(self, name: str, prop_def: dict) -> dict:
        if "type" not in prop_def:
            raise ValueError(f"Property without type: {name} [{prop_def}]")

        if "$ref" in prop_def:
            raise NotImplementedError("references are not yet supported")

        if prop_def["type"] == "object":
            obj_type = name.capitalize()
            self._struct_defs[obj_type] = self.generate_object_definition(prop_def)
            return {
                "name": name,
                "type": obj_type
            }

        return {
            "name": name,
            "type": self.get_prop_type(prop_def)
        }

    def get_prop_type(self, prop_def: dict) -> str:
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
            return self.generate_array(prop_def["items"])
        if value_type not in basic_types:
            raise ValueError(f"Unhandled value type: {value_type}")
        return basic_types[value_type]

    def generate_array(self, arr_def: dict) -> str:
        if "type" in arr_def:  # arrays are implemented using vectors
            return f"std::vector<{self.get_prop_type(arr_def)}>"

        if "oneOf" in arr_def:  # oneOf types are implemented as variants
            # TODO: handle enum generation case
            types = []
            for e in arr_def["oneOf"]:
                types.append(self.get_prop_type(e))

            return "std::variant<" + ", ".join(types) + ">"

        raise TypeError(f"Unsupported array item type: {arr_def}")


if __name__ == '__main__':
    sd = SchemaDecoder()
    sd.load_from_file("sample_schema/sample_definition1.json")

    cg = CodeGenerator()
    cg.generate(sd.struct_definitions)
