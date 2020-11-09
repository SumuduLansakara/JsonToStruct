from code_generator.cpp_code_generator import CodeGenerator
from schema_parser.schema_batch_parser import SchemaBatchParser


def start():
    batch_parser = SchemaBatchParser()

    batch_parser.set_input_dir("example/schemas")
    batch_parser.add_schema_file('simple_alias.json')
    batch_parser.add_schema_file('array_alias.json')
    batch_parser.add_schema_file('struct.json')
    batch_parser.add_schema_file('type_reference.json')
    batch_parser.add_schema_file('extended_variant.json')

    batch_parser.parse(['core'])

    code_gen = CodeGenerator(batch_parser.type_registry, 'temp_generated', 'include', 'src')
    code_gen.generate_code()


if __name__ == '__main__':
    start()
