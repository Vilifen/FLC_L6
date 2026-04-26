from .token_codes import TOKEN_CODES
def build_table_rows(tokens, errors, quads):
    token_rows = []
    error_rows = []
    quad_rows = []

    for t in tokens:
        if t.type.name == "WHITESPACE":
            continue

        code = TOKEN_CODES.get(t.type.name, 0)
        lexeme = t.value
        location = f"строка {t.line}, {t.column}-{t.column + max(1, len(t.value)) - 1}"

        token_rows.append({
            "code": code,
            "type": t.type.name,
            "lexeme": lexeme,
            "location": location,
            "line": t.line,
            "col": t.column,
        })

    for e in errors:
        error_rows.append({
            "code": e.code,
            "type": "ERROR",
            "lexeme": e.char,
            "location": f"строка {e.line}, {e.column}",
            "line": e.line,
            "col": e.column,
        })
    
    for q in quads:
        quad_rows.append({
            "operation": q.op,
            "arg1": q.arg1,
            "arg2": q.arg2,
            "result": q.result
        })

    return token_rows, error_rows, quad_rows  # Возвращаем quad_rows