from .scan_error import ScanError
from .error_codes import ERROR_CODES
from .token_types import TokenType


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    def parse(self):
        self._skip_ws()
        self.parse_start()
        return self.errors

    def parse_start(self):
        self._skip_ws()
        if not self._accept(TokenType.KEYWORD, "while"):
            self._error("Ожидалось ключевое слово 'while'")
            return

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, "("):
            self._error("Ожидалась '(' после while")
            self._panic_until({")"})

        self._skip_ws()
        self.parse_condition()

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, ")"):
            self._error("Ожидалась ')' после условия while")
            self._panic_until({"{"})

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, "{"):
            self._error("Ожидался '{' после while(...)")
            self._panic_until({"{"})

        self._skip_ws()
        self.parse_body()

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, "}"):
            self._error("Ожидался '}' после тела цикла")
            self._panic_until({"}"})

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, ";"):
            self._error("Ожидался ';' после блока while")
            self._panic_until({";"})

    def parse_condition(self):
        self._skip_ws()
        self.parse_simple_expr()

        self._skip_ws()
        if self._accept(TokenType.OPERATOR, "&&") or self._accept(TokenType.OPERATOR, "||"):
            self._skip_ws()
            self.parse_condition()

    def parse_simple_expr(self):
        self._skip_ws()
        self.parse_var()

        self._skip_ws()
        if not self._accept(TokenType.OPERATOR):
            self._error("Ожидалась реляционная операция (<, >, <=, >=, ==, !=)")
            self._panic_until({")"})
            return

        self._skip_ws()
        if self._accept(TokenType.NUMBER):
            return

        if self._accept(TokenType.IDENTIFIER):
            return

        self._error("Ожидалось число или переменная после реляционной операции")
        self._panic_until({")"})

    def parse_var(self):
        self._skip_ws()
        if not self._accept(TokenType.IDENTIFIER):
            self._error("Ожидалась переменная вида $id")
            self._panic_until({")", "{", ";", "&&", "||"})
            return

    def parse_body(self):
        self._skip_ws()
        self.parse_var()

        self._skip_ws()
        if not (self._accept(TokenType.OPERATOR, "++") or self._accept(TokenType.OPERATOR, "--")):
            self._error("Ожидался оператор ++ или --")
            self._panic_until({";", "}"})
            return

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, ";"):
            self._error("Ожидался ';' после оператора ++/--")
            self._panic_until({"}"})

    def _accept(self, ttype, value=None):
        if self._eof():
            return False
        tok = self.tokens[self.pos]
        if tok.type == ttype and (value is None or tok.value == value):
            self.pos += 1
            return True
        return False

    def _panic_until(self, sync_values):
        while not self._eof():
            tok = self.tokens[self.pos]
            if tok.type == TokenType.SEPARATOR and tok.value in sync_values:
                return
            if tok.value in sync_values:
                return
            self.pos += 1

    def _error(self, msg):
        tok = self.tokens[self.pos]
        code = ERROR_CODES["INVALID_STRUCTURE"]
        self.errors.append(ScanError(code, msg, tok.line, tok.column, tok.value))
        self.pos += 1

    def _skip_ws(self):
        while not self._eof() and self.tokens[self.pos].type == TokenType.WHITESPACE:
            self.pos += 1

    def _eof(self):
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF
