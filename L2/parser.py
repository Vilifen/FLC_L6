from .scan_error import ScanError
from .error_codes import ERROR_CODES
from .token_types import TokenType


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.errors = []

    def parse(self, scanner_errors=None):
        self.pos = 0
        self.errors = []
        while not self._eof():
            self._skip_noise()
            if self._eof(): break
            self.parse_while_stmt()
        return self.errors

    def _error(self, msg, tok):
        # Строгий контроль: не добавляем ошибку, если на этой позиции она уже была
        if self.errors and self.errors[-1].line == tok.line and self.errors[-1].column == tok.column:
            return
        self.errors.append(ScanError(
            ERROR_CODES["INVALID_STRUCTURE"],
            f"Ошибка: {msg}",
            tok.line, tok.column, tok.value
        ))

    def _skip_noise(self):
        # Просто перепрыгиваем пробелы
        while not self._eof() and self.tokens[self.pos].type == TokenType.WHITESPACE:
            self.pos += 1

    def _sync_expect(self, condition, error_msg):
        """
        Ищет токен. Если видит мусор или несоответствие:
        1. Выдает 'недопустимый символ' (если это мусор) ИЛИ ожидаемую ошибку.
        2. Поглощает токены, пока не найдет то, что нужно.
        """
        self._skip_noise()
        first_error_reported = False

        while not self._eof():
            tok = self.tokens[self.pos]

            # Проверка на совпадение
            is_match = False
            if callable(condition):
                is_match = condition(tok)
            elif isinstance(condition, list):
                is_match = tok.value in condition
            else:
                is_match = tok.value == condition or tok.type == condition

            if is_match:
                self.pos += 1
                return True

            # Если не совпало — это ошибка
            if not first_error_reported:
                # Если это реально мусорный токен (типа ! или @)
                if tok.type == TokenType.UNKNOWN or tok.value == ";":
                    self._error("недопустимый символ", tok)
                else:
                    self._error(error_msg, tok)
                first_error_reported = True

            # Поглощаем токен и ищем дальше
            self.pos += 1
            self._skip_noise()

        return False

    def parse_while_stmt(self):
        # Ожидаем структуру, игнорируя мусор между элементами
        self._sync_expect("while", "ключевое слово 'while'")
        self._sync_expect("(", "'('")

        # Переменная $id
        self._sync_expect(lambda t: t.type == TokenType.IDENTIFIER and t.value.startswith("$"),
                          "переменная '$id'")

        # Оператор сравнения
        self._sync_expect(["<", ">", "==", "!=", "<=", ">="], "оператор сравнения")

        # Число или переменная
        self._sync_expect(lambda t: t.type in [TokenType.NUMBER, TokenType.IDENTIFIER],
                          "число или переменная")

        self._sync_expect(")", "')'")
        self._sync_expect("{", "'{'")

        # Тело цикла
        while not self._eof():
            self._skip_noise()
            if self._eof() or self.tokens[self.pos].value == "}":
                break

            # Разбор $i++;
            if self.tokens[self.pos].type == TokenType.IDENTIFIER:
                self.pos += 1
                self._sync_expect(["++", "--"], "++ или --")
                self._sync_expect(";", "';'")
            else:
                # Если в теле встречен мусор (не идентификатор)
                tok = self.tokens[self.pos]
                self._error(
                    "недопустимый символ" if tok.type == TokenType.UNKNOWN or tok.value == ";" else "инструкция", tok)
                self.pos += 1

        self._sync_expect("}", "'}'")
        self._sync_expect(";", "';'")

    def _eof(self):
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == TokenType.EOF