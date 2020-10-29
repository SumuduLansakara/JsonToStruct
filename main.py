import json

from cpp_code_generator import CodeGenerator
from schema_parser import SchemaParser


def start():
    parser = SchemaParser()

    build_order = [
        ('core', 'common'),
        # ('triggerBindingConfiguration', 'configurations'),
        # ('triggerConfiguration', 'configs')
    ]

    for schema, namespace in build_order:
        with open(f"sample_schema/{schema}.json") as j_file:
            schema_def = json.load(j_file)
            parser.parse_root_level('#/definitions', namespace, schema_def["definitions"])

    code_gen = CodeGenerator()
    code_gen.generate(parser.type_registry)


if __name__ == '__main__':
    start()
