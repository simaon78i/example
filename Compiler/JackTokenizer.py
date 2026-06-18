"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported License.
"""
import typing


class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.
    
    # Jack Language Grammar
    ...
    """

    KEYWORDS = {
        "class", "constructor", "function", "method", "field",
        "static", "var", "int", "char", "boolean", "void",
        "true", "false", "null", "this",
        "let", "do", "if", "else", "while", "return"
    }

    SYMBOLS = set('{}()[].,;+-*/&|<>=~^#')

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        self.source = input_stream.read()
        self.length = len(self.source)
        self.index = 0
        self.current_token = None

    # -------------------------
    # helpers
    # -------------------------

    def _skip_whitespace_and_comments(self):
        while self.index < self.length:
            ch = self.source[self.index]

            if ch.isspace():
                self.index += 1
                continue

            if self.source.startswith("//", self.index):
                while self.index < self.length and self.source[self.index] != "\n":
                    self.index += 1
                continue

            if self.source.startswith("/*", self.index):
                end = self.source.find("*/", self.index + 2)
                if end == -1:
                    self.index = self.length
                else:
                    self.index = end + 2
                continue

            break

    def _read_string(self):
        self.index += 1  # skip opening "
        start = self.index

        while self.index < self.length and self.source[self.index] != '"':
            self.index += 1

        value = self.source[start:self.index]
        self.index += 1  # skip closing "
        return value

    def _read_number_or_identifier(self):
        start = self.index

        while (
            self.index < self.length and
            (self.source[self.index].isalnum() or self.source[self.index] == "_")
        ):
            self.index += 1

        return self.source[start:self.index]

    # -------------------------
    # API
    # -------------------------

    def has_more_tokens(self) -> bool:
        temp = self.index
        self._skip_whitespace_and_comments()
        result = self.index < self.length
        self.index = temp
        return result

    def advance(self) -> None:
        self._skip_whitespace_and_comments()

        if self.index >= self.length:
            self.current_token = None
            return

        ch = self.source[self.index]

        if ch in self.SYMBOLS:
            self.current_token = ch
            self.index += 1
            return

        if ch == '"':
            self.current_token = '"' + self._read_string() + '"'
            return

        self.current_token = self._read_number_or_identifier()

    def token_type(self) -> str:
        if self.current_token in self.KEYWORDS:
            return "KEYWORD"
        if self.current_token in self.SYMBOLS:
            return "SYMBOL"
        if self.current_token.isdigit():
            return "INT_CONST"
        elif self.current_token.startswith('"') and self.current_token.endswith('"'):
            return "STRING_CONST"
        return "IDENTIFIER"

    def keyword(self) -> str:
        return self.current_token.upper()

    def symbol(self) -> str:
        return self.current_token

    def identifier(self) -> str:
        return self.current_token

    def int_val(self) -> int:
        return int(self.current_token)

    def string_val(self) -> str:
        return self.current_token[1:-1]

    # -------------------------
    # XML OUTPUT (Project 10)
    # -------------------------

    def _escape(self, token: str) -> str:
        if token == "<":
            return "&lt;"
        if token == ">":
            return "&gt;"
        if token == "&":
            return "&amp;"
        return token

    def write_xml_tokens(self, output_stream: typing.TextIO) -> None:
        """
        Writes tokens in XML format:
        <tokens> ... </tokens>
        """
        output_stream.write("<tokens>\n")

        saved_index = self.index
        self.index = 0

        while True:
            self._skip_whitespace_and_comments()

            if self.index >= self.length:
                break

            ch = self.source[self.index]

            if ch in self.SYMBOLS:
                token = ch
                ttype = "symbol"
                self.index += 1

            elif ch == '"':
                token = self._read_string()
                ttype = "stringConstant"

            else:
                token = self._read_number_or_identifier()

                if token in self.KEYWORDS:
                    ttype = "keyword"
                elif token.isdigit():
                    ttype = "integerConstant"
                else:
                    ttype = "identifier"

            output_stream.write(
                f"<{ttype}> {self._escape(token)} </{ttype}>\n"
            )

        output_stream.write("</tokens>\n")

        self.index = saved_index