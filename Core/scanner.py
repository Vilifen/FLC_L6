from .token_types import TokenType
from .token import Token

class Scanner:
    KEYWORDS = {"while"}
    OPERATORS = {"++", "--", "<=", ">=", "==", "!=", "&&", "||", "<", ">", "_"}
    SEPARATORS = {"(", ")", "{", "}"}

    def __init__(self):
        self.text = ""
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []

    def scan(self, text: str):
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1
        self.tokens = []

        while self.pos < len(self.text):
            ch = self.text[self.pos]

            if ch in " \t\r\n":
                self._add(TokenType.WHITESPACE, ch)
                self._advance()
            elif ch == "$":
                self._consume_identifier()
            elif ch == ";":
                self._add(TokenType.SEPARATOR, ";")
                self._advance()
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
                # Склеиваем мусор в один блок
                start_line, start_col = self.line, self.col
                val = ""
                while self.pos < len(self.text):
                    curr = self.text[self.pos]
                    if (curr.isspace() or curr == "$" or curr.isalnum() or
                        curr in self.SEPARATORS or curr == ";" or self._starts_operator()):
                        break
                    val += curr
                    self._advance()
                self.tokens.append(Token(TokenType.UNKNOWN, val, start_line, start_col))

        self.tokens.append(Token(TokenType.EOF, "", self.line, self.col))
        return self.tokens, []

    def _advance(self):
        ch = self.text[self.pos]
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1

    def _add(self, ttype, value):
        self.tokens.append(Token(ttype, value, self.line, self.col))

    def _consume_identifier(self):
        start_line, start_col = self.line, self.col
        val = self.text[self.pos]
        self._advance()
        while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
            val += self.text[self.pos]
            self._advance()
        self.tokens.append(Token(TokenType.IDENTIFIER, val, start_line, start_col))

    def _consume_word(self):
        start_line, start_col = self.line, self.col
        val = ""
        while self.pos < len(self.text) and (self.text[self.pos].isalnum() or self.text[self.pos] == '_'):
            val += self.text[self.pos]
            self._advance()
        ttype = TokenType.KEYWORD if val in self.KEYWORDS else TokenType.IDENTIFIER
        self.tokens.append(Token(ttype, val, start_line, start_col))

    def _consume_number(self):
        start_line, start_col = self.line, self.col
        val = ""
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            val += self.text[self.pos]
            self._advance()
        self.tokens.append(Token(TokenType.NUMBER, val, start_line, start_col))

    def _starts_operator(self):
        if self.pos >= len(self.text): return False
        if self.pos + 1 < len(self.text):
            if (self.text[self.pos] + self.text[self.pos+1]) in self.OPERATORS: return True
        return self.text[self.pos] in self.OPERATORS

    def _consume_operator(self):
        start_line, start_col = self.line, self.col
        if self.pos + 1 < len(self.text) and (self.text[self.pos] + self.text[self.pos+1]) in self.OPERATORS:
            val = self.text[self.pos] + self.text[self.pos+1]
            self._advance()
            self._advance()
        else:
            val = self.text[self.pos]
            self._advance()
        self.tokens.append(Token(TokenType.OPERATOR, val, start_line, start_col))