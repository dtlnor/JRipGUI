# from PyQt5 import QWinTaskbarButton
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtWidgets import QCheckBox, QListWidgetItem, QStackedLayout
from MyWidgets import *
from aboutwidget import AboutWidget
from commandwidget import CommandWidget
from data import *
from encodewidget import EncodeWidget
from mediainfowidget import MediaInfoWidget
from settingwidget import SettingWidget
from toolswidget import ToolsWidget


class MainWidget(QWidget):
    def __init__(self, app: QApplication):
        super().__init__()
        self.app = app
        self.language_files: dict[str, QFile] = {}
        self.functionListWidget = FunctionListWidget(self)
        self.home = QHBoxLayout(self)

        '''
        self.taskButton = QWinTaskbarButton(self)
        self.taskProgress = self.taskButton.progress()
        '''

        self.partWidgets = QStackedLayout()
        self.commandWidget = CommandWidget(self)
        self.mediaInfoWidget = MediaInfoWidget(self)
        self.toolsWidget = ToolsWidget(self)
        self.encodeWidget = EncodeWidget(self)
        self.settingWidget = SettingWidget(self)
        self.aboutWidget = AboutWidget()

        self.alwaysOnTopCheckBox = QCheckBox(self)
        self.aboutButton = QToolButton(self)

        self.mainWidgets = (
            self.commandWidget,
            self.mediaInfoWidget,
            self.toolsWidget,
            self.encodeWidget,
            self.settingWidget,
            self.aboutWidget)
        self.init_ui()

    def init_ui(self):
        self.setContentsMargins(0, 0, 0, 0)
        self.setMinimumSize(950, 800)
        self.setWindowIcon(QIcon('icon.ico'))
        palette = QPalette()
        palette.setBrush(self.backgroundRole(), QColor('#FFFBFF'))
        self.setPalette(palette)
        move_to_middle(self)
        self.home.setContentsMargins(0, 0, 0, 0)
        self.home.setSpacing(0)

        self.aboutButton.setIcon(set_icon(svgs.about))
        self.aboutButton.clicked.connect(self.aboutWidget.show)

        # self.functionListWidget.addItems(('',) * 5)
        for index, svg in zip(range(5), (svgs.command, svgs.media, svgs.tools, svgs.encode, svgs.setting)):
            item = QListWidgetItem()
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
            widget = QWidget(self)
            layout = QHBoxLayout(widget)

            svg_widget = QSvgWidget(self)
            svg_widget.load(svg)
            svg_widget.setFixedSize(64, 64)
            layout.addWidget(svg_widget, alignment=Qt.AlignmentFlag.AlignCenter)
            self.functionListWidget.addItem(item)
            self.functionListWidget.setItemWidget(item, widget)

            # self.functionListWidget.item(index).setIcon(set_icon(svg))
        self.functionListWidget.setCurrentRow(0)
        self.functionListWidget.setFixedWidth(140)
        self.functionListWidget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        part_about = QHBoxLayout()
        self.functionListWidget.setLayout(QVBoxLayout())
        self.functionListWidget.layout().addStretch(1)
        self.functionListWidget.layout().addLayout(part_about)
        part_about.addWidget(self.alwaysOnTopCheckBox)
        part_about.addWidget(self.aboutButton)
        self.functionListWidget.currentRowChanged.connect(self.partWidgets.setCurrentIndex)

        self.alwaysOnTopCheckBox.stateChanged.connect(self.always_on_top)

        self.home.addWidget(self.functionListWidget)
        self.home.addLayout(self.partWidgets)

        self.partWidgets.addWidget(self.commandWidget)
        self.partWidgets.addWidget(self.mediaInfoWidget)
        self.partWidgets.addWidget(self.toolsWidget)
        self.partWidgets.addWidget(self.encodeWidget)
        self.partWidgets.addWidget(self.settingWidget)

    def init_language(self):
        for n, text in enumerate(LANG_UI_TXT.mainWidget.menu):
            self.functionListWidget.item(n).setText(text)
        self.setWindowTitle(LANG_UI_TXT.windowsTitle)

        self.alwaysOnTopCheckBox.setText(LANG_UI_TXT.button.Always_on_top)
        self.aboutButton.setToolTip(LANG_UI_TXT.mainWidget.about)

    def load_language(self, languages: list[tuple[str, str, QFile]]) -> bool:
        for (language_name, language_code, file) in languages:
            self.settingWidget.cmdLanguageComboBox.addItem(language_name)
            self.settingWidget.languageComboBox.addItem(language_name)
            self.language_files[language_code] = file

        for (language_name, language_code, file) in languages:
            if SETTINGS.language == language_code:
                self.settingWidget.languageComboBox.setCurrentText(language_name)
                self.set_ui_language(language_code, init_length=False)
                break
        else:
            return False

        for (language_name, language_code, file) in languages:
            if SETTINGS.cmdLanguage == language_code:
                self.settingWidget.cmdLanguageComboBox.setCurrentText(language_name)
                self.set_cmd_language(language_code, init_length=False)
                self.commandWidget.close_project(reset_recent=False)
                return True
        else:
            self.commandWidget.close_project(reset_recent=False)
            return False

    def init_font(self, font: QFont):
        self.functionListWidget.setFont(font)
        self.alwaysOnTopCheckBox.setFont(font)

    def set_font(self, font: QFont):
        self.app.setFont(font)
        self.commandWidget.init_font(font)
        self.settingWidget.init_font(font)
        self.mediaInfoWidget.init_font(font)
        self.toolsWidget.init_font(font)
        self.encodeWidget.init_font(font)
        self.aboutWidget.init_font(font)
        self.init_font(font)

    def set_ui_language(self, language_code: str, *, init_length: bool = True):
        if file := self.language_files.get(language_code):
            data = pickle.loads(file.readAll().data()).get('ui_language')
            file.seek(0)
            LANG_UI_TXT.reset()
            LANG_UI_TXT.load(data)
            SETTINGS.language = language_code
            self.commandWidget.init_language(init_length=init_length)
            self.mediaInfoWidget.init_language()
            self.settingWidget.init_language()
            self.toolsWidget.init_language()
            self.encodeWidget.init_language()
            self.aboutWidget.init_language()
            self.init_language()

    def set_cmd_language(self, language_code: str, *, init_length: bool = True):
        if file := self.language_files.get(language_code):
            data = pickle.loads(file.readAll().data()).get('cmd_language')
            file.seek(0)
            CMD_LANG_TXT.reset()
            CMD_LANG_TXT.load(data)
            SETTINGS.cmdLanguage = language_code
            self.commandWidget.init_cmd_language(init_length=init_length)

    def always_on_top(self, state: int):
        if state == 0:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, False)
        else:
            self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.show()
    '''
    def showEvent(self, e) -> None:
        super().showEvent(e)
        
        if not self.taskButton.window():
            self.taskButton.setWindow(self.windowHandle())
            self.taskProgress.show()
        
    '''
    def closeEvent(self, e):
        self.encodeWidget.taskOperationWidget.tasks.save()
        if self.commandWidget.winTitleChange:
            while True:
                answer = QMessageBox.question(
                    self,
                    LANG_UI_TXT.info.not_saved,
                    LANG_UI_TXT.info.save_ask,
                    QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Ok)
                if answer == QMessageBox.StandardButton.Ok:
                    self.commandWidget.saveButton.click()
                    if self.commandWidget.saveSuccess:
                        break
                elif answer == QMessageBox.StandardButton.Cancel:
                    e.ignore()
                    return
                else:
                    break
        if not self.encodeWidget.taskOperationWidget.runButton.isEnabled():
            answer = QMessageBox.question(
                self,
                LANG_UI_TXT.info.encoding,
                LANG_UI_TXT.info.close_anyway,
                buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                defaultButton=QMessageBox.StandardButton.Yes)
            if answer == QMessageBox.StandardButton.Yes:
                self.encodeWidget.taskOperationWidget.abort_all()
                self.encodeWidget.taskOperationWidget.save_tasks()
            else:
                e.ignore()
                return
        for file in self.language_files.values():
            file.close()


