from __future__ import annotations

from typing import List

UNIT_INDENT = ' ' * 4


class LineBuffer:
    _lines: List[str]
    _indent_level: int
    _prefix: str

    def __init__(self, indent: int, *lines):
        self._lines = list(lines)
        self._indent_level = indent
        self._prefix = self.get_indent_prefix(self._indent_level)

    @staticmethod
    def get_indent_prefix(indent_level: int) -> str:
        if indent_level < 0:
            raise ValueError("Indentation level can't be negative")
        return UNIT_INDENT * indent_level

    def set_indentation(self, level: int):
        self._indent_level = level
        self._prefix = self.get_indent_prefix(self._indent_level)

    def indent_up(self, units=1):
        self._indent_level += units
        self._prefix = self.get_indent_prefix(self._indent_level)

    def indent_down(self, units=1):
        self._indent_level -= units
        self._prefix = self.get_indent_prefix(self._indent_level)

    def prepend(self, *lines):
        for line in reversed(lines):
            self._lines.insert(0, line)

    def append(self, line: str):
        self._lines.append(self._prefix + line)

    def append_buffer(self, buffer: LineBuffer):
        self._lines.extend([self._prefix + line for line in buffer._lines])

    def pop(self):
        self._lines.pop()

    def new_line(self):
        self._lines.append("")

    def str(self, indent_offset=0):
        indent_prefix = self.get_indent_prefix(indent_offset)
        return '\n'.join([indent_prefix + line for line in self._lines])

    def __len__(self):
        return len(self._lines)


class IndentedBlock:
    line_buffer: LineBuffer

    def __init__(self, line_buffer: LineBuffer):
        self.line_buffer = line_buffer

    def __enter__(self):
        self.line_buffer.indent_up()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.line_buffer.indent_down()
