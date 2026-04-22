import sys
from antlr4 import *

# Эти файлы будут сгенерированы ANTLR из WhileLang.g4
try:
    from .WhileLangLexer import WhileLangLexer
    from .WhileLangParser import WhileLangParser
except ImportError:
    # Инструкция: выполните в терминале 'antlr4 -Dlanguage=Python3 WhileLang.g4'
    pass

from .error_listener import MyErrorListener


def execute_antlr_analysis(text):
    input_stream = InputStream(text)

    # 1. Лексический анализ
    lexer = WhileLangLexer(input_stream)
    lexer_listener = MyErrorListener()
    lexer.removeErrorListeners()
    lexer.addErrorListener(lexer_listener)

    stream = CommonTokenStream(lexer)

    # 2. Синтаксический анализ
    parser = WhileLangParser(stream)
    parser_listener = MyErrorListener()
    parser.removeErrorListeners()
    parser.addErrorListener(parser_listener)

    # Запуск парсинга
    tree = parser.program()

    # 3. Подготовка токенов
    token_rows = []
    stream.fill()
    for token in stream.tokens:
        if token.type != Token.EOF:
            token_rows.append({
                "code": token.type,
                "type": lexer.symbolicNames[token.type] if token.type < len(lexer.symbolicNames) else "UNKNOWN",
                "lexeme": token.text,
                "line": token.line,
                "col": token.column
            })

    # Собираем все ошибки (лексер + парсер)
    all_errors = lexer_listener.errors + parser_listener.errors

    # Исправленное распределение по колонкам
    error_output = []
    for err in all_errors:
        error_output.append({
            "code": err["code"],
            "type": err["type"],
            "lexeme": err["lexeme"],
            "location": err["location"], # Теперь тут реально только "Line X, Col Y"
            "description": err["msg"],    # Описание ошибки теперь в своем поле
            "line": err["line"],
            "col": err["col"]
        })

    return token_rows, error_output