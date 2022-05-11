from PySide6.QtCore import QRect, Qt, QFileInfo, Signal, QUrl, QSize, QStringListModel, QProcess, QThread, \
    QRegularExpression
from PySide6.QtGui import QColor, QPainter, QFont, QDesktopServices, QDropEvent, QDragEnterEvent, QFontMetrics,\
    QKeyEvent, QPalette, QPaintEvent, QDragMoveEvent, QWheelEvent, QRegularExpressionValidator
from PySide6.QtWidgets import QWidget, QPushButton, QListWidget, QLineEdit, QFormLayout, QVBoxLayout, QHBoxLayout, \
    QFileDialog, QMessageBox, QGroupBox, QPlainTextEdit, QToolButton, QCompleter, QLabel, QComboBox

from data import set_icon, shadow
import svgs
from data import LANG_UI_TXT, CORE, X265, VSPIPE, AVS4X26X, COMMANDS, SETTINGS


class Ext:
    def __init__(self, *all_ext: str):
        if all_ext:
            if all([isinstance(ext, str) for ext in all_ext]):
                self.__group = all_ext
            else:
                raise TypeError('*all_ext必须是字符串')
        else:
            raise ValueError('缺少参数*all_ext')

    def __str__(self) -> str:
        return f'Ext{self.__group}'

    def __getitem__(self, item) -> str:
        return self.__group[item]

    def __len__(self) -> int:
        return len(self.__group)

    def __iter__(self):
        return self.__group.__iter__()


class ExtGroup:
    def __init__(self, *groups):
        self.__groups: list[Ext] = []
        self.__allExt: list[str] = []
        if groups:
            if all([isinstance(group, (str, Ext)) for group in groups]):
                self.extend(groups)
            else:
                raise TypeError('*group必须为字符串或Ext')

    def __iter__(self):
        return self.__groups.__iter__()

    def __getitem__(self, item: int) -> Ext:
        return self.__groups[item]

    def __len__(self) -> int:
        return len(self.__groups)

    def set_ext(self, groups: tuple):
        self.clear()
        self.extend(groups)

    def extend(self, groups: tuple):
        if all([isinstance(group, (str, Ext)) for group in groups]):
            for group in groups:
                if isinstance(group, Ext):
                    self.__groups.append(group)
                    self.__allExt.extend(group)
                elif isinstance(group, str):
                    self.__groups.append(Ext(group))
                    self.__allExt.append(group)
                else:
                    raise TypeError('*groups必须是Ext或字符')

    @property
    def all_ext(self) -> list:
        return self.__allExt

    def clear(self):
        self.__groups.clear()
        self.__allExt.clear()


class PathLineEdit(QLineEdit):
    def __init__(self, dialog_type, ext_group: ExtGroup = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if dialog_type not in (QFileDialog.getSaveFileName,
                               QFileDialog.getOpenFileName,
                               QFileDialog.getExistingDirectory):
            raise TypeError('dialog_type 必须是QFileDialog.getSaveFileName, QFileDialog.getOpenFileName,'
                            ' QFileDialog.getExistingDirectory中的一种')
        self.__dialogType = dialog_type
        self.home = QHBoxLayout(self)
        self.exploreButton = QToolButton(self)
        self.selectButton = QToolButton(self)
        self.clearButton = QToolButton(self)
        self.extGroup = ExtGroup() if ext_group is None else ext_group

        self.init_ui()

    def init_ui(self):
        self.setAcceptDrops(True)
        self.setTextMargins(0, 0, 50, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setReadOnly(True)
        self.textChanged.connect(self.hide_button)
        if self.__dialogType != QFileDialog.getSaveFileName:
            self.textChanged.connect(self.hide_explore_button)

        self.exploreButton.setIcon(set_icon(svgs.folder))
        self.exploreButton.setIconSize(QSize(16, 16))
        self.exploreButton.setStyleSheet('background:transparent;border:none')
        self.exploreButton.setContentsMargins(0, 0, 0, 0)
        self.exploreButton.clicked.connect(self.explore)
        self.exploreButton.hide()
        self.exploreButton.setCursor(Qt.CursorShape.PointingHandCursor)

        self.clearButton.setIcon(set_icon(svgs.line_clear))
        self.clearButton.setIconSize(QSize(16, 16))
        self.clearButton.setStyleSheet('background:transparent;border:none')
        self.clearButton.setContentsMargins(0, 0, 0, 0)
        self.clearButton.clicked.connect(self.clear)
        self.clearButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clearButton.hide()

        self.selectButton.clicked.connect(self.get_file)
        self.selectButton.setContentsMargins(0, 0, 0, 0)
        self.selectButton.setText('..')
        self.selectButton.setFixedWidth(16)
        self.selectButton.setCursor(Qt.CursorShape.PointingHandCursor)
        self.selectButton.setStyleSheet('background:transparent;border:none')

        self.home.addStretch(1)
        self.home.addWidget(self.exploreButton, alignment=Qt.AlignmentFlag.AlignCenter)
        self.home.addWidget(self.selectButton, alignment=Qt.AlignmentFlag.AlignBottom)
        self.home.addWidget(self.clearButton, alignment=Qt.AlignmentFlag.AlignCenter)
        self.home.setContentsMargins(0, 0, 0, 0)
        self.home.setSpacing(0)

    def setFont(self, font: QFont) -> None:
        super().setFont(font)
        self.selectButton.setFont(font)

    @property
    def dialog_type(self):
        return self.__dialogType

    @dialog_type.setter
    def dialog_type(self, dialog_type):
        if dialog_type in (QFileDialog.getOpenFileName,
                           QFileDialog.getSaveFileName):
            self.__dialogType = dialog_type
        elif dialog_type == QFileDialog.getExistingDirectory:
            self.__dialogType = dialog_type
            self.extGroup.clear()
        else:
            raise TypeError(
                'dialog_type must be QFileDialog.getOpenFileName, '
                'QFileDialog.getSaveFileName, QFileDialog.getExistingDirectory')

    def hide_button(self, text: str):
        if text:
            self.clearButton.show()
        else:
            self.clearButton.hide()

    def hide_explore_button(self, text: str):
        if text:
            self.exploreButton.show()
        else:
            self.exploreButton.hide()

    @property
    def dir_path(self):
        if self.__dialogType in (QFileDialog.getOpenFileName, QFileDialog.getSaveFileName):
            return QFileInfo(self.text()).absoluteDir().path()
        else:
            return self.text()

    def explore(self):
        if not QDesktopServices.openUrl(QUrl(self.dir_path)):
            QMessageBox.warning(self,
                                LANG_UI_TXT.info.error,
                                LANG_UI_TXT.info.fail_to_open_file,
                                QMessageBox.StandardButton.Ok,
                                QMessageBox.StandardButton.Ok)

    def get_file(self):
        if len(self.extGroup) <= 1 or self.__dialogType == QFileDialog.getSaveFileName:
            all_type = []
        else:
            all_type = [f"{LANG_UI_TXT.fileDialog.available} (*.{';*.'.join(self.extGroup.all_ext)})"]

        for group in self.extGroup:
            if (group_len := len(group)) > 1:
                if self.__dialogType == QFileDialog.getSaveFileName:
                    all_type.append(f'{getattr(LANG_UI_TXT.fileType, group[0])} (*.{group[0]})')
                else:
                    all_type.append(f'{getattr(LANG_UI_TXT.fileType, group[0])} (*.{";*.".join(group)})')
            elif group_len == 1:
                all_type.append(f'{getattr(LANG_UI_TXT.fileType, group[0])} (*.{group[0]})')
            else:
                all_type.append(f'(*.*)')
        if self.__dialogType == QFileDialog.getSaveFileName:
            file = self.__dialogType(
                self,
                LANG_UI_TXT.fileDialog.save,
                SETTINGS.recentDir,
                f'{";;".join(all_type)}')[0]
        elif self.__dialogType == QFileDialog.getOpenFileName:
            file = self.__dialogType(
                self,
                LANG_UI_TXT.fileDialog.open,
                SETTINGS.recentDir,
                f"{';;'.join(all_type)}")[0]
        elif self.__dialogType == QFileDialog.getExistingDirectory:
            file = self.__dialogType(self,
                                     LANG_UI_TXT.fileDialog.open,
                                     SETTINGS.recentDir)
        else:
            file = ''
        if file:
            SETTINGS.recentDir = self.dir_path
            self.setText(file)

    def setText(self, a0: str) -> None:
        super().setText(a0)
        self.setToolTip(a0)

    def clear(self):
        super().clear()
        self.setToolTip('')

    def dragEnterEvent(self, event: QDragEnterEvent):
        data = event.mimeData()
        if data.hasUrls():
            event.accept()
        else:
            self.setAcceptDrops(False)

    def dropEvent(self, event: QDropEvent):
        data = event.mimeData()
        if len(urls := data.urls()) == 1:
            url = urls[0].toLocalFile()
            if QFileInfo(url).suffix().lower() in self.extGroup.all_ext or not self.extGroup.all_ext:
                if self.__dialogType == QFileDialog.getSaveFileName:
                    r = QMessageBox.question(
                        self,
                        LANG_UI_TXT.fileDialog.save,
                        f'{url}{LANG_UI_TXT.info_is_exist}\n{LANG_UI_TXT.continue_anyway}',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.Yes)
                    if r == QMessageBox.StandardButton.Yes:
                        self.setText(url)
                else:
                    self.setText(url)
            else:
                QMessageBox.warning(
                    self,
                    LANG_UI_TXT.info.file_extension_error,
                    f'{LANG_UI_TXT.info.not_support}{", ".join(self.extGroup.all_ext)}',
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                LANG_UI_TXT.info.too_many_files,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)

    def set_ext(self, ext_group: ExtGroup):
        self.extGroup = ext_group


class CommandComboBox(QComboBox):
    def wheelEvent(self, e: QWheelEvent) -> None:
        y = e.angleDelta().y()
        if y != 0:
            last = -1 if y > 0 else self.count()
            step = y // abs(y)
            new_index = self.currentIndex() - step
            if new_index in range(self.count()) and self.view().isRowHidden(new_index):
                for row in range(new_index, last, -step):
                    if not self.view().isRowHidden(row):
                        self.setCurrentIndex(row)
                        break
                else:
                    e.ignore()
            else:
                super().wheelEvent(e)


class FileListWidget(QListWidget):
    class Back(QWidget):
        def __init__(self, color: str):
            super().__init__()
            self.buttonBox = QVBoxLayout(self)
            self.setContentsMargins(0, 0, 0, 0)
            self.buttonBox.setContentsMargins(0, 0, 0, 0)
            self.setFixedWidth(24)
            self.__color = color

        def paintEvent(self, e: QPaintEvent):
            painter = QPainter(self)
            painter.fillRect(e.rect(), QColor(self.__color))

    def __init__(self, dialog_type=None, ext_group: ExtGroup = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if dialog_type not in (QFileDialog.getSaveFileName,
                               QFileDialog.getOpenFileName,
                               QFileDialog.getOpenFileNames,
                               QFileDialog.getExistingDirectory):
            raise TypeError('dialog_type 必须是QFileDialog.getSaveFileName, QFileDialog.getOpenFileName,'
                            ' QFileDialog.getExistingDirectory中的一种')
        self.extGroup = ExtGroup() if ext_group is None else ext_group
        self.__dialogType = dialog_type
        self.home = QHBoxLayout(self)
        self.back = self.Back('#ffffff')
        self.addButton = QToolButton(self)
        self.removeButton = QToolButton(self)
        self.clearButton = QToolButton(self)
        self.topButton = QToolButton(self)
        self.upButton = QToolButton(self)
        self.downButton = QToolButton(self)
        self.bottomButton = QToolButton(self)
        self.init_ui()

    def init_ui(self):
        self.setViewportMargins(24, 0, 0, 0)
        self.setContentsMargins(0, 0, 0, 0)
        self.setDragDropMode(QListWidget.DragDropMode.DragDrop)
        self.setDefaultDropAction(Qt.DropAction.MoveAction)
        self.back.buttonBox.addWidget(self.addButton, 1, Qt.AlignmentFlag.AlignCenter)
        self.back.buttonBox.addWidget(self.removeButton, 1, Qt.AlignmentFlag.AlignCenter)
        self.back.buttonBox.addWidget(self.clearButton, 1, Qt.AlignmentFlag.AlignCenter)
        self.back.buttonBox.addWidget(self.topButton, 1, Qt.AlignmentFlag.AlignCenter)
        self.back.buttonBox.addWidget(self.upButton, 1, Qt.AlignmentFlag.AlignCenter)
        self.back.buttonBox.addWidget(self.downButton, 1, Qt.AlignmentFlag.AlignCenter)
        self.back.buttonBox.addWidget(self.bottomButton, 1, Qt.AlignmentFlag.AlignCenter)
        self.back.buttonBox.addStretch(1)
        self.back.setContentsMargins(0, 0, 0, 0)
        self.home.setContentsMargins(0, 0, 0, 0)
        self.home.addWidget(self.back, 1, Qt.AlignmentFlag.AlignLeft)
        self.setStyleSheet(
            'QToolButton{border:none;background-color:white;padding:0}'
            'QToolButton:hover{background-color:#f0f0f0}')
        self.addButton.setIcon(set_icon(svgs.new))
        self.removeButton.setIcon(set_icon(svgs.remove))
        self.clearButton.setIcon(set_icon(svgs.clear))
        self.topButton.setIcon(set_icon(svgs.top))
        self.upButton.setIcon(set_icon(svgs.up))
        self.downButton.setIcon(set_icon(svgs.down))
        self.bottomButton.setIcon(set_icon(svgs.bottom))
        self.addButton.clicked.connect(self.add)
        self.removeButton.clicked.connect(self.remove)
        self.clearButton.clicked.connect(self.clear)
        self.topButton.clicked.connect(self.top)
        self.upButton.clicked.connect(self.up)
        self.downButton.clicked.connect(self.down)
        self.bottomButton.clicked.connect(self.bottom)

    def init_language(self):
        self.addButton.setToolTip(LANG_UI_TXT.button.add)
        self.removeButton.setToolTip(LANG_UI_TXT.button.remove)
        self.clearButton.setToolTip(LANG_UI_TXT.button.clear)
        self.topButton.setToolTip(LANG_UI_TXT.button.top)
        self.upButton.setToolTip(LANG_UI_TXT.button.up)
        self.downButton.setToolTip(LANG_UI_TXT.button.down)
        self.bottomButton.setToolTip(LANG_UI_TXT.button.bottom)

    def set_ext(self, ext_group: ExtGroup):
        self.extGroup = ext_group

    def add(self):
        if len(self.extGroup) <= 1 or self.__dialogType == QFileDialog.getSaveFileName:
            all_type = []
        else:
            all_type = [f"{LANG_UI_TXT.fileDialog.available} (*.{';*.'.join(self.extGroup.all_ext)})"]

        for group in self.extGroup:
            if (group_len := len(group)) > 1:
                if self.__dialogType == QFileDialog.getSaveFileName:
                    all_type.append(f'{getattr(LANG_UI_TXT.fileType, group[0])} (*.{group[0]})')
                else:
                    all_type.append(f'{getattr(LANG_UI_TXT.fileType, group[0])} (*.{";*.".join(group)})')
            elif group_len == 1:
                all_type.append(f'{getattr(LANG_UI_TXT.fileType, group[0])} (*.{group[0]})')
            else:
                all_type.append(f'(*.*)')
        if self.__dialogType == QFileDialog.getSaveFileName:
            files = self.__dialogType(
                self,
                LANG_UI_TXT.fileDialog.save,
                SETTINGS.recentDir,
                f'{";;".join(all_type)}')[0]
            files = [files] if files else []
        else:
            files = self.__dialogType(
                self,
                LANG_UI_TXT.fileDialog.open,
                SETTINGS.recentDir,
                f"{';;'.join(all_type)}")[0]
        if self.__dialogType != QFileDialog.getOpenFileNames:
            files = tuple(files) if files else ()
        path = SETTINGS.recentDir
        for path in files:
            for n in range(self.count()):
                if self.item(n).text() == path:
                    a = QMessageBox.question(
                        self,
                        LANG_UI_TXT.info.file_repeat,
                        f'"{path}"\n{LANG_UI_TXT.info.is_repeat}\n{LANG_UI_TXT.info.continue_anyway}',
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No)
                    if a == QMessageBox.StandardButton.Yes:
                        self.addItem(path)
                    break
            else:
                self.addItem(path)
        SETTINGS.recentDir = self.dir_path(path)
        self.setCurrentRow(self.count() - 1)

    def remove(self):
        self.removeItemWidget(self.takeItem(self.currentRow()))

    def top(self):
        row = self.currentRow()
        if row > 0:
            item = self.takeItem(row)
            self.insertItem(0, item)
            self.setCurrentItem(item)

    def up(self):
        row = self.currentRow()
        if row > 0:
            item = self.takeItem(row)
            self.insertItem(row - 1, item)
            self.setCurrentItem(item)

    def down(self):
        row = self.currentIndex().row()
        if row < self.count() - 1:
            item = self.takeItem(row)
            self.insertItem(row + 1, item)
            self.setCurrentItem(item)

    def bottom(self):
        row = self.currentRow()
        if row < self.count() - 1:
            item = self.takeItem(row)
            self.addItem(item)
            self.setCurrentItem(item)

    def dir_path(self, path: str) -> str:
        if self.__dialogType in (QFileDialog.getOpenFileName,
                                 QFileDialog.getSaveFileName,
                                 QFileDialog.getOpenFileNames):
            return QFileInfo(path).absoluteDir().path()
        else:
            return path

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.source() == self:
            e.accept()
        elif e.mimeData().hasUrls():
            e.accept()

    def dragMoveEvent(self, e: QDragMoveEvent):
        super().dragMoveEvent(e)
        if e.mimeData().hasUrls():
            e.accept()

    def dropEvent(self, e: QDropEvent):
        if self.count() == 0:
            row = 0
        else:
            item = self.itemAt(e.position().toPoint())
            if item:
                row = self.row(item)
            else:
                row = self.count()
        if e.source() == self:
            item = self.takeItem(self.currentRow())
            self.insertItem(row, item)
        elif e.mimeData().hasUrls():
            has_error = []
            files = [i.toLocalFile() for i in e.mimeData().urls()]
            for n, i in enumerate(sorted(files)):
                if QFileInfo(i).suffix().lower() in self.extGroup.all_ext or not self.extGroup.all_ext:
                    self.insertItem(row + n, i)
                else:
                    has_error.append(i)
            if has_error:
                text = "\n".join(has_error)
                QMessageBox.warning(
                    self,
                    LANG_UI_TXT.info.file_extension_error,
                    f'{LANG_UI_TXT.info.file_below_is_not_supported}\n{text}',
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)

    def keyReleaseEvent(self, a0: QKeyEvent) -> None:
        if a0.key() == Qt.Key.Key_Delete:
            self.remove()


class PathPushButton(QPushButton):
    select_signal = Signal(tuple)

    def __init__(self, dialog_type=None, ext_group: ExtGroup = None, at_once: bool = True, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if dialog_type not in (QFileDialog.getSaveFileName,
                               QFileDialog.getOpenFileName,
                               QFileDialog.getOpenFileNames,
                               QFileDialog.getExistingDirectory):
            raise TypeError('dialog_type 必须是QFileDialog.getSaveFileName, QFileDialog.getOpenFileName,'
                            ' QFileDialog.getOpenFileNames, QFileDialog.getExistingDirectory中的一种')
        self.__dialogType = dialog_type
        self.extGroup = ExtGroup() if ext_group is None else ext_group
        if at_once:
            self.clicked.connect(self.select_file)
        else:
            self.clicked.connect(self.send_func)

    def get_all(self) -> list:
        if len(self.extGroup) <= 1 or self.__dialogType == QFileDialog.getSaveFileName:
            all_type = []
        else:
            all_type = [f"{LANG_UI_TXT.fileDialog.available} (*.{';*.'.join(self.extGroup.all_ext)})"]

        for group in self.extGroup:
            first_ext = group[0]
            if (group_len := len(group)) > 1:
                if self.__dialogType == QFileDialog.getSaveFileName:
                    all_type.append(f'{getattr(LANG_UI_TXT.fileType, first_ext, first_ext)} (*.{first_ext})')
                else:
                    all_type.append(f'{getattr(LANG_UI_TXT.fileType, first_ext, first_ext)} (*.{";*.".join(group)})')
            elif group_len == 1:
                all_type.append(f'{getattr(LANG_UI_TXT.fileType, first_ext, first_ext)} (*.{first_ext})')
            else:
                all_type.append(f'(*.*)')
        return all_type

    def dir_path(self, path: str) -> str:
        if self.__dialogType in (QFileDialog.getOpenFileName,
                                 QFileDialog.getSaveFileName,
                                 QFileDialog.getOpenFileNames):
            return QFileInfo(path).absoluteDir().path()
        else:
            return path

    def select_file(self):
        all_type = self.get_all()
        if self.__dialogType == QFileDialog.getSaveFileName:
            title = LANG_UI_TXT.fileDialog.save
        else:
            title = LANG_UI_TXT.fileDialog.open

        files = self.__dialogType(
                self,
                title,
                SETTINGS.recentDir,
                f'{";;".join(all_type)}')[0]

        if self.__dialogType == QFileDialog.getOpenFileNames:
            files = tuple(files)
        else:
            files = (files,) if files else ()
        if files:
            SETTINGS.recentDir = self.dir_path(files[-1])
            self.select_signal.emit(files)

    def send_func(self):
        all_type = self.get_all()
        self.select_signal.emit((self.__dialogType, f"{';;'.join(all_type)}"))


class CodeEditor(QPlainTextEdit):
    class CodeType:
        Other = 0
        Vpy = 1
        Avs = 2

    class NumberBar(QWidget):
        def __init__(self, editor, *args, **kwargs):
            super().__init__(*args, **kwargs)
            editor: CodeEditor
            self.font = QFont()
            self.editor = editor
            self.editor.blockCountChanged.connect(self.update_width)
            self.editor.updateRequest.connect(self.update_contents)
            self.numberBarColor = QColor("#e8e8e8")
            self.update_width()

        def init_font(self, font: QFont):
            self.font.setFamily(font.family())
            self.font.setPixelSize(font.pixelSize())
            self.update_width()

        def paintEvent(self, event: QPaintEvent):
            painter = QPainter(self)
            painter.fillRect(event.rect(), self.numberBarColor)
            painter.setFont(self.font)
            document = self.editor.document()
            for block_number in range(document.blockCount()):
                block = document.findBlockByNumber(block_number)
                block_top = int(self.editor.blockBoundingGeometry(block).translated(self.editor.contentOffset()).top())
                if block_number == self.editor.textCursor().blockNumber():
                    self.font.setBold(True)
                    painter.setPen(QColor("#000000"))
                else:
                    self.font.setBold(False)
                    painter.setPen(QColor("#717171"))
                paint_rect = QRect(
                    0,
                    block_top,
                    self.width(),
                    self.editor.fontMetrics().height())
                painter.drawText(paint_rect, Qt.AlignmentFlag.AlignCenter, str(block_number + 1))

        def update_width(self):
            count = self.editor.blockCount()
            if 0 <= count < 99:
                width = self.fontMetrics().horizontalAdvance('999')
            else:
                width = self.fontMetrics().horizontalAdvance(str(count * 10))
            self.setFixedWidth(width)
            self.editor.setViewportMargins(width, 0, 0, 0)

        def update_contents(self, rect: QRect, dy: int):
            if dy:
                self.scroll(0, dy)
            else:
                self.update(0, rect.y(), self.width(), rect.height())
            if rect.contains(self.editor.viewport().rect()):
                self.font.setStyle(QFont.Style.StyleNormal)
                self.update_width()

    def __init__(self, code_type: int = CodeType.Other, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.home = QHBoxLayout()
        self.codeType = code_type
        self.number_bar = self.NumberBar(self)
        self.model = QStringListModel()
        self.plugins: dict[str, list] = {}
        self.completer = QCompleter(self.model, self)
        self.completer.activated.connect(self.insert_text)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setWrapAround(False)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        self.textChanged.connect(self.show_selecter)
        self.cursorPositionChanged.connect(self.cursor_change)
        self.setLayout(self.home)
        self.home.setContentsMargins(0, 0, 0, 0)
        self.home.addWidget(self.number_bar)
        self.home.addStretch(1)
        self.init_plugins()

    def init_font(self, font: QFont):
        self.setFont(font)
        self.number_bar.init_font(font)

    def init_plugins(self):
        self.plugins.clear()
        if self.codeType == self.CodeType.Vpy:
            for data in CORE.get_plugins().values():
                data: dict
                funcs: list[str] = []
                for func_name, pars in data['functions'].items():
                    par_names = ', '.join([par.split(":", 1)[0] for par in pars.split(";") if par.split(":", 1)[0]])
                    funcs.append(f'{func_name}({par_names})')
                self.plugins[data['namespace']] = funcs

    def set_code_type(self, code_type: int):
        if code_type in range(3):
            self.codeType = code_type
            self.init_plugins()
        else:
            raise ValueError('code_type必须是0~2的整数')

    def insert_text(self, text: str):
        pre = self.completer.completionPrefix()
        self.insertPlainText(text[len(pre):])
        self.completer.popup().hide()

    def cursor_change(self):
        if self.codeType == self.CodeType.Vpy:
            if (popup := self.completer.popup()).isVisible():
                popup.hide()

    def show_selecter(self):
        if self.codeType == self.CodeType.Vpy:
            cursor = self.textCursor()
            block = cursor.block()
            text = block.text()[:cursor.positionInBlock()]

            if text:
                last = []
                pre = []
                start = False
                for char in text[::-1]:
                    if not char.isalnum():
                        if char == '.' and not start:
                            start = True
                        else:
                            break
                    else:
                        if start:
                            last.append(char)
                        else:
                            pre.append(char)
                pre = ''.join(reversed(pre))
                popup = self.completer.popup()
                if not last and pre and 'core'[:len(pre)] == pre:
                    self.model.setStringList(['core'])
                    length = QFontMetrics(popup.font()).horizontalAdvance('core')
                    self.completer.setCompletionPrefix(pre)
                    cursor_rect = self.cursorRect()
                    cursor_rect.setWidth(length + 30)
                    self.completer.complete(cursor_rect)
                elif last:
                    last = ''.join(reversed(last))
                    if last.lower() in ('vs', 'vapoursynth'):
                        pars = ['core', 'get_core(threads=0, add_cache=True)', 'set_message_handler(handler_func)',
                                'get_outputs()', 'get_output(index=0)', 'clear_output(index = 0)',
                                'clear_outputs()', 'construct_signature(signature, injected=None)']
                    elif last.lower() == 'core':
                        pars = list(self.plugins.keys())
                    elif last in self.plugins:
                        pars = self.plugins[last]
                    else:
                        pars = None
                    if pars:
                        self.model.setStringList(sorted(pars))
                        length = [QFontMetrics(popup.font()).horizontalAdvance(n) for n in pars]
                        self.completer.setCompletionPrefix(pre)
                        cursor_rect = self.cursorRect()
                        cursor_rect.setWidth(max(length) + 30)

                        self.completer.complete(cursor_rect)

                    else:
                        self.completer.popup().hide()
                else:
                    self.completer.popup().hide()
            else:
                self.completer.popup().hide()

    def keyPressEvent(self, e: QKeyEvent) -> None:
        if self.completer.popup().isVisible():
            if e.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return):
                if data := self.completer.popup().currentIndex().data():
                    self.insert_text(data)
            else:
                super().keyPressEvent(e)
        else:
            super().keyPressEvent(e)


class CommandLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setClearButtonEnabled(True)


class ColorFormLayout(QGroupBox):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form = QFormLayout(self)
        self.setContentsMargins(0, 0, 0, 0)
        self.form.setSpacing(5)
        shadow(self)


class BatchExportWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.home = QVBoxLayout()
        self.confirmBox = QHBoxLayout()
        self.inputLine = FileListWidget(QFileDialog.getOpenFileNames, ExtGroup('vpy', 'avs', 'yuv'))
        self.outputVideoList = FileListWidget(QFileDialog.getSaveFileName, ExtGroup('265'))
        self.outputBatLine = PathLineEdit(QFileDialog.getSaveFileName, ExtGroup('bat'), self)
        self.exportButton = QPushButton(self)
        self.cancelButton = QPushButton(self)

        self.init_ui()

    def init_ui(self):
        self.setMinimumWidth(450)
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(255, 255, 255))
        self.setPalette(palette)
        self.setLayout(self.home)

        self.home.addWidget(QLabel(self))
        self.home.addWidget(self.inputLine)
        self.home.addWidget(QLabel(self))
        self.home.addWidget(self.outputVideoList)
        self.home.addWidget(QLabel(self))
        self.home.addWidget(self.outputBatLine)
        self.home.addLayout(self.confirmBox)

        self.confirmBox.addStretch(1)
        self.confirmBox.addWidget(self.exportButton)
        self.confirmBox.addWidget(self.cancelButton)

        self.inputLine.currentItemChanged.connect(self.change_row)
        self.outputVideoList.currentItemChanged.connect(self.change_row)
        self.exportButton.clicked.connect(self.export_code)
        self.cancelButton.clicked.connect(self.hide)

    def init_language(self):
        self.setWindowTitle(LANG_UI_TXT.BatchExportWidget.title)
        self.outputVideoList.init_language()
        self.inputLine.init_language()
        self.exportButton.setText(LANG_UI_TXT.fileDialog.export)
        self.cancelButton.setText(LANG_UI_TXT.button.Cancel)
        for n, label in enumerate(self.findChildren(QLabel)):
            label.setText(LANG_UI_TXT.BatchExportWidget.label[n])
        self.outputBatLine.setPlaceholderText('')

    def init_font(self, font: QFont):
        for i in self.findChildren(QLabel):
            i.setFont(font)
        for i in self.findChildren(QLineEdit):
            i.setFont(font)
        for i in self.findChildren(QListWidget):
            i.setFont(font)
        for i in self.findChildren(QPushButton):
            i.setFont(font)

    def change_row(self):
        sender = self.sender()
        row = sender.currentRow()
        if sender == self.inputLine:
            self.outputVideoList.setCurrentRow(row)
        else:
            self.inputLine.setCurrentRow(row)

    def export_code(self):
        enable = True
        input_len = self.inputLine.count()
        if not self.outputBatLine.text():
            self.outputBatLine.setPlaceholderText(
                LANG_UI_TXT.info.no_empty)
            enable = False
        else:
            self.outputBatLine.setPlaceholderText('')
        if input_len == 0:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                LANG_UI_TXT.info.input_file_can_not_be_empty,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
            enable = False
        else:
            if (output_len := self.outputVideoList.count()) != input_len:
                r = QMessageBox.question(
                    self,
                    LANG_UI_TXT.info.error,
                    LANG_UI_TXT.info.not_equal,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes)
                if r == QMessageBox.StandardButton.Yes:
                    few, more = (
                        self.outputVideoList, self.inputLine) if output_len < input_len else (
                        self.inputLine, self.outputVideoList)
                    for n in range(more.count()):
                        if n + 1 > few.count():
                            file_name = QFileInfo(more.item(n).text())
                            base_name = file_name.completeBaseName()
                            new = QFileInfo(file_name.absoluteDir(), base_name).absoluteFilePath()
                            few.addItem(f'{new}.265')
                else:
                    enable = False
        if enable:
            x265 = X265.absoluteFilePath() if X265.absoluteFilePath() else 'x265'
            vspipe = VSPIPE.absoluteFilePath() if VSPIPE.absoluteFilePath() else 'vspipe'
            avs4x26x = AVS4X26X.absoluteFilePath() if AVS4X26X.absoluteFilePath() else 'avs4x26x'
            try:
                with open(self.outputBatLine.text(), 'w') as f:
                    for i in range(input_len):
                        input_path = self.inputLine.item(i).text()
                        output_path = self.outputVideoList.item(i).text()
                        task_type = QFileInfo(input_path).suffix().lower()
                        if task_type == 'vpy':
                            f.write(f'"{vspipe}" -c y4m "{input_path}" -| '
                                    f'"{x265}" {COMMANDS} -o "{output_path}" --y4m --input -\n')
                        elif task_type == 'avs':
                            f.write(
                                f'"{avs4x26x}" {COMMANDS} -o "{output_path}" "{input_path}"\n')
                        elif task_type == 'yuv':
                            f.write(
                                f'"{x265}" --input "{input_path}" {COMMANDS} -o "{output_path}"\n')
            except PermissionError:
                QMessageBox.warning(
                    self,
                    LANG_UI_TXT.info.error,
                    LANG_UI_TXT.info.permission,
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.information(
                    self,
                    LANG_UI_TXT.info.success,
                    LANG_UI_TXT.info.export_success,
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)


class FunctionListWidget(QListWidget):
    pass


class CheckThread(QThread):
    finishSignal = Signal(tuple)

    def __init__(self,
                 obj_name: str,
                 cmd: str,
                 correct_result: bytes,
                 correct_signal: int,
                 default_paths: list[QFileInfo]):
        super().__init__()
        self.cmd = cmd
        self.defaultPaths = default_paths
        self.task_paths = []
        self.correctResult = correct_result
        self.correctSignal = correct_signal
        self.results: list[bytes] = []
        self.process = QProcess()
        self.setObjectName(obj_name)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.add_msg)
        self.process.finished.connect(self.finish)

    def begin(self, paths: list[QFileInfo] = None):
        self.task_paths.clear()
        if paths:
            self.task_paths.extend(paths)
        else:
            self.task_paths.extend(self.defaultPaths)
        self.start()

    def next(self):
        if self.task_paths:
            return self.start()
        else:
            return False

    def run(self):
        file = self.task_paths[0]
        if file.exists():
            if file.isReadable():
                self.results.clear()
                self.process.startCommand(f'"{file.absoluteFilePath()}"{self.cmd}')
                self.process.waitForFinished(-1)
            else:
                self.finishSignal.emit((self.objectName(), False, 0, self.task_paths.pop(0)))
        else:
            self.finishSignal.emit((self.objectName(), None, 0, self.task_paths.pop(0)))

    def add_msg(self):
        data = self.process.readAllStandardOutput().data()
        self.results.append(data)

    def finish(self, signal: int):
        self.finishSignal.emit((self.objectName(), b''.join(self.results), signal, self.task_paths.pop(0)))


class FuncLineEdit(QLineEdit):
    pass
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        char = r'!@\#\$%\^\&\(\)\-=\+/\.,\?><";:\\\|\[\]\{\}'
        self.setValidator(QRegularExpressionValidator(QRegularExpression(f'[^0-9{char}][^{char}]+')))
    '''
