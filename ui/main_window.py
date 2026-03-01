from PyQt6.QtWidgets import QMainWindow, QMessageBox
from ui.central import CentralWidget
from ui.actions import ActionManager
from ui.menus import MenuBuilder
from ui.toolbar import ToolbarBuilder


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
            "about_text": "О программе",
            "save_title": "Сохранить файл?",
            "save_text": "Сохранить изменения в файле",
            "yes": "Да",
            "no": "Нет",
            "cancel": "Отмена",
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
            "about_text": "About",
            "save_title": "Save file?",
            "save_text": "Save changes to file",
            "yes": "Yes",
            "no": "No",
            "cancel": "Cancel",
        }

        self.labels = self.labels_ru

        self.setWindowTitle("Текстовый редактор")
        self.resize(1000, 700)
        self.menuBar().setNativeMenuBar(False)

        self.central = CentralWidget()
        self.setCentralWidget(self.central)

        self.actions = ActionManager(self, controller)
        MenuBuilder(self, self.actions)
        ToolbarBuilder(self, self.actions)

        self.set_language("ru")

    def set_language(self, lang: str):
        if lang == "ru":
            self.labels = self.labels_ru
        else:
            self.labels = self.labels_en

        self.menuBar().clear()
        from ui.menus import MenuBuilder
        MenuBuilder(self, self.actions)

        for tab in self.central.tabs:
            title = tab["title"]
            tab["button"].setText(f"{title}   ✕")

        self.repaint()

    def closeEvent(self, event):
        for tab in self.central.tabs:
            if tab.get("modified"):
                msg = QMessageBox(self)
                msg.setWindowTitle(self.labels["save_title"])
                msg.setText(f"{self.labels['save_text']} «{tab['title']}»?")
                yes_btn = msg.addButton(self.labels["yes"], QMessageBox.ButtonRole.YesRole)
                no_btn = msg.addButton(self.labels["no"], QMessageBox.ButtonRole.NoRole)
                cancel_btn = msg.addButton(self.labels["cancel"], QMessageBox.ButtonRole.RejectRole)
                msg.setDefaultButton(yes_btn)
                msg.exec()
                clicked = msg.clickedButton()
                if clicked is cancel_btn:
                    event.ignore()
                    return
                if clicked is yes_btn:
                    self.actions.save.trigger()
        event.accept()
