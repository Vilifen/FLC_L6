from antlr4 import InputStream, CommonTokenStream
from ANTLR.WhileLoopLexer import WhileLoopLexer
from ANTLR.WhileLoopParser import WhileLoopParser
from antlr4.error.ErrorListener import ErrorListener
from antlr4.error.Errors import InputMismatchException, NoViableAltException


class AntlrErrorListener(ErrorListener):
    def __init__(self):
        super(AntlrErrorListener, self).__init__()
        self.errors = []

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        if isinstance(recognizer, WhileLoopLexer):
            return

        err_type = "Синтаксическая ошибка"
        if isinstance(e, InputMismatchException):
            err_type = "Ошибка соответствия"
        elif isinstance(e, NoViableAltException):
            err_type = "Неверная конструкция"

        self.errors.append({
            "code": "SYNTAX_ERR",
            "type": err_type,
            "lexeme": offendingSymbol.text if offendingSymbol else "",
            "line": line,
            "col": column + 1,
            "message": msg
        })


def execute_antlr_analysis(text):
    input_stream = InputStream(text)
    error_listener = AntlrErrorListener()

    lexer = WhileLoopLexer(input_stream)
    lexer.removeErrorListeners()
    lexer.addErrorListener(error_listener)

    stream = CommonTokenStream(lexer)
    parser = WhileLoopParser(stream)
    parser.removeErrorListeners()
    parser.addErrorListener(error_listener)

    parser.program()

    token_rows = []
    final_errors = []
    stream.fill()

    any_type = lexer.ANY
    var_type = lexer.VAR

    i = 0
    tokens = stream.tokens
    while i < len(tokens):
        token = tokens[i]
        if token.type == -1:
            i += 1
            continue

        is_bad_var = (token.type == var_type and token.text == "$")
        is_any = (token.type == any_type)

        if is_bad_var or is_any:
            err_lexeme = token.text
            start_line = token.line
            start_col = token.column + 1

            j = i + 1
            while j < len(tokens):
                next_t = tokens[j]
                if next_t.type == any_type or (next_t.type == var_type and next_t.text == "$"):
                    err_lexeme += next_t.text
                    j += 1
                else:
                    break

            final_errors.append({
                "code": "LEX_ERR",
                "type": "Лексическая ошибка",
                "lexeme": err_lexeme,
                "line": start_line,
                "col": start_col,
                "message": f"Недопустимая последовательность '{err_lexeme}'"
            })
            i = j
        else:
            token_rows.append({
                "code": token.type,
                "type": lexer.symbolicNames[token.type] if token.type < len(lexer.symbolicNames) else "UNKNOWN",
                "lexeme": token.text,
                "line": token.line,
                "col": token.column + 1
            })
            i += 1

    final_errors.extend(error_listener.errors)
    return token_rows, final_errors