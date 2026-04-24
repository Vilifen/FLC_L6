from .scanner import Scanner
from .parser import Parser


def run_scanner(editor):
    text = editor.toPlainText()
    scanner = Scanner()
    tokens, lex_errors = scanner.scan(text)
    parser = Parser(tokens)
    syntax_errors = parser.parse()

    raw_errors = lex_errors + syntax_errors
    token_rows = []
    error_rows = []

    for t in tokens:
        token_rows.append({
            "code": t.type.value,
            "type": t.type.name,
            "lexeme": t.value,
            "location": f"строка {t.line}, {t.column}",
            "line": t.line,
            "col": t.column
        })

    if raw_errors:
        merged = []
        current = raw_errors[0]

        for next_err in raw_errors[1:]:
            is_same_type = next_err.code == current.code
            is_same_line = next_err.line == current.line
            is_adjacent = next_err.column == (current.column + len(current.char))

            if is_same_type and is_same_line and is_adjacent:
                current.char += next_err.char
            else:
                merged.append(current)
                current = next_err
        merged.append(current)

        for e in merged:
            error_rows.append({
                "code": e.code,
                "type": "ОШИБКА",
                "lexeme": e.char,
                "location": f"строка {e.line}, {e.column}",
                "line": e.line,
                "col": e.column,
                "description": e.message
            })

    return token_rows, error_rows