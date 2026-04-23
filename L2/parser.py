from .scan_error import ScanError
from .error_codes import ERROR_CODES
from .token_types import TokenType


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.stop_parsing = False

    def parse(self, scanner_errors=None):
        self.pos = 0
        self.errors = scanner_errors[:] if scanner_errors else []
        self.stop_parsing = False

        self._skip_ws()
        while not self._eof() and not self.stop_parsing:
            self.parse_start()
            self._skip_ws()

        lex_error_lines = {e.line for e in self.errors if e.code == ERROR_CODES["INVALID_CHAR"]}
        self.errors = [
            e for e in self.errors
            if not (e.code == ERROR_CODES["INVALID_STRUCTURE"] and e.line in lex_error_lines)
        ]

        return self.errors

    def _error(self, msg, custom_tok=None):
        if self.stop_parsing:
            return

        if custom_tok:
            tok = custom_tok
        elif self._eof():
            tok = self.tokens[-1] if len(self.tokens) > 0 else None
        else:
            tok = self.tokens[self.pos]

        if tok:
            if tok.type == TokenType.UNKNOWN:
                return

            line = tok.line
            col = tok.column
            if self._eof() and not custom_tok:
                col += len(tok.value)
                val = ""
            else:
                val = tok.value

            self.errors.append(
                ScanError(ERROR_CODES["INVALID_STRUCTURE"], f"Ошибка: {msg}", line, col, val))

    def _match_with_recovery(self, expected_vals, error_msg, allowed_brackets=None):
        self._skip_extra_brackets(allowed_brackets)
        if self._eof():
            self._error(f"Ожидалось: {error_msg}")
            return False

        tok = self.tokens[self.pos]
        if tok.value in expected_vals or tok.type in expected_vals:
            self.pos += 1
            return True

        self._error(f"Ожидалось: {error_msg}, получено '{tok.value}'")
        return False

    def _skip_extra_brackets(self, allowed_brackets=None):
        if allowed_brackets is None:
            allowed_brackets = []

        self._skip_ws()
        while not self._eof():
            tok = self.tokens[self.pos]
            if tok.value in ["(", ")"] and tok.value not in allowed_brackets:
                self._error(f"недопустимый символ '{tok.value}'")
                self.pos += 1
                self._skip_ws()
            else:
                break

    def parse_start(self):
        if self._eof(): return
        self._skip_extra_brackets(allowed_brackets=["while"])

        tok = self.tokens[self.pos]
        if tok.value != "while":
            self._error("ключевое слово 'while'")
            if tok.value not in ["(", "{", "$"]:
                self.pos += 1
        else:
            self.pos += 1
        self.parse_keyword_while()

    def parse_keyword_while(self):
        if self._match_with_recovery(["("], "'('", allowed_brackets=["("]):
            self.parse_left_brace()
        else:
            self.parse_left_brace()

    def parse_left_brace(self):
        self._skip_extra_brackets(allowed_brackets=["$"])
        if not self._eof():
            tok = self.tokens[self.pos]
            if tok.type == TokenType.IDENTIFIER and tok.value.startswith("$"):
                self.pos += 1
            else:
                self._error("переменная вида '$id'")
                if tok.type == TokenType.IDENTIFIER: self.pos += 1
        else:
            self._error("переменная вида '$id'")
        self.parse_expression_operator()

    def parse_expression_operator(self):
        ops = ["<", ">", "==", ">=", "<=", "!="]
        self._match_with_recovery(ops, "оператор сравнения")
        self.parse_expression()

    def parse_expression(self):
        self._skip_extra_brackets()
        if self._eof():
            self._error("число или переменная '$id'")
            return

        tok = self.tokens[self.pos]
        if tok.type == TokenType.NUMBER or (tok.type == TokenType.IDENTIFIER and tok.value.startswith("$")):
            self.pos += 1
            self.parse_tail()
        else:
            self._error("число или переменная '$id'")
            if tok.value not in ["||", "&&", ")", "{"]:
                self.pos += 1
            self.parse_tail()

    def parse_tail(self):
        self._skip_extra_brackets(allowed_brackets=["||", "&&", ")"])
        if self._eof():
            self._error("')'")
            return

        tok = self.tokens[self.pos]
        if tok.value in ["||", "&&"]:
            self.pos += 1
            self.parse_left_brace()
        elif tok.value == ")":
            self.pos += 1
            self.parse_right_brace()
        else:
            self._error("')' или логический оператор")
            if tok.value != "{": self.pos += 1
            self.parse_right_brace()

    def parse_right_brace(self):
        self._match_with_recovery(["{"], "'{'", allowed_brackets=["{"])
        self.parse_left_curly_brace()

    def parse_left_curly_brace(self):
        while not self._eof():
            self._skip_extra_brackets(allowed_brackets=["}", "$"])
            if self._eof(): break
            tok = self.tokens[self.pos]

            if tok.value == "}":
                self.pos += 1
                self.parse_final_semicolon()
                return

            if tok.type == TokenType.IDENTIFIER and tok.value.startswith("$"):
                self.pos += 1
                self._skip_extra_brackets(allowed_brackets=["++", "--"])
                self.parse_id_in_operator()
                self._skip_extra_brackets(allowed_brackets=[";", "}"])

                if not self._eof() and self.tokens[self.pos].value == ";":
                    self.pos += 1
            else:
                if tok.value == "while": return
                self._error("инструкция ($id++)")
                self.pos += 1

        self._error("'}'")
        self.parse_final_semicolon()

    def parse_id_in_operator(self):
        self._match_with_recovery(["++", "--"], "++ или --", allowed_brackets=["++", "--"])

    def parse_final_semicolon(self):
        self._match_with_recovery([";"], "';'", allowed_brackets=[";"])

    def _skip_ws(self):
        while not self._eof() and self.tokens[self.pos].type == TokenType.WHITESPACE:
            self.pos += 1

    def _eof(self):
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF