from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QTreeWidget, QLineEdit, QTextEdit, QMessageBox,\
    QTreeWidgetItem
from PyQt5.QtCore import Qt
import argparse

import sys
from bs4 import BeautifulSoup

QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.data = {}
        self.home = QGridLayout(self)
        self.searchLine = QLineEdit(self)
        self.nameTreeWidget = QTreeWidget(self)
        self.helpTextEdit = QTextEdit(self)
        self.init_ui()

    def init_ui(self):
        self.load()
        self.setWindowTitle('x265说明文档')
        self.setMinimumSize(1000, 800)
        self.searchLine.textChanged.connect(self.search)
        self.searchLine.setFixedWidth(200)
        self.nameTreeWidget.setHeaderHidden(True)
        self.nameTreeWidget.setColumnCount(1)
        self.nameTreeWidget.setFixedWidth(200)
        self.nameTreeWidget.currentItemChanged.connect(self.change_row)
        self.home.addWidget(self.searchLine, 0, 0, 1, 1)
        self.home.addWidget(self.nameTreeWidget, 1, 0, 1, 1)
        self.home.addWidget(self.helpTextEdit, 0, 1, 2, 1)

    def load(self):
        soup = BeautifulSoup(open(r'Command Line Options — x265 documentation.html', encoding='utf-8'),
                             features='html.parser')
        for section_tag in soup.find_all(attrs={'class': 'section'}):
            if section_tag.h1:
                continue
            elif section_tag.h2:
                head = section_tag.h2.get_text()
            else:
                head = ''
            head = head.replace('¶', '')
            item = QTreeWidgetItem(self.nameTreeWidget)
            item.setText(0, head)
            value = {}
            for tag in section_tag.find_all(attrs={'class': 'option'}):
                name = tag.dt.code.get_text()[2:]

                header = ''.join([code.get_text() for code in tag.dt.find_all('code')]).strip()
                if header:
                    sub_item = QTreeWidgetItem(item)
                    value[name] = f'{header}\n{str(tag.dd)}'
                    sub_item.setText(0, name)
            self.data[head] = value
        '''
        with open('x265.txt', encoding='utf-8') as f:
            data = f.read()
        for name, value in (re.findall(r'\n(--[^\n]+)\n(.*?)', data, re.M)):
            self.data[name] = value
            self.nameTreeWidget.addItem(name)
        '''

    def search(self, text: str):
        for row in range(self.nameTreeWidget.topLevelItemCount()):
            top_item = self.nameTreeWidget.topLevelItem(row)
            for sub_row in range(top_item.childCount()):
                item = top_item.child(sub_row)
                print(item)
                name = item.text(0)
                if text in name:
                    item.setHidden(False)
                    top_item.setExpanded(False)
                else:
                    item.setHidden(True)
                    top_item.setExpanded(True)

    def change_row(self, item: QTreeWidgetItem):
        name = item.text(0)
        if (parent := item.mainWidget()) is None:
            self.helpTextEdit.clear()
        else:
            self.helpTextEdit.setHtml(self.data[parent.text(0)][name])


def search_command(widget: QWidget, command: str):
    if command:
        for row in range(widget.nameTreeWidget.count()):
            name = widget.nameTreeWidget.item(row).text()
            if name == command:
                widget.nameTreeWidget.setCurrentRow(row)
                break
        else:
            QMessageBox.critical(widget, '找不到命令', f'找不到{command}命令！', QMessageBox.Ok, QMessageBox.Ok)
    widget.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    parser = argparse.ArgumentParser(description="x265说明文档")
    parser.add_argument('-c', '--command', default='')
    args = parser.parse_args()
    mainWidget = MainWidget()
    search_command(mainWidget, args.command)

    sys.exit(app.exec_())
