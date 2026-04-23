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
        self.errors = []
        self.stop_parsing = False

        while not self._eof() and not self.stop_parsing:
            self._skip_ws()
            if self._eof(): break
            self.parse_start()

        return self.errors

    def _error(self, msg, custom_tok=None):
        if self.stop_parsing: return
        tok = custom_tok if custom_tok else (self.tokens[self.pos] if not self._eof() else self.tokens[-1])
        if not tok: return

        self.errors.append(ScanError(
            ERROR_CODES["INVALID_STRUCTURE"],
            f"Ошибка: {msg}",
            tok.line, tok.column, tok.value
        ))

    def _match_with_recovery(self, expected_vals, error_msg, allowed_brackets=None):
        self._skip_extra_brackets(allowed_brackets)
        if self._eof():
            self._error(f"Ожидалось: {error_msg}")
            return False

        tok = self.tokens[self.pos]
        if tok.value in expected_vals or tok.type in expected_vals:
            self.pos += 1
            return True

        self._error(error_msg)
        self.pos += 1
        return False

    def _skip_extra_brackets(self, allowed_brackets=None):
        if allowed_brackets is None: allowed_brackets = []
        self._skip_ws()
        while not self._eof():
            tok = self.tokens[self.pos]
            if tok.value in ["(", ")", "{", "}", ";"] and tok.value not in allowed_brackets:
                self._error(f"недопустимый символ '{tok.value}'")
                self.pos += 1
                self._skip_ws()
            else:
                break

    def parse_start(self):
        if self._eof(): return
        tok = self.tokens[self.pos]
        if tok.value != "while":
            self._error("ключевое слово 'while'")
            # Синхронизация: пропуск до начала параметров или тела
            while not self._eof() and self.tokens[self.pos].value not in ["(", "{"]:
                self.pos += 1
            if self._eof() or self.tokens[self.pos].value == "{": return
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
                self.pos += 1
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
            self.pos += 1
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