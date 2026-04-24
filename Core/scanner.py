from .token_types import TokenType
from .token import Token
from .scan_error import ScanError
from .error_codes import ErrorCode


class Scanner:
    def __init__(self):
        self.text = ""
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.errors = []

    def scan(self, text):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []
        self.errors = []

        operators = {
            '+': TokenType.PLUS, '-': TokenType.MINUS,
            '*': TokenType.MUL, '/': TokenType.DIV,
            '%': TokenType.MOD, '(': TokenType.LPAREN,
            ')': TokenType.RPAREN, '\n': TokenType.NEWLINE
        }

        while self.pos < len(self.text):
            char = self.text[self.pos]

            if char == '\n':
                self._add_token(TokenType.NEWLINE, "\\n")
                self._advance()
            elif char.isspace():
                self._handle_whitespace()
            elif char in operators:
                self._handle_operator(char, operators[char])
            elif char.isdigit():
                self._handle_number()
            elif char == '$':
                self._handle_id()
            else:
                self._handle_unexpected()

        self._add_token(TokenType.EOF, "")
        return self.tokens, self.errors

    def _handle_operator(self, char, type_):
        start_col = self.col
        count = 0
        # Проверяем, не идет ли следом такой же оператор (кроме скобок)
        if char in '+-*/%':
            temp_pos = self.pos
            while temp_pos < len(self.text) and self.text[temp_pos] == char:
                count += 1
                temp_pos += 1

            if count > 1:
                value = char * count
                self.errors.append(ScanError(
                    ErrorCode.UNEXPECTED_CHAR,
                    "Непредвиденная лексема",
                    self.line,
                    start_col,
                    value
                ))
                self.tokens.append(Token(TokenType.ERROR, value, self.line, start_col))
                for _ in range(count):
                    self._advance()
                return

        self._add_token(type_, char)
        self._advance()

    def _handle_unexpected(self):
        start_col = self.col
        value = ""
        stop_chars = {'$', '+', '-', '*', '/', '%', '(', ')', '\n'}

        while self.pos < len(self.text):
            char = self.text[self.pos]
            if char.isspace() or char in stop_chars or char.isdigit():
                break
            value += char
            self._advance()

        if value:
            self.errors.append(ScanError(
                ErrorCode.UNEXPECTED_CHAR,
                "Непредвиденная лексема",
                self.line,
                start_col,
                value
            ))
            self.tokens.append(Token(TokenType.ERROR, value, self.line, start_col))

    def _advance(self):
        if self.pos < len(self.text):
            if self.text[self.pos] == '\n':
                self.line += 1
                self.col = 1
            else:
                self.col += 1
            self.pos += 1

    def _add_token(self, type_, value):
        self.tokens.append(Token(type_, value, self.line, self.col))

    def _handle_whitespace(self):
        while self.pos < len(self.text) and self.text[self.pos].isspace() and self.text[self.pos] != '\n':
            self._advance()

    def _handle_number(self):
        start_col = self.col
        value = ""
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            value += self.text[self.pos]
            self._advance()
        self.tokens.append(Token(TokenType.NUM, value, self.line, start_col))

    def _handle_id(self):
        start_col = self.col
        value = "$"
        self._advance()
        if self.pos < len(self.text) and (self.text[self.pos].isalpha()):
            while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
                value += self.text[self.pos]
                self._advance()
            self.tokens.append(Token(TokenType.ID, value, self.line, start_col))
        else:
            self.errors.append(ScanError(
                ErrorCode.INVALID_ID,
                "Неверный формат идентификатора",
                self.line,
                start_col,
                value
            ))
            self.tokens.append(Token(TokenType.ERROR, value, self.line, start_col))