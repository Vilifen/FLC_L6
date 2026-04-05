from .scan_error import ScanError
from .error_codes import ERROR_CODES
from .token_types import TokenType


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []
        self.stop_parsing = False
        self.consecutive_errors = 0

    def parse(self):
        self.pos = 0
        self.errors = []
        self.stop_parsing = False
        self.consecutive_errors = 0

        self._skip_ws()

        while not self._eof() and not self.stop_parsing:
            self.parse_start()
            self._skip_ws()

        return self.errors

    def _match_with_recovery(self, expected_vals, sync_vals, error_msg):
        if self.stop_parsing:
            return False

        self._skip_ws()
        if self._eof():
            self.consecutive_errors += 1
            if self.consecutive_errors < 2:
                self._error(f"Неожиданный конец файла. Ожидалось: {error_msg}")
            self.stop_parsing = True
            return False

        tok = self.tokens[self.pos]

        if tok.value in expected_vals or tok.type in expected_vals:
            self.pos += 1
            self.consecutive_errors = 0
            return True

        self.consecutive_errors += 1
        if self.consecutive_errors >= 2:
            self.stop_parsing = True
            return False

        self._error(f"Ожидалось: {error_msg}, получено '{tok.value}'")

        if tok.value in sync_vals or tok.type in sync_vals:
            return False

        self.pos += 1
        return False

    def parse_start(self):
        if self.stop_parsing: return
        self._skip_ws()
        if self._eof(): return

        tok = self.tokens[self.pos]
        if tok.value != "while":
            self.consecutive_errors += 1
            if self.consecutive_errors >= 2:
                self.stop_parsing = True
                return
            self._error("ключевое слово 'while'")
            if tok.value != "(":
                self.pos += 1
        else:
            self.consecutive_errors = 0
            self.pos += 1

        self.parse_keyword_while()

    def parse_keyword_while(self):
        if self.stop_parsing: return
        self._match_with_recovery(["("], [TokenType.IDENTIFIER], "'('")
        self.parse_left_brace()

    def parse_left_brace(self):
        if self.stop_parsing: return
        ops = ["<", ">", "==", ">=", "<=", "!="]
        self._skip_ws()
        if not self._eof():
            tok = self.tokens[self.pos]
            if tok.type == TokenType.IDENTIFIER and tok.value.startswith("$"):
                self.pos += 1
                self.consecutive_errors = 0
            else:
                self.consecutive_errors += 1
                if self.consecutive_errors >= 2:
                    self.stop_parsing = True
                    return
                self._error("переменная вида '$id'")
                if tok.value not in ops:
                    self.pos += 1

        self.parse_expression_operator()

    def parse_expression_operator(self):
        if self.stop_parsing: return
        ops = ["<", ">", "==", ">=", "<=", "!="]
        self._match_with_recovery(ops, [TokenType.NUMBER], "оператор сравнения")
        self.parse_expression()

    def parse_expression(self):
        if self.stop_parsing: return
        self._match_with_recovery([TokenType.NUMBER], ["||", "&&", ")"], "число")
        self.parse_number_tail()

    def parse_number_tail(self):
        if self.stop_parsing: return
        self._skip_ws()
        if self._eof(): return

        tok = self.tokens[self.pos]
        if tok.value in ["||", "&&"]:
            self.pos += 1
            self.consecutive_errors = 0
            self.parse_left_brace()
        elif tok.value == ")":
            self.pos += 1
            self.consecutive_errors = 0
            self.parse_right_brace()
        else:
            self.consecutive_errors += 1
            if self.consecutive_errors >= 2:
                self.stop_parsing = True
                return
            self._error("')' или логический оператор")
            if tok.value == "{":
                self.parse_right_brace()
            else:
                self.pos += 1
                self.parse_number_tail()

    def parse_right_brace(self):
        if self.stop_parsing: return
        self._match_with_recovery(["{"], [TokenType.IDENTIFIER, "}"], "'{'")
        self.parse_left_curly_brace()

    def parse_left_curly_brace(self):
        if self.stop_parsing: return
        while not self._eof() and not self.stop_parsing:
            self._skip_ws()
            if self._eof(): break

            tok = self.tokens[self.pos]

            if tok.value == "}":
                self.pos += 1
                self.consecutive_errors = 0
                self.parse_final_semicolon()
                return

            if tok.type == TokenType.IDENTIFIER and tok.value.startswith("$"):
                self.pos += 1
                self.consecutive_errors = 0
                self.parse_id_in_operator()
            else:
                self.consecutive_errors += 1
                if self.consecutive_errors >= 2:
                    self.stop_parsing = True
                    return
                self._error("инструкция ($id++) или '}'")
                if tok.value == ";":
                    self.pos += 1
                elif tok.value in ["++", "--"]:
                    self.parse_id_in_operator()
                else:
                    self.pos += 1

    def parse_id_in_operator(self):
        if self.stop_parsing: return
        self._match_with_recovery(["++", "--"], [";"], "++ или --")
        self.parse_operator_change()

    def parse_operator_change(self):
        if self.stop_parsing: return
        self._match_with_recovery([";"], ["$", "}"], "';'")

    def parse_final_semicolon(self):
        if self.stop_parsing: return
        self._match_with_recovery([";"], ["while", TokenType.EOF], "';' после цикла")

    def _error(self, msg):
        if self._eof():
            tok = self.tokens[-1] if self.tokens else None
        else:
            tok = self.tokens[self.pos]
        if tok:
            if self.errors and self.errors[-1].line == tok.line and self.errors[-1].column == tok.column:
                return
            self.errors.append(
                ScanError(ERROR_CODES["INVALID_STRUCTURE"], f"Ошибка: {msg}", tok.line, tok.column, tok.value))

    def _skip_ws(self):
        while not self._eof() and self.tokens[self.pos].type == TokenType.WHITESPACE:
            self.pos += 1

    def _eof(self):
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF

    def _check_unexpected_tokens(self):
        while not self._eof():
            tok = self.tokens[self.pos]
            self.errors.append(
                ScanError(ERROR_CODES["INVALID_STRUCTURE"], f"Лишний текст: '{tok.value}'", tok.line, tok.column,
                          tok.value))
            self.pos += 1