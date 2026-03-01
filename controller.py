from PyQt6.QtWidgets import QFileDialog


class Controller:
    def file_new(self, editor):
        editor.clear()

    def file_open(self, window):
        path, _ = QFileDialog.getOpenFileName(
            window,
            "Открыть файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if path:
            with open(path, "r", encoding="utf-8") as f:
                window.get_editor().setPlainText(f.read())

    def file_save(self, window):
        path, _ = QFileDialog.getSaveFileName(
            window,
            "Сохранить файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(window.get_editor().toPlainText())

    def file_save_as(self, window):
        self.file_save(window)

    def run(self, window, editor, output):
        text = editor.toPlainText()
        lines = text.split("\n")

        forbidden = window.labels["forbidden_word"]
        error_label = window.labels["error_label"]
        line_word = window.labels["line_word"]
        pos_word = window.labels["pos_word"]

        for i, line in enumerate(lines, start=1):
            col = line.find(forbidden)
            if col != -1:
                if error_label == "Error":
                    output.setPlainText(
                        f'{error_label}: invalid word "{forbidden}" ({line_word} {i}, {pos_word} {col + 1})'
                    )
                else:
                    output.setPlainText(
                        f'{error_label}: недопустимое слово "{forbidden}" ({line_word} {i}, {pos_word} {col + 1})'
                    )
                return

        output.setPlainText(window.labels["no_errors"])

    def help(self, window, output):
        output.setPlainText(window.labels["help_text"])

    def about(self, window, output):
        output.setPlainText(window.labels["about_text"])
