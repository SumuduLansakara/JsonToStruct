from code_generator.line_buffer import LineBuffer, IndentedBlock
from schema_parser.type_defs.extended_variant import ExtendedVariant
from schema_parser.type_registry import TypeRegistry


class ToJsonWriter:
    buffer: LineBuffer
    type_registry: TypeRegistry
    container_struct: ExtendedVariant

    def __init__(self, buffer: LineBuffer, type_registry: TypeRegistry, container_struct: ExtendedVariant):
        self.buffer = buffer
        self.type_registry = type_registry
        self.container_struct = container_struct

    def write_function(self):
        self.buffer.append(f"nlohmann::json ToJson({self.container_struct.type_name} const& m)")
        self.buffer.append("{")
        with IndentedBlock(self.buffer):
            self._write_body()
        self.buffer.append("}")
        self.buffer.new_line()

    def _write_body(self):
        self.buffer.append('nlohmann::json res {')
        with IndentedBlock(self.buffer):
            self.buffer.append('{ "type": m.index() },')
        self.buffer.append('};')
        self.buffer.append('auto& content = res["content"];')
        self.buffer.append('// TODO: load content')
        self.buffer.append('return res;')
