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

    def parse(self, scanner_errors=None):
        self.pos = 0
        self.errors = scanner_errors[:] if scanner_errors else []
        self.stop_parsing = False
        self.consecutive_errors = 0

        # Основной цикл парсинга
        while not self._eof() and not self.stop_parsing:
            self.parse_start()
            if not self._eof() and self.tokens[self.pos].value != "while":
                self.pos += 1

        # ФИНАЛЬНАЯ ОЧИСТКА: если на строке есть INVALID_CHAR, удаляем INVALID_STRUCTURE
        clean_errors = []
        # Находим линии, где лексер нашел косяки
        lines_with_lex_errors = {e.line for e in self.errors if e.code == ERROR_CODES["INVALID_CHAR"]}

        for e in self.errors:
            # Если это ошибка структуры на строке, где уже есть ошибка символов — игнорим её
            if e.code == ERROR_CODES["INVALID_STRUCTURE"] and e.line in lines_with_lex_errors:
                continue
            clean_errors.append(e)

        self.errors = clean_errors
        return self.errors

    def _error(self, msg):
        if self._eof():
            tok = self.tokens[-1] if self.tokens else None
        else:
            tok = self.tokens[self.pos]

        if tok:
            # Если на этой позиции уже есть ЛЮБАЯ ошибка — не дублируем
            if any(e.line == tok.line and e.column == tok.column for e in self.errors):
                return

            # Если это неизвестный токен — лексер о нем уже сказал
            if tok.type == TokenType.UNKNOWN:
                return

            if self.consecutive_errors > 0:
                return

            self.errors.append(
                ScanError(ERROR_CODES["INVALID_STRUCTURE"], f"Ошибка: {msg}", tok.line, tok.column, tok.value))
            self.consecutive_errors = 1

    def parse_start(self):
        if self.stop_parsing or self._eof(): return
        tok = self.tokens[self.pos]

        if tok.value != "while":
            self._error("ключевое слово 'while'")
            while not self._eof() and self.tokens[self.pos].value not in ["while", "("]:
                self.pos += 1
            if not self._eof() and self.tokens[self.pos].value == "while":
                self.pos += 1
        else:
            self.pos += 1

        self.parse_keyword_while()

    def _match_with_recovery(self, expected_vals, sync_vals, error_msg):
        if self._eof():
            self._error(f"Неожиданный конец файла. Ожидалось: {error_msg}")
            return False

        tok = self.tokens[self.pos]
        if tok.value in expected_vals or tok.type in expected_vals:
            self.pos += 1
            self.consecutive_errors = 0
            return True

        self._error(f"Ожидалось: {error_msg}, получено '{tok.value}'")

        while not self._eof():
            tok = self.tokens[self.pos]
            if tok.value in expected_vals or tok.type in expected_vals:
                self.pos += 1
                self.consecutive_errors = 0
                return True
            if tok.value in sync_vals or tok.type in sync_vals or tok.type == TokenType.UNKNOWN:
                return False
            self.pos += 1
        return False

    def parse_keyword_while(self):
        if self.stop_parsing or self._eof(): return
        if self._match_with_recovery(["("], [TokenType.IDENTIFIER, TokenType.UNKNOWN, "{", ")"], "'('"):
            self.parse_left_brace()

    def parse_left_brace(self):
        if self.stop_parsing or self._eof(): return
        ops = ["<", ">", "==", ">=", "<=", "!="]
        tok = self.tokens[self.pos]

        if tok.type == TokenType.IDENTIFIER and tok.value.startswith("$"):
            self.pos += 1
        else:
            if tok.value != ")":  # Избегаем ошибки на пустых скобках здесь, её поймает match
                self._error("переменная вида '$id'")
            while not self._eof() and self.tokens[self.pos].value not in ops and self.tokens[self.pos].value != ")":
                self.pos += 1
        self.parse_expression_operator()

    def parse_expression_operator(self):
        if self.stop_parsing or self._eof(): return
        ops = ["<", ">", "==", ">=", "<=", "!="]
        if self._match_with_recovery(ops, [TokenType.NUMBER, TokenType.IDENTIFIER, ")"], "оператор"):
            self.parse_expression()
        else:
            if not self._eof() and (
                    self.tokens[self.pos].type in [TokenType.NUMBER, TokenType.IDENTIFIER] or self.tokens[
                self.pos].value == ")"):
                self.parse_expression()

    def parse_expression(self):
        if self.stop_parsing or self._eof(): return
        tok = self.tokens[self.pos]
        if tok.type == TokenType.NUMBER or (tok.type == TokenType.IDENTIFIER and tok.value.startswith("$")):
            self.pos += 1
            self.parse_tail()
        else:
            if tok.value != ")":
                self._error("число или '$id'")
            while not self._eof() and self.tokens[self.pos].value not in ["||", "&&", ")", "{"]:
                self.pos += 1
            self.parse_tail()

    def parse_tail(self):
        if self.stop_parsing or self._eof(): return
        tok = self.tokens[self.pos]
        if tok.value in ["||", "&&"]:
            self.pos += 1
            self.parse_left_brace()
        elif tok.value == ")":
            self.pos += 1
            self.parse_right_brace()
        else:
            self._error("')' или логический оператор")
            while not self._eof() and self.tokens[self.pos].value not in [")", "{"]:
                self.pos += 1
            if not self._eof() and self.tokens[self.pos].value == ")":
                self.pos += 1
                self.parse_right_brace()

    def parse_right_brace(self):
        if self.stop_parsing or self._eof(): return
        if self._match_with_recovery(["{"], [TokenType.IDENTIFIER, "}"], "'{'"):
            self.parse_left_curly_brace()

    def parse_left_curly_brace(self):
        while not self._eof() and not self.stop_parsing:
            tok = self.tokens[self.pos]
            if tok.value == "}":
                self.pos += 1
                self.parse_final_semicolon()
                return
            if tok.type == TokenType.IDENTIFIER and tok.value.startswith("$"):
                self.pos += 1
                self.parse_id_in_operator()
            else:
                self._error("инструкция или '}'")
                self.pos += 1

    def parse_id_in_operator(self):
        if self._match_with_recovery(["++", "--"], [";", "}"], "++ или --"):
            self.parse_operator_change()

    def parse_operator_change(self):
        self._match_with_recovery([";"], ["$", "}"], "';'")

    def parse_final_semicolon(self):
        self._match_with_recovery([";"], ["while", TokenType.EOF], "';'")

    def _eof(self):
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF