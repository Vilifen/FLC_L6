from .scan_error import ScanError
from .error_codes import ERROR_CODES
from .token_types import TokenType


class ParseStack:
    def __init__(self):
        self.stack = []

    def push(self, node):
        self.stack.append(node)

    def pop(self):
        if self.stack:
            return self.stack.pop()
        return None

    def top(self):
        if self.stack:
            return self.stack[-1]
        return None


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.stack = ParseStack()
        self.body_had_error = False

    def parse(self):
        self.pos = 0
        self.errors = []
        self.body_had_error = False
        self._skip_ws()
        self.parse_start()
        return self.errors

    def parse_start(self):
        self._skip_ws()
        if not self._accept(TokenType.KEYWORD, "while"):
            self._error("Ожидалось ключевое слово 'while'")

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, "("):
            self._error("Ожидалась '(' после while")

        self._skip_ws()
        self.parse_condition()

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, ")"):
            self._error("Ожидалась ')' после условия while")

        self._skip_ws()
        if not self._accept(TokenType.SEPARATOR, "{"):
            self._error("Ожидался '{' после while(...)", advance=False)

        self._skip_ws()
        self.parse_body()

        # Если в теле была ошибка — НЕ продолжаем разбор структуры
        if self.body_had_error:
            return

        self._skip_ws()
        if self._eof() or self.tokens[self.pos].value != "}":
            self._error("Ожидался '}' после тела цикла")
            return

        self.pos += 1
        self._skip_ws()

        if self._eof() or not self._accept(TokenType.SEPARATOR, ";"):
            self._error("Ожидался ';' после блока while")

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
            return

        self._skip_ws()
        if self._accept(TokenType.NUMBER):
            return

        if self._accept(TokenType.IDENTIFIER):
            return

        self._error("Ожидалось число или переменная после реляционной операции")

    def parse_var(self):
        self._skip_ws()
        if not self._accept(TokenType.IDENTIFIER):
            self._error("Ожидалась переменная вида $id")
            return

        tok = self.tokens[self.pos - 1]
        if not tok.value.startswith("$"):
            self._error("Ожидалась переменная вида $id", advance=True)

    def parse_body(self):
        self._skip_ws()

        if self._eof() or self.tokens[self.pos].value == "}":
            self.body_had_error = True
            self._error("Тело цикла не может быть пустым", advance=False)
            return

        while not self._eof() and self.tokens[self.pos].value != "}":

            if self.tokens[self.pos].type != TokenType.IDENTIFIER:
                self.body_had_error = True
                self._error("Ожидалась переменная вида $id")
                return

            self.parse_var()

            self._skip_ws()
            if not (self._accept(TokenType.OPERATOR, "++") or self._accept(TokenType.OPERATOR, "--")):
                self.body_had_error = True
                self._error("Ожидался оператор ++ или --")
                return

            self._skip_ws()
            if not self._accept(TokenType.SEPARATOR, ";"):
                self.body_had_error = True
                self._error("Ожидался ';' после оператора ++/--")
                return

            self._skip_ws()

    def _accept(self, ttype, value=None):
        if self._eof():
            return False
        tok = self.tokens[self.pos]
        if tok.type == ttype and (value is None or tok.value == value):
            self.pos += 1
            return True
        return False

    def _error(self, msg, advance=True):
        if self._eof():
            tok = self.tokens[-1]
        else:
            tok = self.tokens[self.pos]
        code = ERROR_CODES["INVALID_STRUCTURE"]
        self.errors.append(ScanError(code, msg, tok.line, tok.column, tok.value))
        if advance and not self._eof():
            self.pos += 1

    def _skip_ws(self):
        while not self._eof() and self.tokens[self.pos].type == TokenType.WHITESPACE:
            self.pos += 1

    def _eof(self):
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF
