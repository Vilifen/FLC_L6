from PyQt6.QtWidgets import QMainWindow, QMessageBox, QStatusBar
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
            "status_lang": "Язык",
            "status_size": "Размер",
            "status_lines": "Строк",
            "build": "Сборка",
            "errors": "Ошибки",
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
            "status_lang": "Language",
            "status_size": "Size",
            "status_lines": "Lines",
            "build": "Build",
            "errors": "Errors",
        }

        self.labels = self.labels_ru

        self.setWindowTitle("Текстовый редактор")
        self.resize(1000, 700)
        self.menuBar().setNativeMenuBar(False)

        self.status = QStatusBar()
        self.status.setStyleSheet("""
            QStatusBar {
                background: white;
                color: black;
                border-top: 1px solid #c0c0c0;
            }
        """)
        self.setStatusBar(self.status)

        self.central = CentralWidget()
        self.setCentralWidget(self.central)

        self.actions = ActionManager(self, controller)
        MenuBuilder(self, self.actions)
        ToolbarBuilder(self, self.actions)

        self._build_font_menu()

        self.set_language("ru")
        self.update_status_bar()

        self.central.editor.textChanged.connect(self.update_status_bar)

    def _build_font_menu(self):
        view_menu = None
        for act in self.menuBar().actions():
            menu = act.menu()
            if menu and menu.title() == self.labels["view"]:
                view_menu = menu
                break
        if view_menu is None:
            return

        font_menu = view_menu.addMenu(self.labels["font_size"])
        sizes = [8, 9, 10, 11, 12, 14, 16, 18, 20, 22, 24, 28, 32]

        for size in sizes:
            action = font_menu.addAction(str(size))
            action.triggered.connect(lambda _, s=size: self.central.set_font_size(s))

    def update_status_bar(self):
        text = self.central.editor.toPlainText()
        size = len(text.encode("utf-8"))
        lines = text.count("\n") + 1
        lang = "RU" if self.labels is self.labels_ru else "EN"

        self.status.showMessage(
            f"{self.labels['status_lang']}: {lang}    "
            f"{self.labels['status_size']}: {size} B    "
            f"{self.labels['status_lines']}: {lines}"
        )

    def set_language(self, lang: str):
        if lang == "ru":
            self.labels = self.labels_ru
        else:
            self.labels = self.labels_en

        self.actions.update_texts()

        self.menuBar().clear()
        from ui.menus import MenuBuilder
        MenuBuilder(self, self.actions)

        self._build_font_menu()

        for tab in self.central.tabs:
            title = tab["title"]
            tab["button"].setText(f"{title}   ✕")

        self.central.build_btn.setText(self.labels["build"])
        self.central.err_btn.setText(self.labels["errors"])

        self.update_status_bar()
        self.repaint()

    def get_editor(self):
        return self.central.editor

    def get_output(self):
        return self.central.output

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
