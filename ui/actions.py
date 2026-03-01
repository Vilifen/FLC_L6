from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QStyle, QMessageBox


class ActionManager:
    def __init__(self, window, controller):
        self.win = window
        self.ctrl = controller
        style = window.style()

        self.new = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileIcon), "", window)
        self.open = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton), "", window)
        self.save = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogSaveButton), "", window)

        self.undo = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ArrowBack), "", window)
        self.redo = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ArrowForward), "", window)

        self.copy = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogContentsView), "", window)
        self.cut = QAction(style.standardIcon(QStyle.StandardPixmap.SP_TrashIcon), "", window)
        self.paste = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder), "", window)

        self.run = QAction(style.standardIcon(QStyle.StandardPixmap.SP_MediaPlay), "", window)

        self.menu_new = QAction("", window)
        self.menu_open = QAction("", window)
        self.menu_save = QAction("", window)
        self.menu_save_as = QAction("", window)
        self.menu_exit = QAction("", window)

        self.menu_undo = QAction("", window)
        self.menu_redo = QAction("", window)
        self.menu_cut = QAction("", window)
        self.menu_copy = QAction("", window)
        self.menu_paste = QAction("", window)
        self.menu_delete = QAction("", window)
        self.menu_select_all = QAction("", window)

        self.menu_text_task = QAction("", window)
        self.menu_text_grammar = QAction("", window)
        self.menu_text_class = QAction("", window)
        self.menu_text_method = QAction("", window)
        self.menu_text_example = QAction("", window)
        self.menu_text_literature = QAction("", window)
        self.menu_text_source = QAction("", window)

        self.menu_run = QAction("", window)

        self.menu_help = QAction("", window)
        self.menu_about = QAction("", window)

        self.lang_ru = QAction("Русский", window)
        self.lang_en = QAction("English", window)

        self._connect()
        self.update_texts()

    def update_texts(self):
        L = self.win.labels

        self.new.setText(L["new"])
        self.open.setText(L["open"])
        self.save.setText(L["save"])

        self.undo.setText(L["undo"])
        self.redo.setText(L["redo"])
        self.copy.setText(L["copy"])
        self.cut.setText(L["cut"])
        self.paste.setText(L["paste"])

        self.run.setText(L["run"])

        self.menu_new.setText(L["new"])
        self.menu_open.setText(L["open"])
        self.menu_save.setText(L["save"])
        self.menu_save_as.setText(L["save_as"])
        self.menu_exit.setText(L["exit"])

        self.menu_undo.setText(L["undo"])
        self.menu_redo.setText(L["redo"])
        self.menu_cut.setText(L["cut"])
        self.menu_copy.setText(L["copy"])
        self.menu_paste.setText(L["paste"])
        self.menu_delete.setText(L["delete"])
        self.menu_select_all.setText(L["select_all"])

        self.menu_text_task.setText(L["task"])
        self.menu_text_grammar.setText(L["grammar"])
        self.menu_text_class.setText(L["grammar_class"])
        self.menu_text_method.setText(L["method"])
        self.menu_text_example.setText(L["example"])
        self.menu_text_literature.setText(L["literature"])
        self.menu_text_source.setText(L["source"])

        self.menu_run.setText(L["run"])

        self.menu_help.setText(L["help"])
        self.menu_about.setText(L["about"])

    def _connect(self):
        editor = self.win.get_editor()
        output = self.win.get_output()

        self.menu_new.triggered.connect(lambda: self.ctrl.file_new(editor))
        self.menu_open.triggered.connect(lambda: self.ctrl.file_open(self.win))
        self.menu_save.triggered.connect(lambda: self.ctrl.file_save(self.win))
        self.menu_save_as.triggered.connect(lambda: self.ctrl.file_save_as(self.win))
        self.menu_exit.triggered.connect(self.win.close)

        self.new.triggered.connect(lambda: self.ctrl.file_new(editor))
        self.open.triggered.connect(lambda: self.ctrl.file_open(self.win))
        self.save.triggered.connect(lambda: self.ctrl.file_save(self.win))

        self.undo.triggered.connect(editor.undo)
        self.redo.triggered.connect(editor.redo)
        self.copy.triggered.connect(editor.copy)
        self.cut.triggered.connect(editor.cut)
        self.paste.triggered.connect(editor.paste)

        self.menu_undo.triggered.connect(editor.undo)
        self.menu_redo.triggered.connect(editor.redo)
        self.menu_cut.triggered.connect(editor.cut)
        self.menu_copy.triggered.connect(editor.copy)
        self.menu_paste.triggered.connect(editor.paste)
        self.menu_delete.triggered.connect(lambda: editor.textCursor().removeSelectedText())
        self.menu_select_all.triggered.connect(editor.selectAll)

        self.menu_text_task.triggered.connect(lambda: self._info(self.win.labels["task"]))
        self.menu_text_grammar.triggered.connect(lambda: self._info(self.win.labels["grammar"]))
        self.menu_text_class.triggered.connect(lambda: self._info(self.win.labels["grammar_class"]))
        self.menu_text_method.triggered.connect(lambda: self._info(self.win.labels["method"]))
        self.menu_text_example.triggered.connect(lambda: self._info(self.win.labels["example"]))
        self.menu_text_literature.triggered.connect(lambda: self._info(self.win.labels["literature"]))
        self.menu_text_source.triggered.connect(lambda: self._info(self.win.labels["source"]))

        self.menu_run.triggered.connect(lambda: self.ctrl.run(self.win, editor, output))
        self.run.triggered.connect(lambda: self.ctrl.run(self.win, editor, output))

        self.menu_help.triggered.connect(lambda: self.ctrl.help(self.win, output))
        self.menu_about.triggered.connect(lambda: self.ctrl.about(self.win, output))

        self.lang_ru.triggered.connect(lambda: self.win.set_language("ru"))
        self.lang_en.triggered.connect(lambda: self.win.set_language("en"))

    def _info(self, text):
        QMessageBox.information(self.win, self.win.labels["info_title"], text)
