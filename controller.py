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
            window.central.show_results_table([])

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
        if editor is None:
            return

        text = editor.toPlainText()
        lines = text.split("\n")

        forbidden = window.labels["forbidden_word"]
        error_label = window.labels["error_label"]
        line_word = window.labels["line_word"]
        pos_word = window.labels["pos_word"]

        errors = []

        for i, line in enumerate(lines, start=1):
            col = line.find(forbidden)
            if col != -1:
                msg = (
                    f'{error_label}: недопустимое слово "{forbidden}"'
                    if error_label != "Error"
                    else f'{error_label}: invalid word "{forbidden}"'
                )

                errors.append({
                    "file": window.central.tabs[window.central.current_index]["title"],
                    "line": i,
                    "column": col + 1,
                    "message": msg
                })

        window.central.show_results_table(errors)

    def help(self, window, output):
        window.central.show_results_table([])

    def about(self, window, output):
        window.central.show_results_table([])
