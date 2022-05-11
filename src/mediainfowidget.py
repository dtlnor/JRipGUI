from PySide6.QtCore import QRegularExpression, QThread, QSize, QFileInfo, Qt, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QTabWidget, QGridLayout, QWidget, QLineEdit, \
    QTreeWidget, QHeaderView, QTreeWidgetItem, QToolButton, \
    QMessageBox, QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog
import json
import images
import pymediainfo
import svgs
from MyWidgets import PathPushButton, ExtGroup
from data import set_icon, FONT_SIZE, SETTINGS, LANG_UI_TXT, MEDIAINFO, shadow,\
    PATH_CODE, BASENAME_CODE, SUFFIX_CODE, FILENAME_CODE


class InfoWidget(QWidget):
    def __init__(self, path: str, info: list[dict], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.home = QGridLayout(self)
        self.pathLine = QLineEdit(self)
        self.refreshButton = QToolButton(self)
        self.infoTree = QTreeWidget(self)
        self.info = info
        self.path = path

        self.init_ui()
        self.init_language()

    def init_ui(self):
        self.home.addWidget(self.pathLine, 0, 0, 1, 1)
        self.home.addWidget(self.refreshButton, 0, 1, 1, 1)
        self.home.addWidget(self.infoTree, 1, 0, 1, 2)
        self.pathLine.setReadOnly(True)
        self.pathLine.setText(self.path)
        self.refreshButton.setIcon(set_icon(svgs.refresh))
        self.refreshButton.clicked.connect(self.reload)
        self.refreshButton.setStyleSheet('background:transparent;border:none')
        self.infoTree.setColumnCount(2)
        self.infoTree.setHeaderHidden(True)
        self.infoTree.setAutoScroll(False)
        header = self.infoTree.header()
        header.setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        header.setStretchLastSection(False)
        font = QFont(SETTINGS.fontFamily)
        font.setPixelSize(FONT_SIZE)
        self.init_font(font)

    def init_font(self, font: QFont):
        self.pathLine.setFont(font)
        self.infoTree.setFont(font)

    def init_language(self):
        self.infoTree.clear()
        self.load_info(self.info)
        self.refreshButton.setToolTip(LANG_UI_TXT.MediaInfoWidget.reload)

    def load_info(self, info: list[dict]):
        def add(data: dict, parent_item: QTreeWidgetItem):
            if type(data) == dict:
                for name, value in data.items():
                    if name in ('track_type', 'complete_name'):
                        continue
                    elif QRegularExpression(r'^\d\d_\d\d_\d\d\d\d\d$').match(name).hasMatch():
                        item = QTreeWidgetItem(parent_item)
                        time = name.replace('_', ':')
                        time = f'{time[:-3]}.{time[-3:]}'
                        item.setText(0, value)
                        item.setText(1, time)
                    elif hasattr(LANG_UI_TXT.mediaInfo, name):
                        item = QTreeWidgetItem(parent_item)
                        if type(value) in (str, int, float):
                            '''
                            if name in ('Duration',
                                        'duration',
                                        'delay',
                                        'delay_relative_to_video',
                                        'source_duration'):
                                try:
                                    seconds, m_sec = divmod(int(float(value)), 1000)
                                    hour, seconds = divmod(seconds, 3600)
                                    minute, second = divmod(seconds, 60)
                                    h = f'{hour}{LANG_UI_TXT.mediaInfo.hour}' if hour else ''
                                    m = f'{minute}{LANG_UI_TXT.mediaInfo.minute}' if minute else ''
                                    s = f'{second}{LANG_UI_TXT.mediaInfo.second}' if second \
                                        else f'0{LANG_UI_TXT.mediaInfo.second}'
                                    ms = f'{m_sec}{LANG_UI_TXT.mediaInfo.m_second}' if m_sec else ''
                                    value = f'{h} {m} {s} {ms}'.strip()
                                except ValueError:
                                    pass
                            elif name in ('stream_size', 'file_size', 'source_stream_size'):
                                try:
                                    value = get_size(float(value))
                                except ValueError:
                                    pass
                            elif name in ('overall_bit_rate', 'bit_rate'):
                                try:
                                    value = float(value)
                                    if value < 1000:
                                        value = f'{round(value, 3)} bps'
                                    elif 1000 <= value < 1000000:
                                        value = f'{round(value / 1000, 3)} Kbps'
                                    elif 1000000 <= value < 1000000000:
                                        value = f'{round(value / 1000000, 3)} Mbps'
                                    else:
                                        value = f'{round(value / 1000000000, 3)} Gbps'
                                except ValueError:
                                    pass
                            '''
                            if type(value) != str:
                                value = str(value)
                                print(value)

                            item.setText(0, getattr(LANG_UI_TXT.mediaInfo, name, name))

                            text = getattr(LANG_UI_TXT.mediaInfo, value, value)
                            item.setText(1, text)
                            if len(text) > 30:
                                item.setToolTip(1, text)
                        elif type(value) in (list, tuple):
                            item.setText(
                                0,
                                getattr(LANG_UI_TXT.mediaInfo, name, name))
                            item.setText(
                                1,
                                getattr(LANG_UI_TXT.mediaInfo, ", ".join(value), ", ".join(value)))
                        elif type(data) == dict:
                            item.setText(0, getattr(LANG_UI_TXT.mediaInfo, name))
                            add(value, item)

        if info:
            for track in info:
                top_item = QTreeWidgetItem(self.infoTree)
                key = track.get('track_type')
                top_item.setText(0, getattr(LANG_UI_TXT.mediaInfo, key, key))
                add(track, top_item)
        else:
            top_item = QTreeWidgetItem(self.infoTree)
            top_item.setText(0, LANG_UI_TXT.MediaInfoWidget.info)
        self.infoTree.expandAll()

    def reload(self):
        try:
            self.info = pymediainfo.MediaInfo.parse(self.path,
                                                    full=False,
                                                    parse_speed=SETTINGS.parseSpeed,
                                                    library_file=MEDIAINFO.absoluteFilePath()).to_data().get('tracks', [])
        except Exception as e:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                str(e),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
        else:
            self.infoTree.clear()
            self.load_info(self.info)


class MediaInfoWidget(QWidget):
    class LoadThread(QThread):
        resultSignal = Signal(tuple)

        def __init__(self):
            super().__init__()
            self.files = []

        def run(self):
            for file in self.files:
                try:
                    mi = pymediainfo.MediaInfo.parse(file.decode(encoding='utf-8'),
                                                     full=False,
                                                     parse_speed=SETTINGS.parseSpeed,
                                                     library_file=MEDIAINFO.absoluteFilePath())
                except Exception as e:
                    self.resultSignal.emit((file, str(e), False))
                else:
                    self.resultSignal.emit((file,
                                            json.dumps(mi.to_data().get('tracks', []), ensure_ascii=True),
                                            True))
            self.files.clear()

    def __init__(self, parent, /, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        from main import MainWidget
        self.mainWidget: MainWidget = parent
        self.warnings = {}
        self.partButton = QHBoxLayout()
        self.openButton = PathPushButton(QFileDialog.getOpenFileNames, ExtGroup(), True, self)
        self.avsButton = PathPushButton(QFileDialog.getSaveFileName, ExtGroup('avs'), True, self)
        self.vpyButton = PathPushButton(QFileDialog.getSaveFileName, ExtGroup('vpy'), True, self)
        self.batchAvsButton = QPushButton(self)
        self.batchVpyButton = QPushButton(self)
        self.clearButton = QPushButton(self)
        self.fileTab = QTabWidget(self)

        self.loadThread = self.LoadThread()

        self.buttons = (self.openButton, self.vpyButton, self.avsButton,
                        self.batchVpyButton, self.batchAvsButton, self.clearButton)
        self.init_ui()

    def init_ui(self):
        home = QVBoxLayout(self)
        shadow(self)
        self.setAcceptDrops(True)
        self.partButton.addWidget(self.openButton)
        self.partButton.addWidget(self.vpyButton)
        self.partButton.addWidget(self.avsButton)
        self.partButton.addWidget(self.batchVpyButton)
        self.partButton.addWidget(self.batchAvsButton)
        self.partButton.addWidget(self.clearButton)
        self.partButton.addStretch(1)
        home.setContentsMargins(10, 10, 10, 10)
        home.addLayout(self.partButton)
        home.addWidget(self.fileTab)
        self.fileTab.setMovable(True)
        self.fileTab.setTabsClosable(True)
        self.fileTab.tabCloseRequested.connect(self.close_media)
        self.fileTab.tabBar().setFixedHeight(32)

        self.openButton.select_signal.connect(self.check_mediainfo)
        self.openButton.setIcon(set_icon(svgs.open))
        self.avsButton.select_signal.connect(self.avs)
        self.avsButton.setIcon(set_icon(images.avs))
        self.avsButton.setDisabled(True)
        self.vpyButton.select_signal.connect(self.vpy)
        self.vpyButton.setIcon(set_icon(svgs.vs))
        self.vpyButton.setDisabled(True)
        self.batchAvsButton.clicked.connect(self.batch_export)
        self.batchAvsButton.setDisabled(True)
        self.batchVpyButton.clicked.connect(self.batch_export)
        self.batchVpyButton.setDisabled(True)
        self.clearButton.setIcon(set_icon(svgs.trash))
        self.clearButton.clicked.connect(self.clear)
        for i in self.buttons:
            i: QPushButton
            i.setFixedSize(128, 48)
            i.setIconSize(QSize(32, 32))

        self.loadThread.resultSignal.connect(self.add_info_widget)
        self.loadThread.finished.connect(self.load_over)

    def init_language(self):
        for button, text in zip(self.buttons, LANG_UI_TXT.MediaInfoWidget.buttons):
            button.setText(text)
        for i in range(self.fileTab.count()):
            self.fileTab.widget(i).init_language()

    def init_font(self, font: QFont):
        self.fileTab.setFont(font)
        for button in self.buttons:
            button.setFont(font)
        for i in range(self.fileTab.count()):
            self.fileTab.widget(i).init_font(font)

    def clear(self):
        self.fileTab.clear()
        self.avsButton.setDisabled(True)
        self.vpyButton.setDisabled(True)
        self.batchAvsButton.setDisabled(True)
        self.batchVpyButton.setDisabled(True)

    def check_mediainfo(self, files: tuple[str]):
        if MEDIAINFO.absoluteFilePath():
            if not self.loadThread.isRunning():
                self.openButton.setDisabled(True)
                self.loadThread.files.extend([file.encode(encoding='utf-8') for file in files])
                self.loadThread.start()
            else:
                QMessageBox.warning(self,
                                    LANG_UI_TXT.info.error,
                                    LANG_UI_TXT.info.mediainfo_is_busy,
                                    QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok)

    def add_info_widget(self, signal: tuple[bytes, str, bool]):
        file, msg, success = signal
        file = file.decode(encoding='utf-8')
        if not success:
            self.warnings[file] = msg
        else:
            msg = json.loads(msg)
            print(msg)
            widget = InfoWidget(file, msg)
            base_name = QFileInfo(file).completeBaseName()
            ext = QFileInfo(file).suffix()
            if len(base_name) > 10:
                sum_file_name = f'{base_name[:5]}..{base_name[-3:]}.{ext}'
            else:
                sum_file_name = f'{base_name}.{ext}'
            file_name = QFileInfo(file).fileName()
            self.fileTab.addTab(widget, sum_file_name)
            self.fileTab.tabBar().setToolTip(file_name)

    def load_over(self):
        self.openButton.setEnabled(True)
        if self.fileTab.count():
            self.avsButton.setEnabled(True)
            self.vpyButton.setEnabled(True)
            self.batchAvsButton.setEnabled(True)
            self.batchVpyButton.setEnabled(True)
        if self.warnings:
            msgs = [f'{file}: {msg}' for file, msg in self.warnings.items()]
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                '\n'.join(msgs),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
            self.warnings.clear()

    @staticmethod
    def replace_code(template: str, file_info: QFileInfo):
        return template. \
            replace(PATH_CODE, file_info.absoluteFilePath()). \
            replace(BASENAME_CODE, file_info.completeBaseName()). \
            replace(FILENAME_CODE, file_info.fileName()). \
            replace(SUFFIX_CODE, file_info.suffix())

    def vpy(self, files: tuple):
        try:
            with open(files[0], 'w', encoding='utf-8') as f:
                f.write(self.replace_code(SETTINGS.vpyTemplate,
                                          QFileInfo(self.fileTab.currentWidget().path)))
        except PermissionError:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                LANG_UI_TXT.info.permission,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                str(e),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(
                self,
                LANG_UI_TXT.info.success,
                LANG_UI_TXT.info.export_success,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)

    def avs(self, files: tuple):
        try:
            with open(files[0], 'w') as f:
                f.write(self.replace_code(SETTINGS.avsTemplate,
                                          QFileInfo(self.fileTab.currentWidget().path)))
        except PermissionError:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                LANG_UI_TXT.info.permission,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
        except Exception as e:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                str(e),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(
                self,
                LANG_UI_TXT.info.success,
                LANG_UI_TXT.info.export_success,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)

    def batch_export(self):
        sender = self.sender()
        paths = []
        if sender == self.batchVpyButton:
            template = SETTINGS.vpyTemplate
            ext = 'vpy'
            encoding = 'utf-8'
        else:
            template = SETTINGS.avsTemplate
            ext = 'avs'
            encoding = 'ansi'
        for n in range(self.fileTab.count()):
            widget: InfoWidget = self.fileTab.widget(n)
            if widget.path in paths:
                QMessageBox.warning(self,
                                    LANG_UI_TXT.info.error,
                                    f'"{widget.path}" {LANG_UI_TXT.info.is_repeat}!',
                                    QMessageBox.StandardButton.Cancel,
                                    QMessageBox.StandardButton.Cancel)
                return
            else:
                if QFileInfo(f'{widget.path}.{ext}').exists():
                    r = QMessageBox.question(self,
                                             LANG_UI_TXT.info.warning,
                                             f'"{widget.path}.{ext}" {LANG_UI_TXT.info.is_exist}\n{LANG_UI_TXT.info.overwritten}',
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                                             QMessageBox.StandardButton.No)
                    if r == QMessageBox.StandardButton.Cancel:
                        return
                    elif r == QMessageBox.StandardButton.Yes:
                        paths.append(widget.path)
                else:
                    paths.append(widget.path)
        errors = []
        for path in paths:
            try:
                with open(f'{path}.{ext}', 'w', encoding=encoding) as f:
                    f.write(self.replace_code(template, QFileInfo(self.fileTab.currentWidget().path)))
            except PermissionError:
                QMessageBox.warning(
                    self,
                    LANG_UI_TXT.info.error,
                    f'{LANG_UI_TXT.info.permission}\n{path}',
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
                errors.append(path)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    LANG_UI_TXT.info.error,
                    f'{str(e)}\n{path}',
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
                errors.append(path)
        if errors:
            error_paths = '\n'.join(errors)
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                f'{LANG_UI_TXT.info.error}: \n{error_paths}',
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.information(
                self,
                LANG_UI_TXT.info.success,
                LANG_UI_TXT.info.export_success,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)

    def close_media(self, index: int):
        self.fileTab.removeTab(index)
        if not self.fileTab.count():
            self.avsButton.setDisabled(True)
            self.vpyButton.setDisabled(True)
            self.batchAvsButton.setDisabled(True)
            self.batchVpyButton.setDisabled(True)

    def dragEnterEvent(self, a0) -> None:
        data = a0.mimeData()
        if data.hasUrls():
            a0.accept()
        else:
            a0.ignore()

    def dropEvent(self, a0) -> None:
        if (data := a0.mimeData()).hasUrls():
            files = tuple([url.toLocalFile() for url in data.urls()])

            self.check_mediainfo(files)

    def keyReleaseEvent(self, a0) -> None:
        if a0.modifiers() == Qt.KeyboardModifier.ControlModifier and a0.key() == Qt.Key.Key_O:
            if self.openButton.isEnabled():
                self.openButton.click()
        elif a0.modifiers() == Qt.KeyboardModifier.ControlModifier and a0.key() == Qt.Key.Key_Q:
            if self.fileTab.count():
                self.fileTab.removeTab(self.fileTab.currentIndex())
