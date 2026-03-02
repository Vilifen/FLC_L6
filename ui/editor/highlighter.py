from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor
from PyQt6.QtCore import QRegularExpression


class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.rules = []

        def fmt(color, bold=False):
            f = QTextCharFormat()
            f.setForeground(QColor(color))
            if bold:
                f.setFontWeight(600)
            return f

        keywords = [
            "def", "class", "return", "if", "elif", "else", "while", "for",
            "try", "except", "finally", "with", "as", "import", "from",
            "pass", "break", "continue", "in", "is", "not", "and", "or",
            "lambda", "yield", "global", "nonlocal", "assert", "raise"
        ]

        keyword_format = fmt("#0077cc", True)
        for kw in keywords:
            self.rules.append((QRegularExpression(rf"\b{kw}\b"), keyword_format))

        string_format = fmt("#dd1144")
        self.rules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.rules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))

        comment_format = fmt("#009933")
        self.rules.append((QRegularExpression(r"#.*"), comment_format))

        number_format = fmt("#aa00aa")
        self.rules.append((QRegularExpression(r"\b[0-9]+\b"), number_format))

    def highlightBlock(self, text):
        for pattern, form in self.rules:
            it = pattern.globalMatch(text)
            while it.hasNext():
                m = it.next()
                self.setFormat(m.capturedStart(), m.capturedLength(), form)
