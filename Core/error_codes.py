class ErrorCode:
    UNEXPECTED_CHAR = 101
    INVALID_ID = 102
    UNEXPECTED_TOKEN = 201
    MISSING_RPAREN = 202

ERROR_CODES = {
    101: "Unexpected character",
    102: "Invalid ID format",
    201: "Unexpected token",
    202: "Missing closing parenthesis"
}