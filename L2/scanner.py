from .token_types import TokenType
from .token import Token
from .scan_error import ScanError
from .error_codes import ERROR_CODES

class Scanner:
    KEYWORDS = {"while"}
    OPERATORS = {"++", "--", "<=", ">=", "==", "!=", "&&", "||", "<", ">", "_"}
    SEPARATORS = {"(", ")", "{", "}", ";"}

    def __init__(self):
        self.text = ""
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = 0
        self.tokens = []
        self.errors = []

    def scan(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.length = len(text)
        self.tokens = []
        self.errors = []

        while not self._eof():
            ch = self._cur()

            if ch in " \t\r\n":
                self._add(TokenType.WHITESPACE, ch)
                self._advance()
            elif ch == "$":
                self._consume_identifier()
            elif ch.isalpha() or ch == "_":
                self._consume_word()
            elif ch.isdigit():
                self._consume_number()
            elif ch in self.SEPARATORS:
                self._add(TokenType.SEPARATOR, ch)
                self._advance()
            elif self._starts_operator():
                self._consume_operator()
            else:
                self._consume_unknown()

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.col))
        return self.tokens, self.errors

    def _eof(self):
        return self.pos >= self.length

    def _cur(self):
        return "" if self._eof() else self.text[self.pos]

    def _peek(self, offset=1):
        idx = self.pos + offset
        return "" if idx >= self.length else self.text[idx]

    def _advance(self, steps=1):
        for _ in range(steps):
            if self._eof(): return
            ch = self.text[self.pos]
            self.pos += 1
            if ch == "\n":
                self.line += 1
                self.col = 1
            else:
                self.col += 1

    def _add(self, ttype, value):
        self.tokens.append(Token(ttype, value, self.line, self.col))

    def _is_separator_or_space_or_op_start(self, ch):
        if ch == "": return True
        if ch.isspace(): return True
        if ch in self.SEPARATORS: return True
        if (ch + self._peek()) in self.OPERATORS or ch in self.OPERATORS: return True
        return False

    def _consume_identifier(self):
        start_line, start_col = self.line, self.col
        value = self._cur()
        self._advance()
        content = ""
        while not self._eof() and not self._is_separator_or_space_or_op_start(self._cur()):
            content += self._cur()
            self._advance()
        full_value = value + content
        if not content or not all(c.isalnum() or c == '_' for c in content):
            self.tokens.append(Token(TokenType.UNKNOWN, full_value, start_line, start_col))
        else:
            self.tokens.append(Token(TokenType.IDENTIFIER, full_value, start_line, start_col))

    def _consume_word(self):
        start_line, start_col = self.line, self.col
        value = ""
        while not self._eof() and not self._is_separator_or_space_or_op_start(self._cur()):
            value += self._cur()
            self._advance()
        ttype = TokenType.KEYWORD if value in self.KEYWORDS else TokenType.IDENTIFIER
        self.tokens.append(Token(ttype, value, start_line, start_col))

    def _consume_number(self):
        start_line, start_col = self.line, self.col
        value = ""
        while not self._eof() and self._cur().isdigit():
            value += self._cur()
            self._advance()
        self.tokens.append(Token(TokenType.NUMBER, value, start_line, start_col))

    def _starts_operator(self):
        return (self._cur() + self._peek()) in self.OPERATORS or self._cur() in self.OPERATORS

    def _consume_operator(self):
        start_line, start_col = self.line, self.col
        op2 = self._cur() + self._peek()
        if op2 in self.OPERATORS:
            self.tokens.append(Token(TokenType.OPERATOR, op2, start_line, start_col))
            self._advance(2)
        else:
            self.tokens.append(Token(TokenType.OPERATOR, self._cur(), start_line, start_col))
            self._advance(1)

    def _consume_unknown(self):
        start_line, start_col = self.line, self.col
        val = self._cur()
        self._advance()
        self.tokens.append(Token(TokenType.UNKNOWN, val, start_line, start_col))