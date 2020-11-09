from typing import List

from code_generator.line_buffer import LineBuffer


class HeaderCodeWriter:
    include_headers: List[str]

    def __init__(self, buffer: LineBuffer):
        self.buffer = buffer
        self.include_headers = []

    def str(self):
        final_buffer = LineBuffer(0)
        final_buffer.append('#pragma once')
        if self.include_headers:
            final_buffer.new_line()
            for include in self.include_headers:
                final_buffer.append(f"#include <{include}>")
        final_buffer.new_line()
        final_buffer.append_buffer(self.buffer)
        return final_buffer.str()
