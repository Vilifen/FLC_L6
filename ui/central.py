from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPlainTextEdit, QPushButton, QSizePolicy, QMessageBox
from PyQt6.QtGui import QPainter, QColor
from PyQt6.QtCore import QRect, QSize, Qt
from functools import partial


class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self):
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event):
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(False)

        self.line_number_area = LineNumberArea(self)
        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.update)
        self.update_line_number_area_width(0)

    def dragEnterEvent(self, event):
        event.ignore()

    def dropEvent(self, event):
        event.ignore()

    def line_number_area_width(self):
        digits = len(str(max(1, self.blockCount())))
        return 12 + self.fontMetrics().horizontalAdvance('9') * digits

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor(245, 245, 245))
        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())
        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                painter.setPen(QColor(0, 0, 0))
                painter.drawText(
                    0, top,
                    self.line_number_area.width() - 4,
                    self.fontMetrics().height(),
                    Qt.AlignmentFlag.AlignRight,
                    str(block_number + 1)
                )
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1


class CentralWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = []
        self.current_index = -1
        self.untitled_counter = 1

        self.setAcceptDrops(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tab_bar = QWidget()
        self.tab_bar.setStyleSheet("""
            QWidget {
                background: #f0f0f0;
                border-bottom: 1px solid #c0c0c0;
            }
        """)

        self.tab_layout = QHBoxLayout(self.tab_bar)
        self.tab_layout.setContentsMargins(4, 2, 4, 0)
        self.tab_layout.setSpacing(2)

        self.spacer = QWidget()
        self.spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.plus_button = QPushButton("+")
        self.plus_button.setFixedWidth(28)
        self.plus_button.setFlat(True)
        self.plus_button.setStyleSheet("""
            QPushButton {
                background: #e6e6e6;
                border: 1px solid #a0a0a0;
                padding: 4px 8px;
                color: black;
            }
            QPushButton:hover {
                background: #f2f2f2;
            }
        """)
        self.plus_button.clicked.connect(self.add_tab)

        self.tab_layout.addWidget(self.spacer)
        self.tab_layout.addWidget(self.plus_button)

        self.editor = CodeEditor()
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background: white;
                color: black;
                font-size: 14px;
                border: none;
            }
        """)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QTextEdit {
                background: white;
                color: black;
                font-size: 14px;
                border-top: 1px solid #c0c0c0;
            }
        """)

        self.editor.textChanged.connect(self._sync_editor)

        layout.addWidget(self.tab_bar)
        layout.addWidget(self.editor, 3)
        layout.addWidget(self.output, 1)

        self.add_tab()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if not urls:
            return
        path = urls[0].toLocalFile()
        if not path:
            return
        self.open_file_from_path(path)

    def open_file_from_path(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        except Exception:
            return

        self.add_tab()

        filename = path.split("/")[-1]
        tab = self.tabs[self.current_index]
        tab["title"] = filename
        tab["button"].setText(f"{filename}   ✕")
        tab["text"] = text
        tab["modified"] = False

        self.editor.blockSignals(True)
        self.editor.setPlainText(text)
        self.editor.blockSignals(False)

    def _sync_editor(self):
        if 0 <= self.current_index < len(self.tabs):
            self.tabs[self.current_index]["text"] = self.editor.toPlainText()
            self.tabs[self.current_index]["modified"] = True

    def _sync_output(self):
        if 0 <= self.current_index < len(self.tabs):
            self.tabs[self.current_index]["output"] = self.output.toPlainText()
            self.tabs[self.current_index]["modified"] = True

    def _update_tab_buttons_state(self):
        for i, tab in enumerate(self.tabs):
            tab["button"].setChecked(i == self.current_index)

    def add_tab(self):
        if 0 <= self.current_index < len(self.tabs):
            self._sync_editor()
            self._sync_output()

        title = f"Без имени {self.untitled_counter}"
        self.untitled_counter += 1

        btn = QPushButton(f"{title}   ✕")
        btn.setCheckable(True)
        btn.setFlat(True)
        btn.setStyleSheet("""
            QPushButton {
                background: #e6e6e6;
                border: 1px solid #a0a0a0;
                padding: 4px 12px;
                color: black;
            }
            QPushButton:checked {
                background: #ffffff;
                border-bottom: 1px solid #ffffff;
                color: black;
            }
        """)

        index = len(self.tabs)
        btn.clicked.connect(partial(self.switch_tab, index))
        btn.mousePressEvent = partial(self._tab_mouse_press, index=index, button=btn)

        self.tab_layout.insertWidget(self.tab_layout.count() - 2, btn)

        self.tabs.append({
            "title": title,
            "text": "",
            "output": "",
            "button": btn,
            "modified": False,
        })

        self.current_index = index
        self._load_tab()
        self._update_tab_buttons_state()

    def _tab_mouse_press(self, event, index, button):
        if event.pos().x() > button.width() - 18:
            self._request_close_tab(index)
            return
        self.switch_tab(index)

    def _request_close_tab(self, index):
        data = self.tabs[index]
        if not data.get("modified"):
            self.close_tab(index)
            return

        w = self.window()

        msg = QMessageBox(self)
        msg.setWindowTitle(w.labels["save_title"])
        msg.setText(f"{w.labels['save_text']} «{data['title']}»?")
        yes_btn = msg.addButton(w.labels["yes"], QMessageBox.ButtonRole.YesRole)
        no_btn = msg.addButton(w.labels["no"], QMessageBox.ButtonRole.NoRole)
        cancel_btn = msg.addButton(w.labels["cancel"], QMessageBox.ButtonRole.RejectRole)
        msg.setDefaultButton(yes_btn)
        msg.exec()
        clicked = msg.clickedButton()

        if clicked is cancel_btn:
            return
        if clicked is yes_btn:
            w.actions.save.trigger()

        self.close_tab(index)

    def close_tab(self, index):
        if len(self.tabs) == 1:
            return

        self.tabs.pop(index)
        self.tab_layout.itemAt(index).widget().deleteLater()

        for i, tab in enumerate(self.tabs):
            tab["button"].clicked.disconnect()
            tab["button"].clicked.connect(partial(self.switch_tab, i))
            tab["button"].mousePressEvent = partial(self._tab_mouse_press, index=i, button=tab["button"])

        self.current_index = max(0, index - 1)
        self._load_tab()
        self._update_tab_buttons_state()

    def switch_tab(self, index):
        if index == self.current_index:
            return
        if not (0 <= index < len(self.tabs)):
            return

        if 0 <= self.current_index < len(self.tabs):
            self._sync_editor()
            self._sync_output()

        self.current_index = index
        self._load_tab()
        self._update_tab_buttons_state()

    def _load_tab(self):
        data = self.tabs[self.current_index]
        self.editor.blockSignals(True)
        self.editor.setPlainText(data["text"])
        self.editor.blockSignals(False)
        self.output.setPlainText(data["output"])

    def current_editor(self):
        return self.editor

    def current_output(self):
        return self.output

    def set_current_output_text(self, text):
        self.output.setPlainText(text)
        self._sync_output()

    def rename_current_tab(self, title):
        if 0 <= self.current_index < len(self.tabs):
            self.tabs[self.current_index]["title"] = title
            self.tabs[self.current_index]["button"].setText(f"{title}   ✕")
