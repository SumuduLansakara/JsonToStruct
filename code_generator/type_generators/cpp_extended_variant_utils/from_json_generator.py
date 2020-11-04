from code_generator.line_buffer import LineBuffer, IndentedBlock
from schema_parser.type_defs.extended_variant import ExtendedVariant
from schema_parser.type_registry import TypeRegistry


class FromJsonWriter:
    buffer: LineBuffer
    type_registry: TypeRegistry
    container_struct: ExtendedVariant

    def __init__(self, buffer: LineBuffer, type_registry: TypeRegistry, container_struct: ExtendedVariant):
        self.buffer = buffer
        self.type_registry = type_registry
        self.container_struct = container_struct

    def write_function(self):
        self.buffer.append(f"void FromJson({self.container_struct.type_name}& m, nlohmann::json const& j)")
        self.buffer.append("{")
        with IndentedBlock(self.buffer):
            self._write_body()
        self.buffer.append("}")

    def _write_body(self):
        self.buffer.append(f'switch(j.at("type").get<{self.container_struct.type_name}::Type>())')
        self.buffer.append('{')
        with IndentedBlock(self.buffer):
            self.buffer.append('// TODO: add missing cases')
            self.buffer.append(
                'default: throw std::runtime_error(std::string() + "Unexpected member type: " + j.at("type"))')
        self.buffer.append('}')
