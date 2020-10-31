from code_generator.cpp_code_generator import CodeGenerator
from schema_parser.schema_batch_parser import SchemaBatchParser


def start():
    batch_parser = SchemaBatchParser()
    batch_parser.set_dir_offset("sample_schema")
    batch_parser.add_schema_file('test.json', 'common')
    batch_parser.add_schema_file('triggerBindingConfiguration.json', 'configs')
    # batch_parser.add_schema_file('triggerConfiguration.json', 'configs')
    batch_parser.parse()

    code_gen = CodeGenerator(batch_parser.type_registry)
    code_gen.generate()


if __name__ == '__main__':
    start()
