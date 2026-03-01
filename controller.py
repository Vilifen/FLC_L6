from PyQt6.QtWidgets import QFileDialog
import os


class Controller:
    def file_new(self, window):
        window.central.add_tab("Без имени")

    def file_open(self, window):
        path, _ = QFileDialog.getOpenFileName(
            window,
            "Открыть файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if path:
            title = os.path.basename(path)
            window.central.add_tab(title)
            editor = window.get_editor()
            with open(path, "r", encoding="utf-8") as f:
                editor.setPlainText(f.read())
            window.central.set_current_output_text("")

    def file_save(self, window):
        editor = window.get_editor()
        if editor is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            window,
            "Сохранить файл",
            "",
            "Текстовые файлы (*.txt);;Все файлы (*.*)"
        )
        if path:
            with open(path, "w", encoding="utf-8") as f:
                f.write(editor.toPlainText())
            window.central.rename_current_tab(os.path.basename(path))

    def file_save_as(self, window):
        self.file_save(window)

    def run(self, window):
        editor = window.get_editor()
        output = window.get_output()
        if editor is None or output is None:
            return

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
                    msg = f'{error_label}: invalid word "{forbidden}" ({line_word} {i}, {pos_word} {col + 1})'
                else:
                    msg = f'{error_label}: недопустимое слово "{forbidden}" ({line_word} {i}, {pos_word} {col + 1})'
                window.central.set_current_output_text(msg)
                return

        window.central.set_current_output_text(window.labels["no_errors"])

    def help(self, window, output):
        output.setPlainText(window.labels["help_text"])

    def about(self, window, output):
        output.setPlainText(window.labels["about_text"])
