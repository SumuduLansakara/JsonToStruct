from code_generator.cpp_code_generator import CodeGenerator
from schema_parser.schema_batch_parser import SchemaBatchParser


def start():
    batch_parser = SchemaBatchParser()
    batch_parser.set_dir_offset("sample_schema")
    batch_parser.add_schema_file('test.json', ['lui', 'common'])

    # batch_parser.add_schema_file('triggerConfiguration.json', 'configs')
    batch_parser.set_dir_offset("sample_schema/riedel2")

    batch_parser.parse(['core', 'messages'])

    code_gen = CodeGenerator(batch_parser.type_registry, 'include', 'src')
    code_gen.generate_headers()
    code_gen.generate_sources()


if __name__ == '__main__':
    start()
