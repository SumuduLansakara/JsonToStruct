import json

from schema_parser import SchemaParser


def start():
    parser = SchemaParser()

    build_order = [
        'triggerBindingConfiguration',
        'triggerConfiguration'
    ]

    for schema in build_order:
        with open(f"sample_schema/{schema}.json") as j_file:
            schema_def = json.load(j_file)
            parser.parse_root_level('#/definitions', schema_def["definitions"])

    for k, v in parser.type_registry:
        print(f"{k} : {v}")


if __name__ == '__main__':
    start()
