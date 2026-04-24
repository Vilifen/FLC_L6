from enum import Enum

class TokenType(Enum):
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    MOD = "%"
    LPAREN = "("
    RPAREN = ")"
    ID = "ID"
    NUM = "NUM"
    NEWLINE = "NEWLINE"
    WHITESPACE = "WHITESPACE"
    EOF = "EOF"
    ERROR = "ERROR"