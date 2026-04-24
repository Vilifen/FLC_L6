from .token_types import TokenType
from .scan_error import ScanError
from .error_codes import ErrorCode


class Parser:
    def __init__(self, tokens):
        self.tokens = [t for t in tokens if t.type != TokenType.WHITESPACE]
        self.pos = 0
        self.errors = []

    def parse(self):
        while self.pos < len(self.tokens) and self._current_token().type != TokenType.EOF:
            current = self._current_token()

            if current.type == TokenType.NEWLINE:
                self.pos += 1
                continue

            if current.type == TokenType.ERROR:
                self._skip_to_next_line()
                continue

            self.E()

            if self.pos < len(self.tokens) and self._current_token().type not in (TokenType.NEWLINE, TokenType.EOF):
                if self._current_token().type != TokenType.ERROR:
                    self._record_error("Неожиданный токен", ErrorCode.UNEXPECTED_TOKEN)
                self._skip_to_next_line()

        return self.errors

    def _skip_to_next_line(self):
        while self.pos < len(self.tokens) and self._current_token().type not in (TokenType.NEWLINE, TokenType.EOF):
            self.pos += 1

    def _current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def _match(self, expected_type):
        if self._current_token().type == expected_type:
            self.pos += 1
            return True
        return False

    def _record_error(self, message, code):
        token = self._current_token()
        self.errors.append(ScanError(code, message, token.line, token.column, token.value))

    def E(self):
        self.T()
        self.A()

    def T(self):
        self.F()
        self.B()

    def A(self):
        if self._current_token().type in (TokenType.PLUS, TokenType.MINUS):
            self.pos += 1
            self.T()
            self.A()

    def B(self):
        if self._current_token().type in (TokenType.MUL, TokenType.DIV, TokenType.MOD):
            self.pos += 1
            self.F()
            self.B()

    def F(self):
        current = self._current_token()
        if current.type == TokenType.NUM:
            self._match(TokenType.NUM)
        elif current.type == TokenType.ID:
            self._match(TokenType.ID)
        elif current.type == TokenType.LPAREN:
            self._match(TokenType.LPAREN)
            self.E()
            if not self._match(TokenType.RPAREN):
                self._record_error("Отсутствует закрывающая скобка", ErrorCode.MISSING_RPAREN)
        elif current.type == TokenType.ERROR:
            pass
        else:
            self._record_error("Ожидалось число, переменная или открывающая скобка", ErrorCode.UNEXPECTED_TOKEN)
            self.pos += 1