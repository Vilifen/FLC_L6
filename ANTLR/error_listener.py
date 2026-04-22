from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener(ErrorListener):
    def __init__(self):
        super(MyErrorListener, self).__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        # Формируем структуру: описание отдельно, координаты отдельно
        error_info = {
            "code": "SYNTAX_ERR",
            "type": "ANTLR Error",
            "lexeme": str(offendingSymbol.text) if offendingSymbol else "unknown",
            "location": f"Line {line}, Col {column}", # Только местоположение
            "msg": msg, # Чистое описание ошибки
            "line": line,
            "col": column
        }
        self.errors.append(error_info)