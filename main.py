import sys
import os
import py_mini_racer
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QAction, QToolBar, QMainWindow, QFileDialog, QTabWidget, QMessageBox, QSizePolicy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class JsEditorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.tabs = QTabWidget()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('ZenJS - Editor')
        self.setGeometry(100, 100, 800, 600)
        self.setCentralWidget(self.tabs)
        self.setup_toolbar()
        self.add_new_tab()

    def setup_toolbar(self):
        open_action = QAction(QIcon(), 'Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)

        save_action = QAction(QIcon(), 'Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)

        save_as_action = QAction(QIcon(), 'Save As', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_as_file)

        new_action = QAction(QIcon(), 'New File', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)

        execute_action = QAction(QIcon(), 'Execute File', self)
        execute_action.setShortcut('Ctrl+E')
        execute_action.triggered.connect(self.execute_js_file)

        toolbar = QToolBar('Toolbar')
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)
        toolbar.addAction(save_as_action)
        toolbar.addAction(new_action)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        toolbar.addWidget(spacer)

        toolbar.addAction(execute_action)

    def add_new_tab(self, filename=None):
        new_tab_index = self.tabs.count()

        editor = QTextEdit()
        console_label = QLabel('Console Output:')
        console = QTextEdit()
        console.setReadOnly(True)

        tab_widget = QWidget()
        tab_layout = QHBoxLayout(tab_widget)
        
        # Divide the tab horizontally
        editor_and_console_layout = QVBoxLayout()
        editor_and_console_layout.addWidget(editor, 2)  # Editor takes 2/3 of space
        editor_and_console_layout.addWidget(console_label)
        editor_and_console_layout.addWidget(console, 1)  # Console takes 1/3 of space

        tab_layout.addLayout(editor_and_console_layout)

        self.tabs.addTab(tab_widget, filename if filename else 'Untitled')
        self.tabs.setCurrentIndex(new_tab_index)
        
        tab_widget.editor = editor
        tab_widget.console = console
        tab_widget.filepath = None

    def open_file(self):
        filepath, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'JavaScript Files (*.js)')
        if filepath:
            filename = os.path.basename(filepath)
            with open(filepath, 'r') as file:
                js_code = file.read()
                self.add_new_tab(filename)
                tab_widget = self.tabs.currentWidget()
                tab_widget.editor.setPlainText(js_code)
                tab_widget.filepath = filepath

    def save_file(self):
        tab_widget = self.tabs.currentWidget()
        if hasattr(tab_widget, 'filepath') and tab_widget.filepath:
            try:
                js_code = tab_widget.editor.toPlainText()
                with open(tab_widget.filepath, 'w') as file:
                    file.write(js_code)
                filename = os.path.basename(tab_widget.filepath)
                self.tabs.setTabText(self.tabs.currentIndex(), filename)
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to save file: {str(e)}')
        else:
            self.save_as_file()

    def save_as_file(self):
        tab_widget = self.tabs.currentWidget()
        filepath, _ = QFileDialog.getSaveFileName(self, 'Save File As', '', 'JavaScript Files (*.js)')
        if filepath:
            tab_widget.filepath = filepath
            self.save_file()

    def new_file(self):
        self.add_new_tab()

    def execute_js_file(self):
        tab_widget = self.tabs.currentWidget()
        if hasattr(tab_widget, 'filepath') and tab_widget.filepath:
            try:
                self.save_file()
                with open(tab_widget.filepath, 'r') as file:
                    js_code = file.read()
                ctx = py_mini_racer.MiniRacer()
                result = ctx.eval(js_code)
                self.append_to_console(tab_widget.console, f'{tab_widget.filepath}:\n{str(result)}\n')
            except Exception as e:
                self.append_to_console(tab_widget.console, f'Error executing {tab_widget.filepath}:\n{str(e)}\n')
        else:
            QMessageBox.warning(self, 'Warning', 'No JavaScript file open in the current tab.')

    def append_to_console(self, console, text):
        cursor = console.textCursor()
        cursor.movePosition(cursor.End)
        cursor.insertText(text)
        console.setTextCursor(cursor)
        console.ensureCursorVisible()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = JsEditorApp()
    ex.show()
    sys.exit(app.exec_())