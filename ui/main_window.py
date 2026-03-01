from PyQt6.QtWidgets import QMainWindow
from ui.central import CentralWidget
from ui.actions import ActionManager
from ui.menus import MenuBuilder
from ui.toolbar import ToolbarBuilder
import re


class MainWindow(QMainWindow):
    def __init__(self, controller):
        super().__init__()

        self.labels_ru = {
            "file": "Файл",
            "edit": "Правка",
            "text": "Текст",
            "run": "Пуск",
            "help": "Справка",
            "localization": "Локализация",
            "view": "Вид",
            "font_size": "Размер шрифта",

            "new": "Создать",
            "open": "Открыть",
            "save": "Сохранить",
            "save_as": "Сохранить как",
            "exit": "Выход",

            "undo": "Отменить",
            "redo": "Повторить",
            "cut": "Вырезать",
            "copy": "Копировать",
            "paste": "Вставить",
            "delete": "Удалить",
            "select_all": "Выделить всё",

            "task": "Постановка задачи",
            "grammar": "Грамматика",
            "grammar_class": "Классификация грамматики",
            "method": "Метод анализа",
            "example": "Тестовый пример",
            "literature": "Список литературы",
            "source": "Исходный код программы",

            "about": "О программе",
            "info_title": "Информация",

            "error_label": "Ошибка",
            "forbidden_word": "Ошибка",
            "line_word": "строка",
            "pos_word": "позиция",
            "no_errors": "Ошибок не найдено.",
            "help_text": "Справка",
            "about_text": "О программе"
        }

        self.labels_en = {
            "file": "File",
            "edit": "Edit",
            "text": "Text",
            "run": "Run",
            "help": "Help",
            "localization": "Language",
            "view": "View",
            "font_size": "Font size",

            "new": "New",
            "open": "Open",
            "save": "Save",
            "save_as": "Save as",
            "exit": "Exit",

            "undo": "Undo",
            "redo": "Redo",
            "cut": "Cut",
            "copy": "Copy",
            "paste": "Paste",
            "delete": "Delete",
            "select_all": "Select all",

            "task": "Task description",
            "grammar": "Grammar",
            "grammar_class": "Grammar classification",
            "method": "Analysis method",
            "example": "Example",
            "literature": "References",
            "source": "Source code",

            "about": "About",
            "info_title": "Information",

            "error_label": "Error",
            "forbidden_word": "Error",
            "line_word": "line",
            "pos_word": "position",
            "no_errors": "No errors found.",
            "help_text": "Help",
            "about_text": "About"
        }

        self.labels = self.labels_ru

        self.setWindowTitle("Текстовый редактор")
        self.resize(900, 600)

        self.menuBar().setNativeMenuBar(False)
        self.menuBar().setStyleSheet("""
            QMenuBar { background: white; color: black; }
            QMenuBar::item { background: white; color: black; }
            QMenuBar::item:selected { background: #e6e6e6; color: black; }
            QMenu { background: white; color: black; }
            QMenu::item:selected { background: #e6e6e6; color: black; }
        """)

        self.setUnifiedTitleAndToolBarOnMac(False)

        self.central = CentralWidget()
        self.setCentralWidget(self.central)

        self.central.editor.textChanged.connect(self.on_editor_text_changed)

        self.actions = ActionManager(self, controller)
        MenuBuilder(self, self.actions)
        ToolbarBuilder(self, self.actions)

    def set_language(self, lang):
        if lang == "ru":
            self.labels = self.labels_ru
        else:
            self.labels = self.labels_en

        self.actions.update_texts()
        self.menuBar().clear()
        MenuBuilder(self, self.actions)

    def get_editor(self):
        return self.central.editor

    def get_output(self):
        return self.central.output

    def on_editor_text_changed(self):
        self.get_output().clear()

    def handle_output_click(self, line):
        line_word = self.labels["line_word"]
        pos_word = self.labels["pos_word"]
        pattern = rf"{line_word}\s+(\d+),\s*{pos_word}\s+(\d+)"
        match = re.search(pattern, line)
        if not match:
            return

        row = int(match.group(1))
        col = int(match.group(2))

        editor = self.get_editor()
        cursor = editor.textCursor()

        block = editor.document().findBlockByLineNumber(row - 1)
        cursor.setPosition(block.position() + col - 1)
        cursor.movePosition(cursor.MoveOperation.Right, cursor.MoveMode.KeepAnchor, 1)

        editor.setTextCursor(cursor)
        editor.setFocus()
