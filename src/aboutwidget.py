from PySide6.QtWidgets import QLabel, QVBoxLayout, QTableWidgetItem, QTableWidget
from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette

from data import *


class AboutWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.home = QVBoxLayout()
        self.table = QTableWidget(self)
        self.text = QLabel(self)
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setWindowTitle('关于')
        self.setFixedSize(450, 420)
        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor('#ffffff'))
        self.setPalette(palette)
        move_to_middle(self)

        self.setLayout(self.home)
        self.home.addWidget(self.text)
        self.home.addWidget(self.table)
        self.home.setContentsMargins(10, 10, 10, 10)
        self.table.setColumnCount(3)
        self.table.setRowCount(6)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setWordWrap(False)
        self.table.setColumnWidth(0, 100)
        self.table.setColumnWidth(1, 250)
        self.table.setColumnWidth(2, 50)
        self.text.setWordWrap(True)
        self.text.setMargin(15)

    def init_language(self):
        self.text.setText(LANG_UI_TXT.AboutWidget.Info)
        self.table.setHorizontalHeaderLabels(LANG_UI_TXT.AboutWidget.Headers)
        for n, i in enumerate(LANG_UI_TXT.AboutWidget.Programs):
            self.table.setItem(n, 0, QTableWidgetItem(i[0]))
            self.table.setItem(n, 1, QTableWidgetItem(i[1]))
            self.table.setItem(n, 2, QTableWidgetItem(i[2]))

    def init_font(self, font: QFont):
        self.table.setFont(font)
        self.table.horizontalHeader().setFont(font)
        self.table.verticalHeader().setFont(font)
        self.text.setFont(font)
