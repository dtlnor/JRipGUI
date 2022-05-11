import sys
from PySide6.QtCore import QRegularExpression, QTimer, QPoint, QRegularExpressionMatch
from PySide6.QtGui import QBrush, QTextCursor
from PySide6.QtWidgets import QTabWidget, QWidgetAction, QGridLayout, QTableWidget, QTreeWidget, QHeaderView, \
    QMenu, QTreeWidgetItem, QProgressBar, QTableWidgetItem

import pymediainfo
from MyWidgets import *
from data import *


class EncodeWidget(QWidget):
    class VPYProcess(QProcess):
        frames = 0

    class RenameThread(QThread):
        pass

    class MoveThread(QThread):
        finishSignal = Signal(str)
        output_path = ''
        src_path = ''

        def set_parameter(self, src_path: str, output_path: str):
            self.src_path = src_path
            self.output_path = output_path

        def run(self):
            src_file = QFileInfo(self.src_path)
            if not src_file.exists():
                self.finishSignal.emit(f'移动失败：缓存视频文件不存在\n({src_file.absoluteFilePath()})')
            else:
                output_file = QFileInfo(self.output_path)
                output_filename = output_file.fileName()
                output_dir = output_file.dir()
                msg = ''
                for time in range(5):
                    if not output_dir.exists() and not output_dir.mkpath(output_dir.absolutePath()):
                        msg = f'移动失败：输出文件夹不存在且无法创建\n{output_dir.absolutePath()}'
                    else:
                        if QFileInfo(output_dir, output_filename).exists() and not output_dir.remove(output_filename):
                            msg = f'移动失败：输出文件已存在且无法覆盖\n{self.output_path}'
                        else:
                            if not WORK_DIR.rename(self.src_path, self.output_path):
                                msg = f'移动失败：移动至输出文件夹失败，请确认是否有权限复制至该文件夹：\n{output_dir.absolutePath()}'
                            else:
                                break
                    self.sleep(1)

                self.finishSignal.emit(msg)

    class DeleteThread(QThread):
        finishSignal = Signal(int)
        file_path = ''

        def run(self):
            if not QFileInfo(self.file_path).exists():
                self.finishSignal.emit(1)
            else:
                for i in range(10):
                    if QDir().remove(self.file_path):
                        self.finishSignal.emit(1)
                        break
                    else:
                        self.msleep(500)
                else:
                    self.finishSignal.emit(0)

    class FinishThread(QThread):
        finishSignal = Signal()

        def __init__(self, *process: QProcess):
            super().__init__()
            self.processes = process

        def run(self):
            for process in self.processes:
                if process.state() != QProcess.ProcessState.NotRunning:
                    if not process.waitForFinished(10000):
                        process.kill()
            self.finishSignal.emit()

    def __init__(self, parent, /, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        from main import MainWidget
        self.mainWidget: MainWidget = parent
        # self.taskProgress = parent.taskProgress
        self.home = QVBoxLayout(self)

        self.tabWidget = QTabWidget(self)
        self.taskOperationWidget = TaskOperationWidget(self)
        self.taskAppendWidget = TaskAppendWidget(self)

        self.init_ui()

    def init_ui(self):
        shadow(self)
        palette = QPalette()
        palette.setColor(self.backgroundRole(), QColor(255, 255, 255))
        self.setPalette(palette)

        self.home.setContentsMargins(10, 10, 10, 10)

        self.home.addWidget(self.tabWidget)
        self.tabWidget.addTab(self.taskAppendWidget, '')
        self.tabWidget.addTab(self.taskOperationWidget, '')

    def init_language(self):
        self.tabWidget.setTabText(0, LANG_UI_TXT.EncodeWidget.tab[0])
        self.tabWidget.setTabText(1, LANG_UI_TXT.EncodeWidget.tab[1])
        self.taskAppendWidget.init_language()
        self.taskOperationWidget.init_language()

    def init_font(self, font: QFont):
        self.tabWidget.setFont(font)
        self.tabWidget.tabBar().setFont(font)
        self.taskAppendWidget.init_font(font)
        self.taskOperationWidget.init_font(font)

    def create_task(self):
        TASK_DIR.refresh()
        tasks = [file.completeBaseName()[3:] for file in TASK_DIR.entryInfoList()]
        tasks.sort()
        last = int(tasks[-1]) if tasks else 0
        task_table_widget = self.taskOperationWidget.taskTableWidget
        for i in range(self.taskAppendWidget.inputListWidget.count()):
            last += 1
            task_name = f'job{last:03}.task'

            input_name = self.taskAppendWidget.inputListWidget.item(i).text()
            output_name = self.taskAppendWidget.outputVideoList.item(i).text()
            task_type = QFileInfo(input_name).suffix().lower()
            task = Task(input_name, output_name, task_type, Task.States.WAITING, '', '', str(COMMANDS),
                        file_name=task_name, parent=self.taskOperationWidget.tasks)
            row = task_table_widget.rowCount()
            task_table_widget.setRowCount(row + 1)
            for col, text in enumerate(task.to_tuple()):
                if col == 3:
                    text = LANG_UI_TXT.EncodeWidget.state[text]
                item = QTableWidgetItem(text)
                if col in range(2, 6):
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                else:
                    item.setToolTip('\n'.join([text[i * 60:(i + 1) * 60] for i in range(len(text) // 60 + 1)]))

                task_table_widget.setItem(row, col, item)
                task_table_widget.resizeRowToContents(row)
            task.save()
        if self.taskOperationWidget.tasks.cur_task:
            self.taskOperationWidget.numLine.setText(
                f'{self.taskOperationWidget.tasks.cur_index + 1}/{task_table_widget.rowCount()}')
        self.taskAppendWidget.clear_temp_task()

    def create_task2(self, command: str):
        TASK_DIR.refresh()
        tasks = [file.completeBaseName()[3:] for file in TASK_DIR.entryInfoList()]
        tasks.sort()
        last = int(tasks[-1]) if tasks else 0
        last += 1
        task_name = f'job{last:03}.task'
        task_table_widget = self.taskOperationWidget.taskTableWidget
        row = task_table_widget.rowCount()
        task_table_widget.setRowCount(row + 1)
        task = Task('', '', 'bat', 0, '', '', command, file_name=task_name, parent=self.taskOperationWidget.tasks)
        for column, text in enumerate(task.to_tuple()):
            if column == 3:
                text = LANG_UI_TXT.EncodeWidget.state[text]
            item = QTableWidgetItem(text)
            if column in range(2, 6):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            task_table_widget.setItem(row, column, item)
            task_table_widget.resizeRowToContents(row)
        task_table_widget.item(row, 6).setToolTip(
            '\n'.join([command[i * 60:(i + 1) * 60] for i in range(len(command) // 60 + 1)]))
        if self.taskOperationWidget.tasks.cur_task:
            self.taskOperationWidget.numLine.setText(
                f'{self.taskOperationWidget.tasks.cur_index + 1}/{task_table_widget.rowCount()}')

        task.save()


class TaskAppendWidget(QWidget):
    def __init__(self, parent, /, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        parent: EncodeWidget
        self.encodeWidget = parent

        self.home = QGridLayout(self)
        self.inputListLabel = QLabel(self)
        self.inputCodeLabel = QLabel(self)
        self.outputTypeLabel = QLabel(self)
        self.outputListLabel = QLabel(self)

        self.partCode = QVBoxLayout()
        self.codeEditor = CodeEditor()
        self.partCodeButton = QHBoxLayout()
        self.partTaskButton = QHBoxLayout()
        self.commandLabel = QLabel(self)
        self.commandPlainTextEdit = CodeEditor()
        self.inputListWidget = FileListWidget(QFileDialog.getOpenFileNames,
                                              ExtGroup('vpy', 'avs', 'yuv'))
        self.outputTypeComboBox = QComboBox(self)
        self.outputVideoList = FileListWidget(QFileDialog.getSaveFileName,
                                              ExtGroup(SETTINGS.rawHevcExt))

        self.appendTaskButton = QPushButton(self)
        self.clearTaskButton = QPushButton(self)
        self.saveCodeButton = QPushButton(self)
        self.cancelCodeButton = QPushButton(self)
        self.partBatButton = QHBoxLayout()
        self.loadBatButton = PathPushButton(QFileDialog.getOpenFileName, ExtGroup('bat'), True, self)
        self.appendTaskButton2 = QPushButton(self)
        self.oneClickTaskButton = QPushButton(self)

        self.taskEditor = TaskEditionWidget(
            self.encodeWidget.taskOperationWidget,
            mode='append',
            input_ext=ExtGroup('vpy',
                               'avs',
                               'yuv',
                               'avi',
                               Ext('mp4', 'm4v'),
                               'mov',
                               Ext('3gp', '3g2'),
                               Ext('m2ts', 'ts'),
                               'm2v',
                               Ext('mpeg', 'mpg'),
                               Ext('ogm', 'ogv'),
                               'vob',
                               Ext('mkv', 'webm'),
                               'flv',
                               Ext('rmvb', 'rm'),
                               Ext('wmv', 'wm')),
            output_ext=ExtGroup(SETTINGS.rawHevcExt, 'mkv', 'mp4'))

        self.labels = (self.inputListLabel,
                       self.inputCodeLabel,
                       self.outputTypeLabel,
                       self.outputListLabel,
                       self.commandLabel)

        self.buttons = (self.appendTaskButton,
                        self.clearTaskButton,
                        self.saveCodeButton,
                        self.cancelCodeButton,
                        self.loadBatButton,
                        self.appendTaskButton2,
                        self.oneClickTaskButton)
        self.init_ui()

    def init_ui(self):
        self.partTaskButton.addWidget(self.appendTaskButton, 0, Qt.AlignmentFlag.AlignLeft)
        self.partTaskButton.addWidget(self.clearTaskButton, 0, Qt.AlignmentFlag.AlignLeft)
        self.partTaskButton.addStretch(1)

        self.partCodeButton.addWidget(self.saveCodeButton, 0, Qt.AlignmentFlag.AlignLeft)
        self.partCodeButton.addWidget(self.cancelCodeButton, 0, Qt.AlignmentFlag.AlignLeft)
        self.partCodeButton.addStretch(1)

        self.outputTypeComboBox.addItems(('raw-hevc', 'mkv', 'mp4'))
        self.outputTypeComboBox.currentTextChanged.connect(self.change_output_type)

        self.commandPlainTextEdit.setFixedHeight(100)
        self.commandPlainTextEdit.textChanged.connect(self.change_command)
        self.appendTaskButton2.setDisabled(True)

        self.home.addWidget(self.inputListLabel, 0, 0, 1, 1)
        self.home.addWidget(self.inputListWidget, 1, 0, 1, 1)
        self.home.addWidget(self.outputTypeLabel, 2, 0, 1, 1)
        self.home.addWidget(self.outputTypeComboBox, 3, 0, 1, 1)
        self.home.addWidget(self.outputListLabel, 4, 0, 1, 1)
        self.home.addWidget(self.outputVideoList, 5, 0, 1, 1)
        self.home.addLayout(self.partTaskButton, 6, 0, 1, 1)
        self.home.addLayout(self.partCode, 0, 1, 7, 1)
        self.home.addWidget(self.commandLabel, 7, 0, 1, 2)
        self.home.addWidget(self.commandPlainTextEdit, 8, 0, 1, 2)
        self.home.addLayout(self.partBatButton, 9, 0, 1, 2)
        self.partBatButton.addWidget(self.appendTaskButton2)
        self.partBatButton.addWidget(self.loadBatButton)
        self.partBatButton.addStretch(1)
        self.partBatButton.addWidget(self.oneClickTaskButton)

        self.inputListWidget.currentItemChanged.connect(self.change_row)
        self.outputVideoList.currentItemChanged.connect(self.change_row)

        self.partCode.addWidget(self.inputCodeLabel)
        self.partCode.addWidget(self.codeEditor)
        self.partCode.addLayout(self.partCodeButton)

        self.appendTaskButton.clicked.connect(self.append_task)
        self.appendTaskButton2.clicked.connect(self.append_task2)
        self.oneClickTaskButton.clicked.connect(self.one_click_task)
        self.oneClickTaskButton.setMinimumWidth(100)
        self.clearTaskButton.clicked.connect(self.clear_temp_task)
        self.clearTaskButton.setIcon(set_icon(svgs.trash))
        self.codeEditor.textChanged.connect(self.edit)
        self.codeEditor.setDisabled(True)

        self.saveCodeButton.clicked.connect(self.save)
        self.saveCodeButton.setDisabled(True)
        self.saveCodeButton.setIcon(set_icon(svgs.save))
        self.cancelCodeButton.clicked.connect(self.cancel)
        self.cancelCodeButton.setDisabled(True)

        self.loadBatButton.select_signal.connect(self.load_bat)

    def init_language(self):
        self.outputVideoList.init_language()
        self.inputListWidget.init_language()
        self.appendTaskButton.setText(LANG_UI_TXT.button.append_task)
        self.appendTaskButton2.setText(LANG_UI_TXT.button.append_task)
        self.oneClickTaskButton.setText(LANG_UI_TXT.button.one_click)
        self.clearTaskButton.setText(LANG_UI_TXT.button.clear)
        self.saveCodeButton.setText(LANG_UI_TXT.fileDialog.save)
        self.cancelCodeButton.setText(LANG_UI_TXT.button.Cancel)
        self.loadBatButton.setText(LANG_UI_TXT.button.Load)
        self.taskEditor.setWindowTitle(LANG_UI_TXT.button.one_click)
        self.taskEditor.init_language()
        for n, label in enumerate(self.labels):
            label.setText(LANG_UI_TXT.EncodeWidget.TaskAppendWidget[n])

    def init_font(self, font: QFont):
        self.inputListWidget.setFont(font)
        self.outputVideoList.setFont(font)
        self.codeEditor.init_font(font)
        self.commandPlainTextEdit.init_font(font)
        self.outputTypeComboBox.setFont(font)
        self.taskEditor.init_font(font)
        for button in self.buttons:
            button.setFont(font)
        for n, label in enumerate(self.labels):
            label.setFont(font)

    def change_output_type(self, text: str):
        if text == 'raw-hevc':
            self.outputVideoList.extGroup.set_ext((SETTINGS.rawHevcExt,))
        elif text == 'mkv':
            self.outputVideoList.extGroup.set_ext(('mkv',))
        elif text == 'mp4':
            self.outputVideoList.extGroup.set_ext(('mp4',))
        else:
            self.outputVideoList.extGroup.set_ext((SETTINGS.rawHevcExt,))

    def change_row(self, current_item: FileListWidget, last_item: FileListWidget):
        sender = self.sender()
        current_row = sender.row(current_item)
        if sender == self.inputListWidget:
            if self.saveCodeButton.isEnabled() and last_item:
                last_row = sender.row(last_item)
                answer = QMessageBox.question(
                    self,
                    LANG_UI_TXT.info.not_saved,
                    LANG_UI_TXT.info.save_ask,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes)
                if answer == QMessageBox.StandardButton.Yes:
                    self.save(self.inputListWidget.item(last_row).text())
            self.codeEditor.set_code_type(CodeEditor.CodeType.Other)

            self.codeEditor.setDisabled(True)
            if current_row == -1:
                self.codeEditor.clear()
            else:
                if self.inputListWidget.count() > current_row:
                    file_name = self.inputListWidget.item(current_row).text()
                    task_type = QFileInfo(file_name).suffix().lower()
                    if task_type in ('vpy', 'avs'):
                        if task_type == 'vpy':
                            encoding = 'utf-8'
                            self.codeEditor.set_code_type(CodeEditor.CodeType.Vpy)
                        else:
                            self.codeEditor.set_code_type(CodeEditor.CodeType.Avs)
                            encoding = None
                        try:
                            with open(file_name, 'r', encoding=encoding, errors='replace') as f:
                                self.codeEditor.setPlainText(f.read())
                                self.codeEditor.setEnabled(True)
                        except FileNotFoundError:
                            self.codeEditor.setPlainText(
                                f'{LANG_UI_TXT.info.not_found} {file_name}')

                            self.codeEditor.set_code_type(CodeEditor.CodeType.Other)
                        except Exception as e:
                            self.codeEditor.setPlainText(str(e))
                            self.codeEditor.set_code_type(CodeEditor.CodeType.Other)
                    else:
                        self.codeEditor.clear()
                else:
                    self.codeEditor.clear()
            if self.outputVideoList.count() >= current_row > -1:
                self.outputVideoList.setCurrentRow(current_row)

            self.saveCodeButton.setDisabled(True)
            self.cancelCodeButton.setDisabled(True)
        else:
            if self.inputListWidget.count() >= current_row > -1:
                self.inputListWidget.setCurrentRow(current_row)

    def edit(self):
        self.saveCodeButton.setEnabled(True)
        self.cancelCodeButton.setEnabled(True)

    def save(self, file_name: str = ''):
        if not file_name:
            file_name = self.inputListWidget.currentItem().text()
        task_type = QFileInfo(file_name).suffix().lower()
        if task_type == 'vpy':
            encoding = 'utf-8'
        elif task_type == 'avs':
            encoding = None
        else:
            encoding = 'utf-8'
        try:
            with open(file_name, 'w', encoding=encoding) as f:
                f.write(self.codeEditor.toPlainText())
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
                LANG_UI_TXT.info.save_success,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
            self.saveCodeButton.setDisabled(True)
            self.cancelCodeButton.setDisabled(True)

    def cancel(self):
        file_name = self.inputListWidget.currentItem().text()
        task_type = QFileInfo(file_name).suffix().lower()
        if task_type == 'vpy':
            encoding = 'utf-8'
        elif task_type == 'avs':
            encoding = None
        else:
            encoding = 'utf-8'
        try:
            with open(file_name, 'r', encoding=encoding) as f:
                self.codeEditor.setPlainText(f.read())
        except Exception as e:
            QMessageBox.warning(self,
                                LANG_UI_TXT.info.error,
                                str(e),
                                QMessageBox.StandardButton.Ok)
        else:
            self.saveCodeButton.setDisabled(True)
            self.cancelCodeButton.setDisabled(True)

    def check_equal(self):
        if (output_len := self.outputVideoList.count()) < (input_len := self.inputListWidget.count()):
            r = QMessageBox.question(
                self,
                LANG_UI_TXT.info.error,
                LANG_UI_TXT.info.not_equal,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes)
            if r == QMessageBox.StandardButton.Yes:
                few, more = (self.outputVideoList, self.inputListWidget) \
                    if output_len < input_len \
                    else (self.inputListWidget, self.outputVideoList)
                if (index := self.outputTypeComboBox.currentIndex()) == 0:
                    suffix = SETTINGS.rawHevcExt
                elif index == 1:
                    suffix = 'mkv'
                elif index == 2:
                    suffix = 'mp4'
                else:
                    suffix = SETTINGS.rawHevcExt
                for n in range(more.count()):
                    if n + 1 > few.count():
                        file_name = QFileInfo(more.item(n).text())
                        base_name = file_name.completeBaseName()
                        new = QFileInfo(file_name.absoluteDir(), base_name).absoluteFilePath()
                        few.addItem(f'{new}.{suffix}')
            return False
        elif output_len > input_len:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                LANG_UI_TXT.info.not_equal,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
        else:
            return True

    def load_bat(self, files: tuple):
        if files:
            try:
                with open(files[0]) as f:
                    self.commandPlainTextEdit.setPlainText(f.read())
            except Exception as e:
                QMessageBox.critical(self,
                                     LANG_UI_TXT.info.error,
                                     str(e),
                                     QMessageBox.StandardButton.Ok)

    def change_command(self):
        if self.commandPlainTextEdit.toPlainText():
            self.appendTaskButton2.setEnabled(True)
        else:
            self.appendTaskButton2.setDisabled(True)

    def append_task(self):
        if self.inputListWidget.count() == 0:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                LANG_UI_TXT.info.input_file_can_not_be_empty,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
        elif self.check_equal():
            self.encodeWidget.create_task()

    def append_task2(self):
        if command := self.commandPlainTextEdit.toPlainText():
            for par in command.splitlines():
                if par and par != 'pause':
                    self.encodeWidget.create_task2(par)
        self.commandPlainTextEdit.clear()

    def one_click_task(self):
        self.taskEditor.importChapterButton.setDisabled(True)
        self.taskEditor.importAudioButton.setDisabled(True)
        self.taskEditor.importSubtitleButton.setDisabled(True)
        self.taskEditor.inputTreeWidget.setDisabled(True)
        self.taskEditor.inputTreeWidget.clear()
        self.taskEditor.inputLine.clear()
        self.taskEditor.outputLine.clear()
        self.taskEditor.commandPlainTextEdit.clear()
        self.taskEditor.commandPlainTextEdit.setMaximumBlockCount(99)
        commands = [line.strip() for line in str(COMMANDS).split('--')]
        for line in commands:
            if line:
                self.taskEditor.commandPlainTextEdit.appendPlainText(f'--{line.strip()}')
        self.taskEditor.show()

    def clear_temp_task(self):
        self.inputListWidget.clear()
        self.outputVideoList.clear()

    def keyReleaseEvent(self, a0) -> None:
        if a0.modifiers() == Qt.KeyboardModifier.ControlModifier and a0.key() == Qt.Key.Key_S:
            if self.saveCodeButton.isEnabled():
                self.saveCodeButton.click()


class TaskOperationWidget(QWidget):
    def __init__(self, parent, /, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        parent: EncodeWidget
        self.encodeWidget = parent
        self.mergeTimes = 5
        self.sysEncoder = sys.getdefaultencoding()
        self.curTaskError = False
        self.hasError = False
        self.times = 0
        self.no_message = 0
        self.encodeTimer = QTimer()
        self.preloadTimer = QTimer()
        self.result: list[tuple[QRegularExpression, QRegularExpressionMatch, str]] = []
        self.isRunning = False

        self.vpyMsgs = []
        self.vpyFrames = 0

        self.tasks = TaskList(self)

        self.home = QVBoxLayout(self)

        self.numLine = QLineEdit(self)
        self.inputLine = QLineEdit(self)
        self.outputLine = QLineEdit(self)
        self.fpsLine = QLineEdit(self)
        self.bitLine = QLineEdit(self)
        self.timeLine = QLineEdit(self)
        self.frameLine = QLineEdit(self)

        self.messageTreeWidget = MessageTreeWidget(self)

        self.numLabel = QLabel(self)
        self.inputLabel = QLabel(self)
        self.outputLabel = QLabel(self)
        self.fpsLabel = QLabel(self)
        self.bitLabel = QLabel(self)
        self.timeLabel = QLabel(self)
        self.frameLabel = QLabel(self)
        self.progressBar = QProgressBar(self)
        self.backCurrentTaskButton = QPushButton(self)
        self.checkTasks: list[CheckThread] = []
        self.x265CheckThread = CheckThread('x265', ' --version', b'x265 [info]', 0, X265_PATH)
        self.vspipeCheckThread = CheckThread('vspipe', ' -v', b'VapourSynth Video Processing Library', 0,
                                             VSPIPE_PATH)
        self.avs4x26xCheckThread = CheckThread('avs4x26x', ' -o',
                                               b'avs4x26x [error]: No supported input file found', -1,
                                               AVS4X26X_PATH)
        self.mkvmergeCheckThread = CheckThread('mkvmerge', ' -V', b'mkvmerge v', 0, MKVMERGE_PATH)
        self.mp4boxCheckThread = CheckThread('mp4box', ' -version', b'MP4Box - GPAC version', 0, MP4BOX_PATH)
        self.checkProcesses = {'x265': self.x265CheckThread,
                               'vspipe': self.vspipeCheckThread,
                               'avs4x26x': self.avs4x26xCheckThread,
                               'mkvmerge': self.mkvmergeCheckThread,
                               'mp4box': self.mp4boxCheckThread}
        self.vspipeProcess = QProcess()
        self.preloadProcess = QProcess()
        self.avsProcess = QProcess()
        self.avs4x26xProcess = QProcess()
        self.batProcess = QProcess()
        self.x265Process = QProcess()
        self.mkvProcess = QProcess()
        self.mp4Process = QProcess()
        self.vpyProcess = EncodeWidget.VPYProcess()
        self.moveThread = EncodeWidget.MoveThread()
        self.finishThread = EncodeWidget.FinishThread(self.vspipeProcess,
                                                      self.avsProcess,
                                                      self.batProcess,
                                                      self.x265Process,
                                                      self.mkvProcess,
                                                      self.mp4Process)
        self.shutDownProcess = QProcess()
        self.deleteTempThread = EncodeWidget.DeleteThread()

        self.filterLayout = QHBoxLayout()
        self.filterLabel = QLabel(self)
        self.filterComboBox = QComboBox(self)
        self.taskTableWidget = TaskTableWidget(self, self.tasks)

        self.partResult = QHBoxLayout()
        self.partProgress = QFormLayout()

        self.confirmBox = QHBoxLayout()
        self.cancelShutDownButton = QPushButton(self)
        self.retryComboBox = QComboBox(self)
        self.retryLabel = QLabel(self)
        self.shutDownComboBox = QComboBox(self)
        self.shutDownLabel = QLabel(self)
        self.runButton = QPushButton(self)
        self.abortButton = QPushButton(self)
        self.abortAllButton = QPushButton(self)

        self.frameReg = QRegularExpression(
            r'\[(\d+\.\d)+%\].*?(\d+/\d+).*?frames.*?([\d\.]+).*?fps.*?([\d\.]+).*?kb/s.*?eta.*?([\d:]+)')
        self.noFrameReg = QRegularExpression(
            r'(\d+).*?frames.*?([\d\.]+).*?fps.*?([\d\.]+).*?kb/s')
        self.finishReg = QRegularExpression(
            r'Output ([\d]+) frames in [\d\.]+ seconds \([\d\.]+ fps\)')
        self.encodeZeroReg = QRegularExpression(r'encoded 0 frames',
                                                QRegularExpression.PatternOption.CaseInsensitiveOption)

        self.lines = (
            self.numLine,
            self.inputLine,
            self.outputLine,
            self.fpsLine,
            self.bitLine,
            self.timeLine,
            self.frameLine)
        self.labels = (
            self.filterLabel,
            self.numLabel,
            self.inputLabel,
            self.outputLabel,
            self.fpsLabel,
            self.bitLabel,
            self.timeLabel,
            self.frameLabel,
            self.retryLabel,
            self.shutDownLabel)

        self.init_ui()

    def init_ui(self):
        for line in self.lines:
            line.setReadOnly(True)

        self.deleteTempThread.finishSignal.connect(self.delete_over)

        self.moveThread.finishSignal.connect(self.move_over)

        self.partResult.addWidget(self.messageTreeWidget)
        self.partResult.addLayout(self.partProgress)
        self.partResult.setStretch(0, 2)
        self.partResult.setStretch(1, 1)

        self.partProgress.addRow(self.numLabel, self.numLine)
        self.partProgress.addRow(self.inputLabel, self.inputLine)
        self.partProgress.addRow(self.outputLabel, self.outputLine)
        self.partProgress.addRow(self.fpsLabel, self.fpsLine)
        self.partProgress.addRow(self.bitLabel, self.bitLine)
        self.partProgress.addRow(self.timeLabel, self.timeLine)
        self.partProgress.addRow(self.frameLabel, self.frameLine)
        self.partProgress.addRow(self.progressBar)
        self.partProgress.addRow(self.backCurrentTaskButton)
        self.confirmBox.addStretch(1)
        self.confirmBox.addWidget(self.cancelShutDownButton)
        self.confirmBox.addWidget(self.retryLabel)
        self.confirmBox.addWidget(self.retryComboBox)
        self.confirmBox.addWidget(self.shutDownLabel)
        self.confirmBox.addWidget(self.shutDownComboBox)
        self.confirmBox.addWidget(self.runButton)
        self.confirmBox.addWidget(self.abortButton)
        self.confirmBox.addWidget(self.abortAllButton)

        self.runButton.clicked.connect(self.run_tasks)
        self.runButton.setIcon(set_icon(svgs.run))
        self.abortButton.clicked.connect(self.abort)
        self.abortButton.setIcon(set_icon(svgs.stop))
        self.abortAllButton.clicked.connect(self.abort_all)
        self.cancelShutDownButton.clicked.connect(self.cancel_plan)
        self.cancelShutDownButton.hide()
        pal = QPalette()
        pal.setColor(QPalette.ColorRole.ButtonText, QColor(255, 0, 0))
        self.cancelShutDownButton.setPalette(pal)
        self.retryComboBox.currentIndexChanged.connect(self.set_times)
        self.abortButton.setDisabled(True)
        self.abortAllButton.setDisabled(True)

        self.x265CheckThread.finishSignal.connect(self.check_process_over)
        self.vspipeCheckThread.finishSignal.connect(self.check_process_over)
        self.avs4x26xCheckThread.finishSignal.connect(self.check_process_over)
        self.mkvmergeCheckThread.finishSignal.connect(self.check_process_over)
        self.mp4boxCheckThread.finishSignal.connect(self.check_process_over)

        self.vpyProcess.finished.connect(self.vpy_over)
        self.vpyProcess.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.vpyProcess.readyReadStandardOutput.connect(self.read_vpy)
        self.vpyProcess.readyReadStandardError.connect(self.read_vpy)
        self.vpyProcess.closeWriteChannel()
        self.vpyProcess.errorOccurred.connect(self.vspipe_error)

        self.vspipeProcess.setStandardOutputProcess(self.x265Process)
        self.vspipeProcess.readyReadStandardOutput.connect(self.read_vspipe)
        self.vspipeProcess.readyReadStandardError.connect(self.read_vspipe_error)
        self.vspipeProcess.closeWriteChannel()
        self.vspipeProcess.errorOccurred.connect(self.vspipe_error)

        self.preloadProcess.closeWriteChannel()
        self.preloadProcess.finished.connect(self.preload_over)

        self.avs4x26xProcess.readyReadStandardError.connect(self.read_avs4x26x_error)
        self.avs4x26xProcess.readyReadStandardOutput.connect(self.read_avs4x26x)
        self.avs4x26xProcess.finished.connect(self.avs4x26x_over)

        self.avsProcess.readyReadStandardOutput.connect(self.read_avs)
        self.avsProcess.readyReadStandardError.connect(self.read_avs_error)
        self.avsProcess.finished.connect(self.encode_over)
        self.avsProcess.closeWriteChannel()

        self.batProcess.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.batProcess.readyReadStandardOutput.connect(self.read_bat)
        self.batProcess.finished.connect(self.bat_over)
        self.batProcess.closeWriteChannel()

        self.x265Process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.x265Process.readyReadStandardOutput.connect(self.read_x265)
        self.x265Process.finished.connect(self.encode_over)
        self.x265Process.errorOccurred.connect(self.encode_error)
        self.x265Process.closeWriteChannel()

        self.mkvProcess.closeWriteChannel()
        self.mkvProcess.finished.connect(self.merge)
        self.mkvProcess.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.mkvProcess.readyReadStandardOutput.connect(self.read_mkv)

        self.mp4Process.closeWriteChannel()
        self.mp4Process.finished.connect(self.merge)
        self.mp4Process.readyReadStandardOutput.connect(self.read_mp4)
        self.mp4Process.readyReadStandardError.connect(self.read_mp4_error)

        self.finishThread.finishSignal.connect(self.finish)

        self.progressBar.setRange(0, 100)
        self.progressBar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.backCurrentTaskButton.clicked.connect(self.back_to_current_task)
        self.backCurrentTaskButton.setDisabled(True)
        self.messageTreeWidget.setHeaderHidden(True)
        self.messageTreeWidget.setColumnCount(1)
        self.messageTreeWidget.header().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.messageTreeWidget.header().setStretchLastSection(False)
        self.encodeTimer.timeout.connect(self.flush)

        self.home.addLayout(self.filterLayout)
        self.home.addWidget(self.taskTableWidget)
        self.home.addLayout(self.partResult)
        self.home.addLayout(self.confirmBox)

        self.filterComboBox.addItem('')
        self.filterComboBox.currentIndexChanged.connect(self.taskTableWidget.filter_task)
        self.filterComboBox.setFixedWidth(100)
        self.filterLayout.addStretch(1)
        self.filterLayout.addWidget(self.filterLabel)
        self.filterLayout.addWidget(self.filterComboBox)

    def init_language(self):
        self.taskTableWidget.init_language()

        if self.shutDownComboBox.count():
            for i in range(5):
                self.shutDownComboBox.setItemText(
                    i, LANG_UI_TXT.EncodeWidget.shutdown[i])
        else:
            self.shutDownComboBox.addItems(
                LANG_UI_TXT.EncodeWidget.shutdown)

        self.cancelShutDownButton.setText(
            LANG_UI_TXT.EncodeWidget.cancel_plan)
        if self.retryComboBox.count():
            for i in range(5):
                self.retryComboBox.setItemText(
                    i, LANG_UI_TXT.EncodeWidget.retry[i])
        else:
            self.retryComboBox.addItems(
                LANG_UI_TXT.EncodeWidget.retry)

        self.runButton.setText(LANG_UI_TXT.button.Run)
        self.abortButton.setText(LANG_UI_TXT.button.Abort)
        self.abortAllButton.setText(LANG_UI_TXT.button.Abort_all)

        self.filterComboBox.clear()
        self.filterComboBox.addItem('')
        self.filterComboBox.addItems(LANG_UI_TXT.EncodeWidget.state)

        for n, label in enumerate(self.labels):
            label.setText(LANG_UI_TXT.EncodeWidget.TaskOperationWidget[n])
        self.backCurrentTaskButton.setText(LANG_UI_TXT.EncodeWidget.back_cur_task)

    def init_font(self, font: QFont):
        new_font = QFont(font.family())
        new_font.setPixelSize(font.pixelSize() - 4)
        self.taskTableWidget.init_font(new_font)
        self.messageTreeWidget.setFont(new_font)
        self.progressBar.setFont(font)
        self.shutDownComboBox.setFont(font)
        self.shutDownComboBox.setFont(font)
        self.retryComboBox.setFont(font)
        self.filterComboBox.setFont(font)
        self.abortButton.setFont(font)
        self.runButton.setFont(font)
        self.abortAllButton.setFont(font)
        self.cancelShutDownButton.setFont(font)
        for line in self.lines:
            line.setFont(font)
        for n, label in enumerate(self.labels):
            label.setFont(font)

        self.backCurrentTaskButton.setFont(font)

    def set_times(self, index: int):
        self.times = (0, 1, 5, 10, -1)[index]

    def change_task(self):
        def add_child(msg, parent):
            if type(msg) == str:
                item = QTreeWidgetItem(parent)
                item.setText(0, msg)
                item.setToolTip(0, msg)
            else:
                for m in msg:
                    sub_item = QTreeWidgetItem(parent)
                    add_child(m, sub_item)

        selection = self.taskTableWidget.selectedRanges()
        if selection and len(selection) == 1 and selection[0].rowCount() == 1:
            row = self.taskTableWidget.currentRow()
            self.messageTreeWidget.clear()
            if row != -1:
                for block in self.tasks[row].message:
                    top, body = block
                    top_item = QTreeWidgetItem(self.messageTreeWidget)
                    top_item.setText(0, top)
                    top_item.setToolTip(0, top)
                    if body:
                        for par in body:
                            add_child(par, top_item)
            self.messageTreeWidget.scrollToBottom()
        else:
            self.messageTreeWidget.clear()

    def clear_message(self):
        if selection := self.taskTableWidget.selectedRanges():
            for select in selection:
                for row in range(select.topRow(), select.bottomRow() + 1):
                    self.tasks[row].message.clear()
                    self.tasks[row].save()
                    self.messageTreeWidget.clear()

    def back_to_current_task(self):
        if (row := self.tasks.cur_index) > -1:
            self.taskTableWidget.selectRow(row)

    def run_tasks(self):
        self.runButton.setDisabled(True)
        self.next()

    def ready_next(self):
        self.task_kill_programs()
        QTimer.singleShot(1000, self.next)

    def next(self):
        self.progressBar.setValue(0)
        self.frameLine.clear()
        self.fpsLine.clear()
        self.bitLine.clear()
        self.timeLine.clear()
        self.inputLine.clear()
        self.inputLine.setToolTip('')
        self.outputLine.clear()
        self.outputLine.setToolTip('')
        self.curTaskError = False
        self.no_message = 0
        self.result.clear()

        if self.preloadProcess.state() == QProcess.ProcessState.NotRunning:
            self.isRunning = True
            if len(self.tasks) > self.tasks.cur_index + 1 > -1:
                self.tasks.cur_task = self.tasks[self.tasks.cur_index + 1]
                self.backCurrentTaskButton.setEnabled(True)
                if SETTINGS.cacheMethod == 1:
                    ENCODE_CACHE_DIR.setPath(QFileInfo(self.tasks.cur_task.output).absolutePath())
                self.numLine.setText(f'{self.tasks.cur_index + 1}/{len(self.tasks)}')
                if self.tasks.cur_task.status in (Task.States.WAITING, Task.States.RETRY):
                    self.check_task()
                else:
                    self.next()
            else:
                self.finishThread.start()
        else:
            self.isRunning = False

    def check_task(self):
        cur_index = self.tasks.cur_index
        task = self.tasks.cur_task
        output_path = task.output
        output_file = QFileInfo(output_path)
        self.taskTableWidget.selectRow(cur_index)

        output_type = output_file.suffix().lower()
        cur_time = get_time()
        if task.status == Task.States.RETRY:
            times = self.times if self.times >= 0 else '∞'
            self.messageTreeWidget.append_message(f'[{cur_time}]重试任务（还剩{times}）次')
        start_time = QDateTime.currentDateTime().toString('MM-dd hh:mm:ss')

        task.start = start_time
        task.end = ''
        if task.type == 'bat':
            self.messageTreeWidget.append_message(f'[{cur_time}]任务信息', [f'任务类型：{task.type}'])
            self.check_task_over()
        else:
            msg = list()
            msg.append(f'输入文件：{task.input}')
            msg.append(f'输出文件：{output_path}')
            msg.append(f'任务类型：{task.type}；输出文件扩展名：{output_type}')
            self.messageTreeWidget.append_message(f'[{cur_time}]任务信息', msg)

            check_vspipe = False
            check_avs4x26x = False
            if task.type in ('vpy', 'raw') and VSPIPE.absoluteFilePath():
                check_vspipe = True

            elif task.type == 'avs' and AVS4X26X.absoluteFilePath():
                check_avs4x26x = True
            check_x265 = True if not X265.absoluteFilePath() else False
            check_mkvmerge = True if output_type == 'mkv' and MKVMERGE.absoluteFilePath() else False
            check_mp4box = True if output_type == 'mp4' and MP4BOX.absoluteFilePath() else False
            self.check_encoding_programs(check_x265=check_x265,
                                         check_vspipe=check_vspipe,
                                         check_avs4x26x=check_avs4x26x,
                                         check_mkvmerge=check_mkvmerge,
                                         check_mp4box=check_mp4box)

    def check_encoding_programs(self,
                                *,
                                check_x265=True,
                                check_vspipe=True,
                                check_avs4x26x=True,
                                check_mkvmerge=True,
                                check_mp4box=True):
        self.checkTasks.clear()
        if check_x265:
            self.checkTasks.append(self.x265CheckThread)
        if check_vspipe:
            self.checkTasks.append(self.vspipeCheckThread)
        if check_avs4x26x:
            self.checkTasks.append(self.avs4x26xCheckThread)
        if check_mkvmerge:
            self.checkTasks.append(self.mkvmergeCheckThread)
        if check_mp4box:
            self.checkTasks.append(self.mp4boxCheckThread)

        if self.checkTasks:
            for thread in self.checkTasks:
                thread.begin()
        else:
            self.check_encoding_programs_over()

    def check_process_over(self, result: tuple):
        obj_name, result, signal, path = result
        programs = {'x265': (self.x265CheckThread,
                             self.encodeWidget.mainWidget.settingWidget.check_x265),
                    'vspipe': (self.vspipeCheckThread,
                               self.encodeWidget.mainWidget.settingWidget.check_vspipe),
                    'avs4x26x': (self.avs4x26xCheckThread,
                                 self.encodeWidget.mainWidget.settingWidget.check_avs4x26x),
                    'mkvmerge': (self.mkvmergeCheckThread,
                                 self.encodeWidget.mainWidget.settingWidget.check_mkvmerge),
                    'mp4box': (self.mp4boxCheckThread,
                               self.encodeWidget.mainWidget.settingWidget.check_mp4box)}
        process, func = programs[obj_name]
        if func(result, signal, path) or not process.next():
            if process in self.checkTasks:
                self.checkTasks.remove(process)
                if not self.checkTasks:
                    self.check_encoding_programs_over()
            else:
                print(f'{obj_name}不在检查列表内')

    def check_encoding_programs_over(self):
        task = self.tasks.cur_task
        msg = []
        if not X265.absoluteFilePath():
            msg.append(f'错误：x265程序不可用！')

        input_path = task.input
        input_file = QFileInfo(input_path)
        output_path = task.output
        output_file = QFileInfo(output_path)
        output_type = output_file.suffix().lower()

        check_vspipe = False
        check_avs4x26x = False
        if task.type in ('vpy', 'raw'):
            check_vspipe = True
        elif task.type == 'avs':
            check_avs4x26x = True
        check_mkvmerge = True if output_type == 'mkv' else False
        check_mp4box = True if output_type == 'mp4' else False
        if not input_file.exists():
            msg.append(f'错误：输入文件不存在！')
        elif not input_file.isReadable():
            msg.append(f'错误：无法读取输入文件')
        for track in task.tracks:
            if not QFileInfo(track.track_path).exists():
                msg.append(f'错误：{track.track_path}不存在！')
        if not output_file.dir().exists():
            msg.append(f'错误：输出文件夹不存在！')
        elif not QFileInfo(output_file.dir().absolutePath()).isWritable():
            msg.append(f'错误：无法写入输出文件夹')
        if check_avs4x26x and not AVS4X26X.absoluteFilePath():
            msg.append(f'错误：avs4x26x不可用！')
        elif check_vspipe and not VSPIPE.absoluteFilePath():
            msg.append(f'错误：vspipe不可用！')
        if check_mkvmerge and not MKVMERGE.absoluteFilePath():
            msg.append(f'错误：mkvmerge不可用！')
        elif check_mp4box and not MP4BOX.absoluteFilePath():
            msg.append(f'错误：mp4box不可用！')
        if msg:
            task.status = Task.States.ERROR
        else:
            msg.append(f'成功：未发现错误！')
        cur_time = get_time()
        self.messageTreeWidget.append_message(f'[{cur_time}]检查任务', msg, save=False)
        task.save()
        self.check_task_over()

    def check_task_over(self):
        task = self.tasks.cur_task
        cur_index = self.tasks.cur_index
        if task.status != Task.States.ERROR:
            task.status = Task.States.RUNNING
            task.save()
            input_path = task.input
            output_path = task.output
            self.inputLine.setText(input_path)
            self.inputLine.setToolTip(input_path)
            self.outputLine.setText(output_path)
            self.outputLine.setToolTip(output_path)
            cur_time = get_time()

            if task.type != 'bat':
                self.deleteTempThread.file_path = ENCODE_CACHE_DIR.absoluteFilePath(
                    QFileInfo(task.output).fileName())
                self.deleteTempThread.start()
            else:
                self.messageTreeWidget.append_message(f'[{cur_time}]任务开始')
                self.abortButton.setEnabled(True)
                self.abortAllButton.setEnabled(True)
                self.encodeTimer.start(2000)
                temp = ENCODE_CACHE_DIR.absoluteFilePath('$temp.bat')
                with open(temp, 'w') as f:
                    f.write(task.command)
                self.batProcess.start(temp)
        else:
            self.set_retry(cur_index)
            self.next()

    def delete_over(self, code: int):
        print(f'delete over: {code=}')
        if code == 1:
            task = self.tasks.cur_task
            output_path = task.output
            output_file = QFileInfo(output_path)
            input_path = task.input
            cur_time = get_time()

            raw_output = ENCODE_CACHE_DIR.absoluteFilePath(f'{output_file.completeBaseName()}.265')
            if task.type in ('vpy', 'raw'):
                if task.type == 'raw':
                    input_ext = QFileInfo(task.input).suffix().lower()
                    temp = ENCODE_CACHE_DIR.absoluteFilePath('$temp.vpy')
                    if input_ext in ('mp4', 'm4v', 'mov', '3gp', '3g2', 'm2ts', 'mpeg', 'vob',
                                     'm2v', 'mpg', 'ogm', 'ogv', 'ts', 'tp', 'ps'):
                        if LSMASH or self.encodeWidget.mainWidget.settingWidget.check_lsmas():
                            func = 'lsmas.LWLibavSource'
                        elif FFMS2 or self.encodeWidget.mainWidget.settingWidget.check_ffms2():
                            func = 'ffms2.Source'
                        else:
                            self.messageTreeWidget.append_brief_message(f'ffms2, lsmash {LANG_UI_TXT.info.not_found}\n',
                                                                        new_line=True,
                                                                        save=False)
                            task.status = Task.States.ERROR
                            task.save()
                            self.next()
                            return
                        with open(temp, 'w', encoding='utf-8') as f:
                            f.write('import vapoursynth as vs\n'
                                    'core = vs.core\n'
                                    f'clip = core.{func}(r"{input_path}")\n'
                                    'clip.set_output()\n')
                    elif input_ext == 'avi':
                        if AVISOURCE or self.encodeWidget.mainWidget.settingWidget.check_avisource():
                            func = 'avisource.AVISource'
                        elif FFMS2 or self.encodeWidget.mainWidget.settingWidget.check_ffms2():
                            func = 'ffms2.Source'
                        elif LSMASH or self.encodeWidget.mainWidget.settingWidget.check_lsmas():
                            func = 'lsmas.LWLibavSource'
                        else:
                            self.messageTreeWidget.append_brief_message(
                                f'ffms2, lsmash, avisource {LANG_UI_TXT.info.not_found}\n',
                                new_line=True,
                                save=False)
                            task.status = Task.States.ERROR
                            task.save()
                            self.next()
                            return
                        with open(temp, 'w', encoding='utf-8') as f:
                            f.write('import vapoursynth as vs\n'
                                    'core = vs.core\n'
                                    f'clip = core.{func}(r"{input_path}")\n'
                                    'clip.set_output()\n')
                    else:
                        if FFMS2 or self.encodeWidget.mainWidget.settingWidget.check_ffms2():
                            func = 'ffms2.Source'
                        elif LSMASH or self.encodeWidget.mainWidget.settingWidget.check_lsmas():
                            func = 'lsmas.LWLibavSource'
                        else:
                            self.messageTreeWidget.append_brief_message(f'ffms2, lsmash {LANG_UI_TXT.info.not_found}\n',
                                                                        new_line=True,
                                                                        save=False)
                            task.status = Task.States.ERROR
                            task.save()
                            self.next()
                            return
                        with open(temp, 'w', encoding='utf-8') as f:
                            f.write('import vapoursynth as vs\n'
                                    'core = vs.core\n'
                                    f'clip = core.{func}(r"{input_path}")\n'
                                    'clip.set_output()\n')
                    vpy_path = temp
                else:
                    vpy_path = input_path
                self.abortButton.setDisabled(True)
                self.abortAllButton.setDisabled(True)
                self.messageTreeWidget.append_message(f'[{cur_time}]vspipe初始化')
                # self.vpyProcess.task = task
                command = task.command
                if (match := QRegularExpression(r'--frames (\d+)').match(command)).hasMatch():
                    frames = int(match.captured(1))
                else:
                    frames = 0
                self.vpyProcess.frames = frames
                command = f'"{VSPIPE.absoluteFilePath()}" --info "{vpy_path}" -'
                self.vpyProcess.startCommand(command)
                print(f'start vpy: {command}')

            elif task.type == 'avs':
                command = f'"{AVS4X26X.absoluteFilePath()}" -L "{X265.absoluteFilePath()}" {task.command} ' \
                          f'"{input_path}"'
                self.messageTreeWidget.append_message(f'[{cur_time}]avisynth初始化')
                self.abortButton.setDisabled(True)
                self.abortAllButton.setDisabled(True)
                self.avs4x26xProcess.startCommand(command)

            elif task.type == 'yuv':
                command = f'"{X265.absoluteFilePath()}" {task.command} --input "{input_path}" -o "{raw_output}"'
                self.messageTreeWidget.append_message(f'[{cur_time}]任务开始')
                self.abortButton.setEnabled(True)
                self.abortAllButton.setEnabled(True)
                self.encodeTimer.start(2000)
                self.x265Process.startCommand(command)
                self.ready_preload()
            else:
                self.set_retry(self.tasks.cur_index)
                self.messageTreeWidget.append_message('任务类型无法识别')
                self.next()

        else:
            self.messageTreeWidget.append_brief_message(f'无法删除{self.deleteTempThread.file_path}\n',
                                                        new_line=True)

    def read_vpy(self):
        data = self.vpyProcess.readAllStandardOutput().data().decode(encoding='utf-8')
        self.messageTreeWidget.new_line()
        for text in data.splitlines(True):
            if text.strip():
                if ': ' in text and text.count(': ') == 1:
                    key, value = text.split(': ')
                    self.messageTreeWidget.append_brief_message(f'{key}: {value}')
                    if key == 'Frames':
                        clip_frames = int(value.strip())
                        if (match := QRegularExpression(r'--seek (\d+)').match(
                                self.tasks.cur_task.command)).hasMatch():
                            seek = int(match.captured(1))
                            if seek >= clip_frames:
                                self.curTaskError = True
                                self.messageTreeWidget.append_brief_message(
                                    f'错误：输入源总共{clip_frames}帧，但是命令"--seek"跳过{seek}帧\n')
                        else:
                            seek = 0
                        if (match := QRegularExpression(r'--frames (\d+)').match(
                                self.tasks.cur_task.command)).hasMatch():
                            frames = int(match.captured(1))
                            if frames > clip_frames:
                                self.curTaskError = True
                                self.messageTreeWidget.append_brief_message(
                                    f'错误：输入源总共{clip_frames}帧，但是命令"--frames"编码{frames}帧\n')
                        else:
                            frames = 0
                        if seek and frames and frames + seek > clip_frames:
                            self.curTaskError = True
                            self.messageTreeWidget.append_brief_message(
                                f'错误：输入源总共{clip_frames}帧，但是命令"--frames"和"--seek"共编码{frames + seek}帧\n')

                        self.vpyProcess.frames = clip_frames - seek
                elif (match := QRegularExpression(r'Creating lwi index file (\d+)%').match(text)).hasMatch():
                    self.progressBar.setValue(int(match.captured(1)))
                else:
                    self.messageTreeWidget.append_brief_message(text)

    def vpy_over(self, code: int):
        self.read_vpy()
        print(f'vpy_over: {code=}')
        if not self.curTaskError and code == 0:
            task = self.tasks.cur_task
            task.totalFrames = self.vpyProcess.frames
            raw_output = ENCODE_CACHE_DIR.absoluteFilePath(f'{QFileInfo(task.output).completeBaseName()}.265')

            self.messageTreeWidget.append_message(f'[{get_time()}]任务开始')
            self.abortButton.setEnabled(True)
            self.abortAllButton.setEnabled(True)
            self.encodeTimer.start(2000)
            self.progressBar.setValue(0)

            frames_cmd = f'--frames {self.vpyProcess.frames} '
            input_path = ENCODE_CACHE_DIR.absoluteFilePath('$temp.vpy') if task.type == 'raw' else task.input
            self.vspipeProcess.startCommand(f'"{VSPIPE.absoluteFilePath()}" -c y4m "{input_path}" -')
            self.x265Process.startCommand(
                f'"{X265.absoluteFilePath()}" {frames_cmd}{task.command} -o "{raw_output}" --y4m --input -')
            self.ready_preload()
            print('start')
        else:
            self.set_retry(self.tasks.cur_index)
            self.ready_next()

    def ready_preload(self):
        if SETTINGS.preload:
            QTimer.singleShot(30000, Partial(self.preload, index=self.tasks.cur_index))

    def preload(self, index: int):
        if self.isRunning and self.tasks.cur_index == index:
            print(f'preload start: index {index}; cur_task {self.tasks.cur_index}')
            for n in range(self.tasks.cur_index + 1, len(self.tasks)):
                next_task = self.tasks[n]
                next_task: Task
                if next_task.status in (Task.States.WAITING, Task.States.RETRY):
                    if next_task.type == 'vpy':
                        self.preloadProcess.startCommand(
                            f'"{VSPIPE.absoluteFilePath()}" --info "{next_task.input}" -')
                        QTimer.singleShot(SETTINGS.preloadTimeout * 1000,
                                          Partial(self.preload_timeout, task_num=index))
                        break
                    elif next_task.type == 'avs':
                        self.preloadProcess.startCommand(f'"{AVS4X26X.absoluteFilePath()}" "{next_task.input}"')
                        QTimer.singleShot(SETTINGS.preloadTimeout * 1000,
                                          Partial(self.preload_timeout, task_num=index))
                        break
                    elif next_task.type == 'raw':
                        pass
            else:
                print(f'no task need preload')

    def preload_timeout(self, task_num: int):
        if self.preloadProcess.state() != QProcess.ProcessState.NotRunning and self.tasks.cur_index == task_num:
            self.preloadProcess.kill()

    def preload_over(self, code: int):
        print(f'preload_over: {code=}')
        if not self.isRunning:
            self.ready_next()

    def read_avs4x26x(self):
        data = self.avs4x26xProcess.readAllStandardOutput().data().decode(SYSTEM_CODEC)
        for text in data.splitlines(True):
            if text.strip():
                if 'avs [info]: Video ' in text and text.count(': ') == 2:
                    head, key, value = text.split(': ')
                    self.messageTreeWidget.append_brief_message(f'{key}: {value}')
                else:
                    print('avs4x26x:  ', text)

    def read_avs4x26x_error(self):
        data = self.avs4x26xProcess.readAllStandardError().data().decode(SYSTEM_CODEC)
        if 'Maybe x26x closed' not in data and 'input or output file not specified' not in data:
            self.messageTreeWidget.new_line()
            self.messageTreeWidget.append_brief_message(data)

    def avs4x26x_over(self, code: int, exit_status):
        self.read_avs4x26x()
        self.read_avs4x26x_error()
        print(code, exit_status)
        if code in (1, -1073741819):
            task = self.tasks.cur_task
            raw_output = ENCODE_CACHE_DIR.absoluteFilePath(f'{QFileInfo(task.output).completeBaseName()}.265')

            command = f'"{AVS4X26X.absoluteFilePath()}" -L "{X265.absoluteFilePath()}" {task.command}' \
                      f' -o "{raw_output}" "{task.input}"'
            self.messageTreeWidget.append_message(f'[{get_time()}]任务开始')
            self.abortButton.setEnabled(True)
            self.abortAllButton.setEnabled(True)
            self.encodeTimer.start(2000)
            self.progressBar.setValue(0)
            self.avsProcess.startCommand(command)
            self.ready_preload()
            print('start')
        else:
            self.set_retry(self.tasks.cur_index)
            self.ready_next()

    def read_avs(self):
        data = self.avsProcess.readAllStandardOutput().data().decode(encoding=SYSTEM_CODEC)
        self.messageTreeWidget.append_brief_message(data)

    def read_avs_error(self):
        data = self.avsProcess.readAllStandardError().data().decode(encoding='utf-8')
        self.parse_data(data)

    def read_x265(self):
        data = self.x265Process.readAllStandardOutput().data().decode(encoding='utf-8')
        self.parse_data(data)

    def parse_data(self, data: str):
        if 'Syntax: x265 [options] infile [-o] outfile' in data:
            for text in data.splitlines(True)[245:]:
                if text.strip():
                    self.messageTreeWidget.append_brief_message(text, save=False)
            self.tasks.cur_task.save()
        else:
            for text in data.splitlines(True):
                if text.strip():
                    self.no_message = 0

                    if (match := self.frameReg.match(text)).hasMatch():
                        self.result.append((self.frameReg, match, text))
                    elif (match := self.noFrameReg.match(text)).hasMatch():
                        self.result.append((self.noFrameReg, match, text))
                    elif self.encodeZeroReg.match(text).hasMatch():
                        cur_time = get_time()
                        self.messageTreeWidget.append_brief_message(f'[{cur_time}]错误：输出视频为0帧。\n',
                                                                    new_line=True)
                        self.curTaskError = True

                    else:
                        self.messageTreeWidget.append_brief_message(text)

    def read_vspipe(self):
        data = self.vspipeProcess.readAllStandardOutput().data().decode(encoding='utf-8')
        print(f'vspipe: {data}')
        self.messageTreeWidget.append_brief_message(data)

    def read_vspipe_error(self):
        data = self.vspipeProcess.readAllStandardError().data().decode(encoding='utf-8')
        print('vspipe error: ', data)
        self.messageTreeWidget.append_brief_message(f'[{get_time()}]vspipe: \n', save=False)
        for text in data.splitlines(True):
            if text.strip():
                self.no_message = 0
                if (match := self.finishReg.match(text)).hasMatch():
                    total_frames = self.tasks.cur_task.totalFrames
                    out_frames = int(text[match.capturedStart(1): match.capturedEnd(1)])
                    if total_frames and out_frames < total_frames:
                        self.messageTreeWidget.append_brief_message(
                            f'错误：输入视频为{total_frames}帧，输出视频为{out_frames}帧。\n',
                            save=False)
                        self.curTaskError = True
                    else:
                        self.messageTreeWidget.append_brief_message(text, save=False)
                else:
                    self.messageTreeWidget.append_brief_message(text, save=False)
        self.tasks.cur_task.save()

    def vspipe_error(self):
        if self.abortButton.isEnabled():
            self.messageTreeWidget.append_brief_message('vspipe程序崩溃，任务中止\n',
                                                        new_line=True)
            self.curTaskError = True

    def read_bat(self):
        data = self.batProcess.readAllStandardOutput().data().decode(encoding=SYSTEM_CODEC)
        for text in data.splitlines(True):
            if text.strip():
                self.no_message = 0

                if (match := self.frameReg.match(text)).hasMatch():
                    self.result.append((self.frameReg, match, text))
                elif (match := self.noFrameReg.match(text)).hasMatch():
                    self.result.append((self.noFrameReg, match, text))
                elif self.encodeZeroReg.match(text).hasMatch():
                    cur_time = get_time()
                    self.messageTreeWidget.append_brief_message(f'[{cur_time}]错误：输出视频为0帧。\n',
                                                                new_line=True)
                    self.curTaskError = True
                elif self.finishReg.match(text).hasMatch():
                    cur_time = get_time()
                    self.messageTreeWidget.append_brief_message(f'[{cur_time}]{text}')
                else:
                    self.messageTreeWidget.append_brief_message(text)

    def read_mkv(self):
        data = self.mkvProcess.readAllStandardOutput().data().decode(encoding='utf-8')
        self.messageTreeWidget.append_brief_message(data)

    def read_mp4(self):
        data = self.mp4Process.readAllStandardOutput().data().decode(encoding='utf-8')
        print(data)
        self.messageTreeWidget.append_brief_message(data)

    def read_mp4_error(self):
        data = self.mp4Process.readAllStandardError().data()
        try:
            data = data.decode(encoding='utf-8', errors='replace')
        except UnicodeDecodeError:
            data = data.decode('ansi', errors='replace')
        print(data)

        self.messageTreeWidget.append_brief_message(data)

    def flush(self):
        if self.result:
            reg, match, text = self.result[-1]
            values = []
            for i in range(1, len(match.capturedTexts())):
                start = match.capturedStart(i)
                end = match.capturedEnd(i)
                values.append(text[start:end])
            if len(values) == 5:
                progress = int(float(values[0]))
                self.progressBar.setValue(progress)
                # self.parent.taskProgress.setValue(progress)
                self.frameLine.setText(values[1])
                self.fpsLine.setText(f'{values[2]}x')
                self.bitLine.setText(f'{values[3]}kbps')
                self.timeLine.setText(values[4])
            else:
                self.frameLine.setText(f'{values[0]}')
                self.fpsLine.setText(f'{values[1]}x')
                self.bitLine.setText(f'{values[2]}kbps')
            self.result.clear()
        else:
            self.no_message += 2
            if SETTINGS.encodeTimeout and self.no_message > SETTINGS.encodeTimeout:
                cur_time = get_time()
                self.messageTreeWidget.append_brief_message(f'[{cur_time}]任务长时间未返回消息，放弃该任务\n',
                                                            new_line=True)
                self.set_retry(self.tasks.cur_index)
                self.pre_abort()
                self.task_kill_programs()

    def encode_error(self):
        print(f'[{get_time()}]x265返回一项错误\n')

    def encode_over(self, code: int = 0):
        self.read_x265()
        self.flush()
        print(f'encode over: {code=}')
        self.encodeTimer.stop()
        self.progressBar.setValue(100)
        # self.parent.taskProgress.setValue(100)
        task = self.tasks.cur_task
        self.abortButton.setDisabled(True)
        self.abortAllButton.setDisabled(True)
        self.no_message = 0
        output_path = task.output
        output_file = QFileInfo(output_path)
        # _dir = output_file.absoluteDir()
        if not self.curTaskError and (code in (0, 62097)):
            if code == 0:
                cur_time = get_time()
                self.messageTreeWidget.append_brief_message(f'[{cur_time}]编码完成\n', new_line=True)
                if output_file.suffix().lower() in ('mkv', 'mp4'):
                    self.merge(-1)
                else:
                    if task.status == Task.States.RUNNING:
                        if SETTINGS.cacheMethod == 0:
                            cur_time = get_time()
                            base_name = output_file.completeBaseName()
                            raw_output = ENCODE_CACHE_DIR.absoluteFilePath(f'{base_name}.265')

                            self.messageTreeWidget.append_brief_message(
                                f'[{cur_time}]移动至{output_file.absolutePath()}\n', new_line=True, save=False)
                            task.save()
                            self.moveThread.set_parameter(raw_output, output_path)
                            self.moveThread.start()
                        else:
                            self.move_over('')
                    else:
                        self.ready_next()

            elif code == 62097:
                self.ready_next()
        else:
            self.messageTreeWidget.append_brief_message('编码失败\n', new_line=True)
            self.set_retry(self.tasks.cur_index)
            self.ready_next()

    def merge(self, code: int = 0):
        sender = self.sender()
        if sender == self.mkvProcess:
            self.read_mkv()
        elif sender == self.mp4Process:
            self.read_mp4_error()
        task = self.tasks.cur_task
        output_path = task.output
        output_file = QFileInfo(output_path)
        output_type = output_file.suffix().lower()

        base_name = output_file.completeBaseName()
        raw_output = ENCODE_CACHE_DIR.absoluteFilePath(f'{base_name}.265')
        if (output_type == 'mkv' and code in (0, 1)) or (output_type == 'mp4' and code == 0):
            cur_time = get_time()
            self.mergeTimes = 5
            self.messageTreeWidget.append_brief_message(f'[{cur_time}]混流成功\n', new_line=True, save=False)
            WORK_DIR.remove(raw_output)

            task.status = Task.States.FINISH
            self.messageTreeWidget.append_message(f'[{cur_time}]任务完成', save=False)
            task.end = QDateTime.currentDateTime().toString('MM-dd hh:mm:ss')
            task.save()
            self.ready_next()

        else:
            cur_time = get_time()
            if self.mergeTimes > 0:
                if self.mergeTimes < 5:
                    self.messageTreeWidget.append_brief_message(f'[{cur_time}]混流失败：重试中，还剩{self.mergeTimes}次\n',
                                                                new_line=True)
                else:
                    self.messageTreeWidget.append_message(f'[{cur_time}]{LANG_UI_TXT.EncodeWidget.merging}')

                self.mergeTimes -= 1

                if output_type == 'mkv':
                    raw_output = ENCODE_CACHE_DIR.absoluteFilePath(f'{output_file.completeBaseName()}.265')
                    if task.tracks:
                        commands = []
                        chapter_cmd = ''
                        track_list = ['0:0']
                        audio_default = True
                        subtitle_default = True
                        num = 1
                        for n, track in enumerate(task.tracks):
                            track: Track

                            track_id = f'{int(track.track_id) - 1}' if track.track_id else '0'
                            if track.track_type == 'Audio':
                                if audio_default:
                                    default = f'--default-track {track_id}:yes '
                                    audio_default = False
                                else:
                                    default = ' '
                                commands.append(
                                    f'--audio-tracks {track_id} --no-video --no-subtitles --no-chapters {default}"'
                                    f'{track.track_path}"')

                                track_list.append(f'{num}:{track_id}')
                                num += 1
                            elif track.track_type == 'Text':
                                if subtitle_default:
                                    default = f'--default-track {track_id}:yes '
                                    subtitle_default = False
                                else:
                                    default = ' '

                                commands.append(
                                    f'--no-video --no-audio --no-chapters {default}"{track.track_path}"')
                                track_list.append(f'{num}:{track_id}')
                                num += 1

                            elif track.track_type == 'Menu':
                                chapter_cmd = f'--chapters "{track.track_path}" '
                        command = f'"{MKVMERGE.absoluteFilePath()}" --ui-language {SETTINGS.language} ' \
                                  f'-o "{output_path}" --default-track 0:yes "{raw_output}" {" ".join(commands)} ' \
                                  f'{chapter_cmd}--track-order {",".join(track_list)}'
                        self.messageTreeWidget.append_brief_message(command, new_line=True)
                        self.mkvProcess.startCommand(command)
                    else:
                        command = f'"{MKVMERGE.absoluteFilePath()}" --ui-language {SETTINGS.language} ' \
                                  f'-o "{output_path}" "{raw_output}"'
                        self.messageTreeWidget.append_brief_message(command, new_line=True)
                        self.mkvProcess.startCommand(command)
                    self.messageTreeWidget.new_line()
                elif output_type == 'mp4':
                    raw_output = ENCODE_CACHE_DIR.absoluteFilePath(f'{output_file.completeBaseName()}.265')
                    if task.tracks:
                        commands = []
                        sub_commands = []
                        for n, track in enumerate(task.tracks):
                            track: Track

                            if track.track_type == 'Audio':
                                commands.append(f'-add "{track.track_path}"#trackID={track.track_id}')
                            elif track.track_type == 'Text':
                                track_id = f'#trackID={track.track_id}' if track.track_id else ''
                                sub_commands.append(f'-add "{track.track_path}"{track_id}')
                            elif track.track_type == 'Menu':
                                sub_commands.append(f'-chap "{track.track_path}"')
                        self.mp4Process.startCommand(f'"{MP4BOX.absoluteFilePath()}" -new -add "{raw_output}" '
                                                     f'{" ".join(commands)} {" ".join(sub_commands)} {output_path}"')
                    else:

                        self.mp4Process.startCommand(
                            f'"{MP4BOX.absoluteFilePath()}" -new -add "{raw_output}" "{output_path}"')

                else:
                    task.status = Task.States.ERROR
                    self.ready_next()

            else:
                self.mergeTimes = 5
                new_name = f"{base_name}_{cur_time.replace(':', '_')}.{SETTINGS.rawHevcExt}"
                if ENCODE_CACHE_DIR.rename(raw_output, new_name):
                    task.status = Task.States.WARNING
                    self.messageTreeWidget.append_message(f'[{cur_time}]任务未完成', save=False)
                    self.messageTreeWidget.append_brief_message(f'[{cur_time}]混流失败：请手动移动raw-hevc文件：\n'
                                                                f'{ENCODE_CACHE_DIR.absoluteFilePath(new_name)}\n',
                                                                new_line=True,
                                                                save=False)
                else:
                    task.status = Task.States.ERROR
                    self.messageTreeWidget.append_message(f'[{cur_time}]任务失败', save=False)
                    self.messageTreeWidget.append_brief_message(f'[{cur_time}]混流失败：请尽快手动移动raw-hevc文件：\n'
                                                                f'{raw_output}\n',
                                                                new_line=True,
                                                                save=False)

                task.end = QDateTime.currentDateTime().toString('MM-dd hh:mm:ss')
                task.save()
                self.ready_next()

    def move_over(self, msg: str):
        task = self.tasks.cur_task
        cur_time = get_time()
        task.end = QDateTime.currentDateTime().toString('MM-dd hh:mm:ss')
        if msg:
            task.status = Task.States.ERROR
            self.messageTreeWidget.append_brief_message(f'[{cur_time}]{msg}\n'
                                                        f'[{cur_time}]输出文件位于视频缓存文件夹中，请手动移动该文件。\n',
                                                        new_line=True,
                                                        save=False)
            self.messageTreeWidget.append_message(f'[{cur_time}]任务失败', save=False)
        else:
            task.status = Task.States.FINISH
            self.messageTreeWidget.append_message(f'[{cur_time}]任务完成', save=False)
        task.save()
        self.ready_next()

    def bat_over(self, code: int):
        self.read_bat()
        self.flush()
        self.encodeTimer.stop()
        self.progressBar.setValue(100)
        ENCODE_CACHE_DIR.remove('$temp.bat')
        cur_time = get_time()
        task = self.tasks.cur_task
        task.status = Task.States.FINISH
        task.end = QDateTime.currentDateTime().toString('MM-dd hh:mm:ss')
        task.save()

        self.messageTreeWidget.append_message(f'[{cur_time}]任务结束', [f'返回代码：{code}'])
        self.curTaskError = False
        self.abortButton.setDisabled(True)
        self.abortAllButton.setDisabled(True)
        self.ready_next()

    def task_kill_programs(self):
        def kill(process: QProcess):
            if process.state() != QProcess.ProcessState.NotRunning:
                process.kill()
        if self.tasks.cur_task:
            if (task_type := self.tasks.cur_task.type) == 'avs':
                kill(self.avsProcess)
            elif task_type == 'bat':
                kill(self.batProcess)
            else:
                if task_type in ('vpy', 'raw'):
                    kill(self.vspipeProcess)
                kill(self.x265Process)

    def pre_abort(self):
        self.abortButton.setDisabled(True)
        self.abortAllButton.setDisabled(True)
        self.result.clear()
        self.encodeTimer.stop()
        self.no_message = 0
        self.progressBar.setValue(0)
        # self.parent.taskProgress.reset()

    def abort(self):
        self.pre_abort()
        self.task_kill_programs()

        cur_time = get_time()

        self.tasks.cur_task.status = Task.States.ABORT
        self.tasks.cur_task.__end = QDateTime.currentDateTime().toString('MM-dd hh:mm:ss')
        self.messageTreeWidget.append_message(f'[{cur_time}]{LANG_UI_TXT.EncodeWidget.abort}', save=False)
        self.tasks.cur_task.save()

    def abort_all(self, is_done: bool = False):
        self.pre_abort()

        if not is_done:
            self.task_kill_programs()
        if self.tasks.cur_index != -1:
            cur_time = get_time()
            for row in range(self.tasks.cur_index):
                if self.tasks[row].status == Task.States.RETRY:
                    task = self.tasks[row]
                    task.status = Task.States.ABORT
                    self.messageTreeWidget.append_message(f'[{cur_time}]{LANG_UI_TXT.EncodeWidget.abort}',
                                                          task=task, save=False)
            for row in range(self.tasks.cur_index, self.taskTableWidget.rowCount()):
                task = self.tasks[row]
                if (state := task.status) in (Task.States.WAITING, Task.States.RETRY, Task.States.RUNNING):

                    task.status = Task.States.ABORT
                    self.messageTreeWidget.append_message(f'[{cur_time}]{LANG_UI_TXT.EncodeWidget.abort}',
                                                          task=task, save=False)
                    if state in (Task.States.RUNNING, Task.States.RETRY):
                        task.end = QDateTime.currentDateTime().toString('MM-dd hh:mm:ss')
        self.tasks.save()
        self.hasError = False
        self.times = 0

    def finish(self):
        print('finish')
        self.encodeTimer.stop()
        self.no_message = 0
        self.result.clear()
        for i in self.lines:
            i.clear()
            i.setToolTip('')
        self.progressBar.setValue(100)
        # self.parent.taskProgress.reset()
        self.tasks.cur_task = None
        self.isRunning = False
        self.backCurrentTaskButton.setDisabled(True)
        self.numLine.clear()
        if self.times and self.hasError:
            self.hasError = False
            self.times -= 1
            self.ready_next()
        else:
            self.tasks.save()

            self.taskTableWidget.task_finished()
            self.runButton.setEnabled(True)
            self.abortButton.setDisabled(True)
            self.abortAllButton.setDisabled(True)

            self.set_times(self.retryComboBox.currentIndex())
            self.hasError = False

            index = self.shutDownComboBox.currentIndex()

            if index == 1:
                self.shutDownProcess.startCommand('shutdown -s -t 60 -f')
                self.cancelShutDownButton.show()
            elif index == 2:
                self.close()
            elif index == 3:
                self.shutDownProcess.startCommand('shutdown -r -t 60 -f')
                self.cancelShutDownButton.show()
            elif index == 4:
                self.shutDownProcess.startCommand('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')

    def set_retry(self, row: int):
        task = self.tasks[row]
        if self.times:
            info = Task.States.RETRY
        else:
            info = Task.States.ERROR
            cur_time = get_time()
            task.end = QDateTime.currentDateTime().toString('MM-dd hh:mm:ss')
            self.messageTreeWidget.append_message(f'[{cur_time}]任务失败！', save=False)
        self.hasError = True

        task.status = info
        task.save()

    def cancel_plan(self):
        self.shutDownProcess.startCommand('shutdown /a')
        self.cancelShutDownButton.hide()


class MessageTreeWidget(QTreeWidget):
    def __init__(self, parent: TaskOperationWidget):
        super().__init__(parent=parent)
        self.parent = parent
        self.tasks = self.parent.tasks
        self.nextNew: bool = True
        self.cur_pos: int = 0

    def new_line(self):
        self.nextNew = True
        self.cur_pos = 0

    def append_brief_message(self, msg: str, *, new_line: bool = False, save=True, ignores: list[str] = None):
        if new_line:
            self.nextNew = True
            self.cur_pos = 0
        selection = self.parent.taskTableWidget.selectedRanges()
        if len(selection) == 1 \
                and selection[0].rowCount() == 1 \
                and selection[0].topRow() == self.tasks.cur_index:
            show_msg = True
        else:
            show_msg = False

        msg = msg.replace('\r\n', '\n')
        if self.tasks.cur_task.message:
            for line in msg.splitlines(True):
                if not ignores or all([t not in line for t in ignores]):
                    if (suffix := line[-1]) in ('\n', '\r'):
                        line = line[:-1]
                    if line:
                        key, value = self.tasks.cur_task.message[-1]
                        if self.nextNew:
                            old_msg = []
                        else:
                            if self.cur_pos > len(value):
                                old_msg = [' ' for _ in range(self.cur_pos)]
                            else:
                                old_msg = list(value)
                        old_msg[self.cur_pos:self.cur_pos + len(line)] = line
                        new_msg = ''.join(old_msg)
                        if show_msg:
                            top_item = self.topLevelItem(self.topLevelItemCount() - 1)
                            if self.nextNew or not top_item.childCount():
                                item = QTreeWidgetItem(top_item)
                            else:
                                item = top_item.child(top_item.childCount() - 1)

                            item.setText(0, new_msg)
                            item.setToolTip(0, new_msg)
                            self.scrollToBottom()
                        if self.nextNew or not value:
                            value.append(new_msg)
                        else:
                            value[-1] = new_msg
                    if suffix == '\r':
                        self.nextNew = False
                        self.cur_pos = 0
                    elif suffix == '\n':
                        self.nextNew = True
                        self.cur_pos = 0
                    else:
                        self.nextNew = False
                        self.cur_pos = self.cur_pos + len(line)
        else:
            top_item_text = get_time()
            if show_msg:
                top_item = QTreeWidgetItem(self)
                top_item.setText(0, top_item_text)
                top_item.setToolTip(0, top_item_text)
            self.tasks.cur_task.message.add_top(top_item_text)
            self.append_brief_message(msg)
        if save:
            self.tasks.cur_task.save()

    def append_message(self, top_msg: str, sub_msgs: list[str] = None, *, task: Task = None, save: bool = True):
        if sub_msgs is None:
            sub_msgs = list()
        index = self.tasks.index(task) if task else self.tasks.cur_index
        selection = self.parent.taskTableWidget.selectedRanges()
        if len(selection) == 1 and selection[0].rowCount() == 1:
            if selection[0].topRow() == index:
                top_item = QTreeWidgetItem(self)
                top_item.setText(0, top_msg)
                top_item.setToolTip(0, top_msg)
                for par in sub_msgs:
                    item = QTreeWidgetItem(top_item)
                    item.setText(0, par)
                    item.setToolTip(0, par)
                top_item.setExpanded(True)
                self.scrollToBottom()
        task = task if task else self.tasks.cur_task
        task.message.add_top(top_msg, sub_msgs)
        self.nextNew = True
        if save:
            task.save()


class TaskEditionWidget(QWidget):
    def __init__(self, parent: TaskOperationWidget,
                 mode: str = 'edit',
                 input_ext: ExtGroup = None,
                 output_ext: ExtGroup = None,
                 *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.mode = mode
        self.row = -1
        self.task = None
        self.allTypes = []

        self.home = QHBoxLayout(self)
        self.editLayout = QFormLayout()
        self.codeLayout = QVBoxLayout()

        self.inputLabel = QLabel(self)
        self.inputLine = PathLineEdit(QFileDialog.getOpenFileName, input_ext, self)
        self.mergeLabel = QLabel(self)
        self.importAudioButton = PathPushButton(QFileDialog.getOpenFileNames, parent=self)
        self.importSubtitleButton = PathPushButton(QFileDialog.getOpenFileNames, parent=self)
        self.importChapterButton = PathPushButton(QFileDialog.getOpenFileNames, parent=self)
        self.inputTreeWidget = InputTreeWidget(self)
        self.outputLabel = QLabel(self)
        self.outputLine = PathLineEdit(QFileDialog.getSaveFileName, output_ext, self)
        self.commandLabel = QLabel(self)
        self.commandPlainTextEdit = CodeEditor()
        self.tipLabel = QLabel(self)
        self.confirmButton = QPushButton(self)
        self.applyButton = QPushButton(self)
        self.appendButton = QPushButton(self)

        self.previewThread = QThread()

        self.codeEditor = CodeEditor()
        self.saveButton = QPushButton(self)
        self.resetButton = QPushButton(self)
        self.init_ui()

    def init_ui(self):
        if self.mode == 'edit':
            self.appendButton.hide()
        elif self.mode == 'append':
            self.confirmButton.hide()
            self.applyButton.hide()
        else:
            raise
        self.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.WindowStaysOnTopHint)
        self.resize(800, 600)
        self.confirmButton.clicked.connect(self.confirm)
        self.applyButton.clicked.connect(self.confirm)
        self.appendButton.clicked.connect(self.append)

        self.importAudioButton.select_signal.connect(self.import_file)
        self.importSubtitleButton.select_signal.connect(self.import_file)
        self.importChapterButton.select_signal.connect(self.import_file)

        self.inputTreeWidget.setColumnCount(4)
        self.inputTreeWidget.itemClicked.connect(self.change)

        for i in (self.inputLine, self.outputLine, self.commandPlainTextEdit):
            i.textChanged.connect(self.change)

        self.inputTreeWidget.setColumnWidth(0, 36)

        self.codeEditor.setDisabled(True)
        self.codeEditor.textChanged.connect(self.edit_code)
        self.saveButton.setDisabled(True)
        self.saveButton.clicked.connect(self.save)
        self.resetButton.setDisabled(True)
        self.resetButton.clicked.connect(self.reset)

        part_import = QHBoxLayout()
        part_import.addWidget(self.importAudioButton)
        part_import.addWidget(self.importSubtitleButton)
        part_import.addWidget(self.importChapterButton)
        part_import.addStretch(1)

        part_button = QHBoxLayout()
        part_button.addStretch(1)
        part_button.addWidget(self.applyButton)
        part_button.addWidget(self.confirmButton)
        part_button.addWidget(self.appendButton)

        self.editLayout.addRow(self.inputLabel, self.inputLine)
        self.editLayout.addRow(self.commandLabel, self.commandPlainTextEdit)
        self.editLayout.addRow('', self.tipLabel)
        self.editLayout.addRow(self.mergeLabel, part_import)
        self.editLayout.addRow('', self.inputTreeWidget)
        self.editLayout.addRow(self.outputLabel, self.outputLine)
        self.editLayout.addRow('', part_button)

        part_code_button = QHBoxLayout()
        part_code_button.addStretch(1)
        part_code_button.addWidget(self.saveButton)
        part_code_button.addWidget(self.resetButton)

        self.codeLayout.addWidget(self.codeEditor)
        self.codeLayout.addLayout(part_code_button)

        self.home.addLayout(self.editLayout)
        self.home.addLayout(self.codeLayout)

    def init_language(self):
        for i, text in zip((self.inputLabel, self.outputLabel, self.commandLabel),
                           LANG_UI_TXT.TaskEdit.label):
            i.setText(text)

        self.setWindowTitle(LANG_UI_TXT.TaskEdit.title)
        self.confirmButton.setText(LANG_UI_TXT.button.Confirm)
        self.applyButton.setText(LANG_UI_TXT.button.Apply)
        self.appendButton.setText(LANG_UI_TXT.button.one_click)
        self.tipLabel.setText('注意：请使用"--"命令(如"--preset")，而不是"-"命令（如"-p"）')
        self.mergeLabel.setText(LANG_UI_TXT.button.Merge)
        self.importAudioButton.setText(LANG_UI_TXT.button.Import_Audio)
        self.importSubtitleButton.setText(LANG_UI_TXT.button.Import_Subtitle)
        self.importChapterButton.setText(LANG_UI_TXT.button.Import_Chapter)
        self.inputTreeWidget.setHeaderLabels(LANG_UI_TXT.TaskEdit.header)

        self.saveButton.setText(LANG_UI_TXT.button.save)
        self.resetButton.setText(LANG_UI_TXT.button.reset)

    def init_font(self, font: QFont):
        self.setFont(font)
        self.inputLabel.setFont(font)
        self.inputLine.setFont(font)
        self.inputTreeWidget.setFont(font)
        self.mergeLabel.setFont(font)
        self.importAudioButton.setFont(font)
        self.importSubtitleButton.setFont(font)
        self.importChapterButton.setFont(font)
        self.outputLabel.setFont(font)
        self.outputLine.setFont(font)
        self.commandLabel.setFont(font)
        self.commandPlainTextEdit.init_font(font)
        self.confirmButton.setFont(font)
        self.applyButton.setFont(font)
        self.appendButton.setFont(font)
        self.tipLabel.setFont(font)
        self.saveButton.setFont(font)
        self.resetButton.setFont(font)
        self.codeEditor.init_font(font)

    def change(self):
        sender = self.sender()
        self.applyButton.setEnabled(True)
        self.confirmButton.setEnabled(True)
        if sender == self.inputLine:
            if self.saveButton.isEnabled():
                answer = QMessageBox.question(
                    self,
                    LANG_UI_TXT.info.not_saved,
                    LANG_UI_TXT.info.save_ask,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes)
                if answer == QMessageBox.StandardButton.Yes:
                    self.save()
            input_path = self.inputLine.text()
            input_type = QFileInfo(input_path).suffix().lower()

            self.codeEditor.setDisabled(True)
            self.codeEditor.clear()

            if input_type in ('vpy', 'avs'):
                if input_type == 'vpy':
                    self.codeEditor.set_code_type(CodeEditor.CodeType.Vpy)
                    encoding = 'utf-8'
                else:
                    self.codeEditor.set_code_type(CodeEditor.CodeType.Avs)
                    encoding = None
                try:
                    with open(input_path, 'r', encoding=encoding, errors='replace') as f:
                        self.codeEditor.setPlainText(f.read())
                        self.codeEditor.setEnabled(True)
                except FileNotFoundError:
                    self.codeEditor.setPlainText(
                        f'{LANG_UI_TXT.info.not_found} {input_path}')

                    self.codeEditor.set_code_type(CodeEditor.CodeType.Other)
                except Exception as e:
                    self.codeEditor.setPlainText(str(e))
            else:
                self.codeEditor.set_code_type(CodeEditor.CodeType.Other)
                self.codeEditor.setDisabled(True)

            self.saveButton.setDisabled(True)
            self.resetButton.setDisabled(True)
        elif sender == self.outputLine:
            output_type = QFileInfo(self.outputLine.text()).suffix().lower()

            if not self.outputLine.isEnabled() or output_type not in ('mp4', 'mkv') or not self.outputLine.text():
                self.inputTreeWidget.setDisabled(True)
                self.importSubtitleButton.setDisabled(True)
                self.importChapterButton.setDisabled(True)
                self.importAudioButton.setDisabled(True)
            else:
                if output_type == 'mp4':
                    self.importSubtitleButton.extGroup.set_ext(('srt', 'idx', 'ttxt'))
                    self.importChapterButton.extGroup.set_ext(('txt',))
                    self.importAudioButton.extGroup.set_ext(
                        ('mp2', 'mp3', 'mp4', 'aac', 'ac3', 'm4a',
                         Ext('mkv', 'mka'),
                         Ext('flac'),
                         Ext('m2ts', 'ts'),
                         Ext('rmvb', 'rm'), 'avi', '3gp'))
                elif output_type == 'mkv':
                    self.importSubtitleButton.extGroup.set_ext(('srt', 'idx', 'ssa', 'ass', 'sup'))
                    self.importChapterButton.extGroup.set_ext(('txt', 'xml'))
                    self.importAudioButton.extGroup.set_ext(
                        ('aac', 'dts', 'mp2', 'mp3', 'mp4', 'm4a', 'ogg', 'ac3',
                         'wav', 'pcm', 'opus',
                         Ext('mkv', 'mka'),
                         Ext('flac'),
                         Ext('m2ts', 'ts'), Ext('rmvb', 'rm'), 'avi', '3gp'))
                for index in range(self.inputTreeWidget.topLevelItemCount()):
                    item = self.inputTreeWidget.topLevelItem(index)
                    input_type = self.allTypes[index]
                    input_path = item.text(3)
                    suffix = QFileInfo(input_path).suffix()
                    if (input_type == 'Menu' and suffix not in self.importChapterButton.extGroup.all_ext) \
                            or (input_type == 'Audio' and suffix not in self.importAudioButton.extGroup.all_ext) \
                            or (input_type == 'Text' and suffix not in self.importSubtitleButton.extGroup.all_ext):
                        item.setDisabled(True)
                    else:
                        item.setDisabled(False)
                self.inputTreeWidget.setEnabled(True)
                self.importSubtitleButton.setEnabled(True)
                self.importChapterButton.setEnabled(True)
                self.importAudioButton.setEnabled(True)

    def import_file(self, files: tuple):
        sender = self.sender()

        if sender == self.importAudioButton:
            import_type = 'Audio'
        elif sender == self.importSubtitleButton:
            import_type = 'Text'
        elif sender == self.importChapterButton:
            import_type = 'Menu'
        else:
            import_type = ''

        no_track = True
        for file in files:
            no_track = self.parse_input(file, import_type)

        if not no_track:
            self.change()
            self.inputTreeWidget.resizeColumnToContents(0)
            self.inputTreeWidget.resizeColumnToContents(1)
            self.inputTreeWidget.resizeColumnToContents(2)
            self.inputTreeWidget.resizeColumnToContents(3)
            self.inputTreeWidget.resizeColumnToContents(4)

    def add_track(self, codec_id: str, import_type: str, track_id: str, path: str):
        top_item = QTreeWidgetItem(self.inputTreeWidget)
        top_item.setCheckState(0, Qt.CheckState.Checked)
        top_item.setText(0, codec_id)
        top_item.setText(1, getattr(LANG_UI_TXT.TaskEdit.task_type, import_type, import_type))
        top_item.setText(2, track_id)
        top_item.setText(3, path)
        top_item.setTextAlignment(1, Qt.AlignmentFlag.AlignCenter)
        top_item.setTextAlignment(2, Qt.AlignmentFlag.AlignCenter)
        self.allTypes.append(import_type)

    def parse_input(self, path: str, import_type: str):
        no_track = True
        if import_type == 'Audio':
            try:
                mi = pymediainfo.MediaInfo.parse(path,
                                                 full=False,
                                                 parse_speed=SETTINGS.parseSpeed,
                                                 library_file=MEDIAINFO.absoluteFilePath())
            except Exception as e:
                QMessageBox.warning(self,
                                    LANG_UI_TXT.fileDialog.open,
                                    str(e),
                                    QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok)
            else:
                for track in mi.to_data().get('tracks', []):
                    track: dict
                    if track.get('track_type') == import_type:
                        no_track = False
                        self.add_track(track.get('codec_id', ''),
                                       import_type,
                                       str(track.get('track_id', '')),
                                       path)
        elif import_type == 'Text':
            no_track = False
            self.add_track('', import_type, '', path)
        elif import_type == 'Menu':
            no_track = False
            self.add_track('', import_type, '', path)
        return no_track

    def set_info(self, task: Task, task_num: int, editable: bool = True):
        self.task = task
        self.inputLine.setText(task.input)
        self.outputLine.setText(task.output)
        command = task.command
        self.commandPlainTextEdit.clear()
        self.inputTreeWidget.clear()
        if task.type == 'bat':
            command = command.splitlines()[0] if command else command
            self.commandPlainTextEdit.setPlainText(command)
            self.commandPlainTextEdit.setMaximumBlockCount(1)
            self.inputLine.setDisabled(True)
            self.outputLine.setDisabled(True)
            self.inputTreeWidget.setDisabled(True)
            self.importSubtitleButton.setDisabled(True)
            self.importChapterButton.setDisabled(True)
            self.importAudioButton.setDisabled(True)
        else:
            self.commandPlainTextEdit.setMaximumBlockCount(99)
            self.inputLine.setEnabled(True)
            self.outputLine.setEnabled(True)
            if QFileInfo(task.output).suffix() not in VIDEO_EXTS:
                self.inputTreeWidget.setDisabled(True)
                self.importSubtitleButton.setDisabled(True)
                self.importChapterButton.setDisabled(True)
                self.importAudioButton.setDisabled(True)
            else:
                self.inputTreeWidget.setEnabled(True)
                self.importSubtitleButton.setEnabled(True)
                self.importChapterButton.setEnabled(True)
                self.importAudioButton.setEnabled(True)
                self.allTypes.clear()
                for track in task.tracks:
                    if type(track) == Track:
                        self.add_track(track.codec_id,
                                       track.track_type,
                                       track.track_id,
                                       track.track_path)
                self.inputTreeWidget.resizeColumnToContents(0)
                self.inputTreeWidget.resizeColumnToContents(1)
                self.inputTreeWidget.resizeColumnToContents(2)
                self.inputTreeWidget.resizeColumnToContents(3)
                self.inputTreeWidget.resizeColumnToContents(4)
            commands = [line.strip() for line in command.split('--')]
            for line in commands:
                if line:
                    self.commandPlainTextEdit.appendPlainText(f'--{line.strip()}')
            self.commandPlainTextEdit.setMaximumBlockCount(99)
            if self.codeEditor.isEnabled():
                if self.codeEditor.codeType == CodeEditor.CodeType.Vpy:
                    encoding = 'utf-8'
                else:
                    encoding = None
                with open(self.inputLine.text(), 'r', encoding=encoding, errors='ignore') as f:
                    self.codeEditor.setPlainText(f.read())

                self.saveButton.setDisabled(True)
                self.resetButton.setDisabled(True)

        self.applyButton.setDisabled(True)
        self.confirmButton.setDisabled(True)
        self.row = task_num
        if editable:
            self.setEnabled(True)
        else:
            self.setDisabled(True)

    def edit_code(self):
        self.saveButton.setEnabled(True)
        self.resetButton.setEnabled(True)

    def save(self):
        input_path = self.inputLine.text()
        file_info = QFileInfo(input_path)
        task_type = file_info.suffix().lower()
        if task_type == 'vpy':
            encoding = 'utf-8'
        elif task_type == 'avs':
            encoding = None
        else:
            encoding = 'utf-8'
        if file_info.isWritable():
            with open(input_path, 'w', encoding=encoding) as f:
                f.write(self.codeEditor.toPlainText())
            QMessageBox.information(
                self,
                LANG_UI_TXT.info.success,
                LANG_UI_TXT.info.save_success,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
            self.saveButton.setDisabled(True)
            self.resetButton.setDisabled(True)
        else:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                LANG_UI_TXT.info.permission,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)

    def reset(self):
        input_path = self.inputLine.text()
        task_type = QFileInfo(input_path).suffix().lower()
        if task_type == 'vpy':
            encoding = 'utf-8'
        elif task_type == 'avs':
            encoding = None
        else:
            encoding = 'utf-8'
        try:
            with open(input_path, 'r', encoding=encoding) as f:
                self.codeEditor.setPlainText(f.read())
        except Exception as e:
            QMessageBox.warning(self,
                                LANG_UI_TXT.info.error,
                                str(e),
                                QMessageBox.StandardButton.Ok)
        else:
            self.saveButton.setDisabled(True)
            self.resetButton.setDisabled(True)

    def append(self):
        output_path = self.outputLine.text()
        if (input_path := self.inputLine.text()) and output_path:
            document = self.commandPlainTextEdit.document()
            errors = []
            commands = []
            codes = []
            err_blocks = []
            for row in range(document.blockCount()):
                block = document.findBlockByNumber(row)
                text = block.text().strip()
                if text:
                    commands.append(text)

                    reg = QRegularExpression(r'^--(\S+)')
                    if len(text) < 5 or text[:2] != '--':
                        errors.append(f"{row + 1:02}: {LANG_UI_TXT.info.command_error}{text}")
                        err_blocks.append(block)
                    elif (match := reg.match(text)).hasMatch():
                        if (command := match.captured(1)) in codes:
                            err_blocks.append(block)
                            errors.append(f"{row + 1:02} {LANG_UI_TXT.info.command_repeat}{command}")
                        else:
                            codes.append(command)
            if errors:
                warning = '\n'.join(errors)
                self.commandPlainTextEdit.setFocus()
                self.commandPlainTextEdit.setTextCursor(QTextCursor(err_blocks[-1]))
                self.commandPlainTextEdit.moveCursor(QTextCursor.MoveOperation.EndOfLine,
                                                     QTextCursor.MoveMode.KeepAnchor)
                QMessageBox.warning(
                    self,
                    LANG_UI_TXT.info.error,
                    warning,
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
            else:
                command = ' '.join(commands)
                chapter_num = 0
                for row in range(self.inputTreeWidget.topLevelItemCount()):
                    item = self.inputTreeWidget.topLevelItem(row)
                    if not item.isDisabled() \
                            and item.checkState(0) == Qt.CheckState.Checked \
                            and self.allTypes[row] == 'Menu':
                        chapter_num += 1
                if chapter_num > 1:
                    QMessageBox.warning(self,
                                        '章节过多',
                                        '只允许1个章节',
                                        QMessageBox.StandardButton.Ok,
                                        QMessageBox.StandardButton.Ok)
                else:
                    task_type = QFileInfo(input_path).suffix().lower()
                    if task_type not in ('vpy', 'avs', 'yuv'):
                        task_type = 'raw'
                        if MEDIAINFO.absoluteFilePath():
                            try:
                                mi = pymediainfo.MediaInfo.parse(input_path,
                                                                 full=False,
                                                                 parse_speed=SETTINGS.parseSpeed,
                                                                 library_file=MEDIAINFO.absoluteFilePath())
                            except Exception as e:
                                QMessageBox.warning(self,
                                                    LANG_UI_TXT.info.error,
                                                    str(e),
                                                    QMessageBox.StandardButton.Ok,
                                                    QMessageBox.StandardButton.Ok)
                                return None
                            else:
                                info = mi.to_data().get('tracks', [])
                                for track in info:
                                    if track.get('track_type') == 'Video':
                                        break
                                else:
                                    QMessageBox.warning(self, LANG_UI_TXT.info.error,
                                                        LANG_UI_TXT.info.video_track_not_found,
                                                        QMessageBox.StandardButton.Ok,
                                                        QMessageBox.StandardButton.Ok)
                                    self.inputLine.selectAll()
                                    self.inputLine.setFocus()
                                    return None
                        else:
                            QMessageBox.warning(self,
                                                LANG_UI_TXT.info.error,
                                                f'mediainfo {LANG_UI_TXT.SettingWidget.disable}',
                                                QMessageBox.StandardButton.Ok,
                                                QMessageBox.StandardButton.Ok)
                            return None

                    tasks = [file.completeBaseName()[3:] for file in TASK_DIR.entryInfoList()]
                    tasks.sort()
                    last = int(tasks[-1]) if tasks else 0
                    last += 1
                    task_name = f'job{last:03}.task'

                    task = Task(input_path, output_path, task_type, Task.States.WAITING, '', '', command,
                                file_name=task_name, parent=self.parent.tasks)
                    if self.inputTreeWidget.isEnabled():
                        for row in range(self.inputTreeWidget.topLevelItemCount()):
                            item = self.inputTreeWidget.topLevelItem(row)
                            if not item.isDisabled() and item.checkState(0) == Qt.CheckState.Checked:
                                texts = [item.text(c) for c in range(4)]
                                task.tracks.append(Track(texts[0], self.allTypes[row], texts[2], texts[3]))

                    task_table_widget = self.parent.taskTableWidget
                    row = task_table_widget.rowCount()
                    task_table_widget.setRowCount(row + 1)
                    for column, text in enumerate(task.to_tuple()):
                        if column == 3:
                            text = LANG_UI_TXT.EncodeWidget.state[text]
                        item = QTableWidgetItem(text)
                        item.setToolTip(text)
                        if column in range(2, 6):
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        task_table_widget.setItem(row, column, item)
                        task_table_widget.resizeRowToContents(row)
                    task.save()
                    self.close()
        else:
            QMessageBox.warning(self,
                                LANG_UI_TXT.info.error,
                                LANG_UI_TXT.info.no_empty,
                                QMessageBox.StandardButton.Ok,
                                QMessageBox.StandardButton.Ok)

    def confirm(self):
        task = self.task
        if self.inputLine.text() or task.type == 'bat':
            if self.outputLine.text() or task.type == 'bat':
                document = self.commandPlainTextEdit.document()
                errors = []
                commands = []
                codes = []
                err_blocks = []
                if task.type == 'bat':
                    block = document.findBlockByNumber(0)
                    text = block.text().strip()
                    commands.append(text)
                    if not text:
                        errors.append(LANG_UI_TXT.info.no_empty)
                        err_blocks.append(block)
                else:
                    for row in range(document.blockCount()):
                        block = document.findBlockByNumber(row)
                        text = block.text().strip()
                        if text:
                            commands.append(text)

                            if len(text) < 5 or text[:2] != '--':
                                errors.append(f"{row + 1:02}: {LANG_UI_TXT.info.command_error}{text}")
                                err_blocks.append(block)
                            elif (match := QRegularExpression(r'^--(\S+)').match(text)).hasMatch():
                                if (command := match.captured(1)) in codes:
                                    err_blocks.append(block)
                                    errors.append(f"{row + 1:02} {LANG_UI_TXT.info.command_repeat}{command}")
                                else:
                                    codes.append(command)
                if errors:
                    warning = '\n'.join(errors)
                    self.commandPlainTextEdit.setFocus()
                    self.commandPlainTextEdit.setTextCursor(QTextCursor(err_blocks[-1]))
                    self.commandPlainTextEdit.moveCursor(QTextCursor.MoveOperation.EndOfLine,
                                                         QTextCursor.MoveMode.KeepAnchor)
                    QMessageBox.warning(
                        self,
                        LANG_UI_TXT.info.error,
                        warning,
                        QMessageBox.StandardButton.Ok,
                        QMessageBox.StandardButton.Ok)
                else:
                    command = ' '.join(commands)
                    task = self.task

                    if self.inputLine.isEnabled():
                        chapter_num = 0
                        for row in range(self.inputTreeWidget.topLevelItemCount()):
                            item = self.inputTreeWidget.topLevelItem(row)
                            if not item.isDisabled() \
                                    and item.checkState(0) == Qt.CheckState.Checked \
                                    and self.allTypes[row] == 'Menu':
                                chapter_num += 1
                        if chapter_num > 1:
                            QMessageBox.warning(self,
                                                '章节过多',
                                                '只允许1个章节',
                                                QMessageBox.StandardButton.Ok,
                                                QMessageBox.StandardButton.Ok)
                            return None
                        else:
                            input_name = self.inputLine.text()
                            task_type = QFileInfo(input_name).suffix().lower()
                            if task_type not in ('vpy', 'avs', 'yuv', 'bat'):
                                task_type = 'raw'
                            output_name = self.outputLine.text()
                            task.input = input_name
                            task.output = output_name
                            task.type = task_type
                            task.tracks.clear()
                            if self.inputTreeWidget.isEnabled():
                                for row in range(self.inputTreeWidget.topLevelItemCount()):
                                    item = self.inputTreeWidget.topLevelItem(row)
                                    if not item.isDisabled() and item.checkState(0) == Qt.CheckState.Checked:
                                        texts = [item.text(c) for c in range(4)]
                                        task.tracks.append(Track(texts[0], self.allTypes[row], texts[2], texts[3]))

                    task.command = command
                    task.save()
                    self.applyButton.setDisabled(True)

                    if self.sender() == self.confirmButton:
                        self.close()
            else:
                QMessageBox.warning(self,
                                    LANG_UI_TXT.info.error,
                                    LANG_UI_TXT.info.output_file_can_not_be_empty,
                                    QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok)
        else:
            QMessageBox.warning(self,
                                LANG_UI_TXT.info.error,
                                LANG_UI_TXT.info.input_file_can_not_be_empty,
                                QMessageBox.StandardButton.Ok,
                                QMessageBox.StandardButton.Ok)

    def closeEvent(self, event) -> None:
        if self.saveButton.isEnabled():
            answer = QMessageBox.question(
                self,
                LANG_UI_TXT.info.not_saved,
                LANG_UI_TXT.info.save_ask,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes)
            if answer == QMessageBox.StandardButton.Yes:
                self.save()
            self.saveButton.setDisabled(True)
            self.resetButton.setDisabled(True)

        if self.mode == 'edit':
            if self.applyButton.isEnabled():
                answer = QMessageBox.question(
                    self,
                    LANG_UI_TXT.info.not_saved,
                    LANG_UI_TXT.info.save_ask,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                    QMessageBox.StandardButton.Yes)
                if answer == QMessageBox.StandardButton.Yes:
                    self.confirm()
                    self.parent.taskTableWidget.setEnabled(True)
                elif answer == QMessageBox.StandardButton.Cancel:
                    event.ignore()
                else:
                    self.parent.taskTableWidget.setEnabled(True)
            else:
                self.parent.taskTableWidget.setEnabled(True)
        elif self.mode == 'append':
            pass


class TaskTableWidget(QTableWidget):
    class Column(IntEnum):
        INPUT = 0
        OUTPUT = 1
        TYPE = 2
        STATUS = 3
        START = 4
        END = 5
        COMMAND = 6

    def __init__(self, parent: TaskOperationWidget, tasks: TaskList, *args, **kwargs):
        super().__init__(parent=parent, *args, **kwargs)
        self.parent = parent
        self.tasks = tasks
        self.menu = QMenu(self)
        self.editAct = QWidgetAction(self.menu)
        self.deleteAct = QWidgetAction(self.menu)
        self.waitingAct = QWidgetAction(self.menu)
        self.abortAct = QWidgetAction(self.menu)
        self.clearTaskAct = QWidgetAction(self.menu)
        self.clearMessageAct = QWidgetAction(self.menu)
        self.openInputAct = QWidgetAction(self.menu)
        self.openInputDirAct = QWidgetAction(self.menu)
        self.openOutputAct = QWidgetAction(self.menu)
        self.openOutputDirAct = QWidgetAction(self.menu)
        self.exportBatAct = QWidgetAction(self.menu)
        self.taskEditor = TaskEditionWidget(parent=self.parent,
                                            input_ext=ExtGroup('vpy',
                                                               'avs',
                                                               'yuv',
                                                               'avi',
                                                               Ext('mp4', 'm4v'),
                                                               'mov',
                                                               Ext('3gp', '3g2'),
                                                               Ext('m2ts', 'ts'),
                                                               'm2v',
                                                               Ext('mpeg', 'mpg'),
                                                               Ext('ogm', 'ogv'),
                                                               'vob',
                                                               Ext('mkv', 'webm'),
                                                               'flv',
                                                               Ext('rmvb', 'rm'),
                                                               Ext('wmv', 'wm')),
                                            output_ext=ExtGroup(SETTINGS.rawHevcExt, 'mkv', 'mp4'))

        self.acts = (
                    self.waitingAct,
                    self.abortAct,
                    self.editAct,
                    self.deleteAct,
                    self.clearTaskAct,
                    self.clearMessageAct,
                    self.openInputAct,
                    self.openInputDirAct,
                    self.openOutputAct,
                    self.openOutputDirAct,
                    self.exportBatAct)
        self.init_ui()

    def init_ui(self):
        for n, i in enumerate(self.acts):
            if n in (2, 5, 6, 10):
                self.menu.addSeparator()
            self.menu.addAction(i)

        font = QFont()
        font.setPixelSize(FONT_SIZE - 4)
        self.horizontalHeader().setFont(font)
        self.verticalHeader().setFont(font)
        self.setColumnCount(7)
        self.setWordWrap(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_menu)
        self.itemSelectionChanged.connect(self.change_task)
        self.setColumnWidth(0, 180)
        self.setColumnWidth(1, 180)
        self.setColumnWidth(6, 130)
        self.doubleClicked.connect(self.edit_task)
        self.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        self.deleteAct.triggered.connect(self.delete_task)
        self.deleteAct.setIcon(set_icon(svgs.delete))
        self.clearTaskAct.triggered.connect(self.clear_task)
        self.clearTaskAct.setIcon(set_icon(svgs.clear))
        self.editAct.triggered.connect(self.edit_task)
        self.editAct.setIcon(set_icon(svgs.edit))
        self.waitingAct.triggered.connect(self.change_state)
        self.waitingAct.setIcon(set_icon(svgs.wait))
        self.abortAct.triggered.connect(self.change_state)
        self.abortAct.setIcon(set_icon(svgs.abort))
        self.clearMessageAct.triggered.connect(self.clear_message)
        self.clearMessageAct.setIcon(set_icon(svgs.clear_msg))
        self.openInputAct.triggered.connect(self.open_file)
        self.openInputAct.setIcon(set_icon(svgs.file))
        self.openInputDirAct.triggered.connect(self.open_dir)
        self.openInputDirAct.setIcon(set_icon(svgs.folder))
        self.openOutputAct.triggered.connect(self.open_file)
        self.openOutputAct.setIcon(set_icon(svgs.file))
        self.openOutputDirAct.triggered.connect(self.open_dir)
        self.openOutputDirAct.setIcon(set_icon(svgs.folder))
        self.exportBatAct.triggered.connect(self.export_bat)
        self.exportBatAct.setIcon(set_icon(svgs.bat))

    def init_language(self):
        self.taskEditor.init_language()
        for n, i in enumerate(LANG_UI_TXT.EncodeWidget.tasks):
            item = QTableWidgetItem(i)
            self.setHorizontalHeaderItem(n, item)
            if n in range(2, 6):
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        sample_texts = (self.horizontalHeaderItem(2).text(),
                        'waiting',
                        '00-00 00:00:00',
                        '00-00 00:00:00')
        for c, text in zip(range(2, 6), sample_texts):
            self.setColumnWidth(c, QFontMetrics(self.font()).horizontalAdvance(
                text) + 10)

        for i, text in zip(self.acts, LANG_UI_TXT.EncodeWidget.action):
            i.setText(text)

        for row, task in enumerate(self.tasks):
            self.item(row, self.Column.STATUS).setText(LANG_UI_TXT.EncodeWidget.state[task.status.value])

    def init_font(self, font: QFont):
        self.setFont(font)
        for c in range(self.horizontalHeader().count()):
            self.horizontalHeaderItem(c).setFont(font)
        for row in range(self.verticalHeader().count()):
            if i := self.verticalHeaderItem(row):
                i.setFont(font)

        self.resizeRowsToContents()

        sample_texts = (self.horizontalHeaderItem(2).text(),
                        'waiting',
                        '00-00 00:00:00',
                        '00-00 00:00:00')
        for c, text in zip(range(2, 6), sample_texts):
            self.setColumnWidth(c, QFontMetrics(font).horizontalAdvance(text) + 10)

        self.taskEditor.init_font(font)
        for c, text in zip(range(2, 6), sample_texts):
            self.setColumnWidth(c, QFontMetrics(self.font()).horizontalAdvance(
                text) + 10)

    def init_tasks(self):
        for n, task_name in enumerate(TASK_DIR.entryList()):
            path = TASK_DIR.absoluteFilePath(task_name)
            has_error = False
            with open(path, 'rb') as f:
                try:
                    data = json.load(f)
                    if type(data) != dict:
                        raise TypeError
                    else:
                        for p in ('input', 'output', 'type', 'start', 'end', 'command'):
                            if type(data[p]) != str:
                                raise TypeError
                        if data['status'] not in range(8):
                            raise ValueError
                        if data['type'] == 'bat' and (not data['command'] or len(data['command'].splitlines()) > 1):
                            raise ValueError
                        message = Message()
                        for top, sub in data['message']:
                            if type(top) == str:
                                message.add_top(top)
                                if type(sub) == list:
                                    for msg in sub:
                                        if type(msg) == str:
                                            message.add_msg(msg)
                                        else:
                                            raise TypeError
                                else:
                                    raise TypeError
                            else:
                                raise TypeError
                        tracks = []
                        for track in data['tracks']:
                            if type(track) == dict:
                                if all([type(track[p]) == str for p in ('codec_id', 'track_type', 'track_id', 'track_path')]):
                                    _track = Track(codec_id=track['codec_id'],
                                                   track_type=track['track_type'],
                                                   track_id=track['track_id'],
                                                   track_path=track['track_path'])
                                    tracks.append(_track)
                                else:
                                    raise ValueError
                            else:
                                raise TypeError
                except (TypeError, KeyError, ValueError, UnicodeDecodeError, AttributeError,
                        json.decoder.JSONDecodeError, EOFError) as e:
                    print(f'[error]任务导入失败：{type(e)} {str(e)}')
                    has_error = True
                else:
                    if data['status'] == 1:
                        data['status'] = 0
                        data['start'] = ''

                    task = Task(data['input'], data['output'], data['type'], Task.States(data['status']),
                                data['start'], data['end'], data['command'],
                                file_name=path, parent=self.tasks)
                    task.message.from_list(message)
                    task.tracks.extend(tracks)
                    self.setRowCount(self.rowCount() + 1)

                    values = task.to_tuple()
                    for col, value in enumerate(values):
                        if col == 3:
                            value = LANG_UI_TXT.EncodeWidget.state[value]
                        item = QTableWidgetItem(value)
                        if col in range(2, 6):
                            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        else:
                            item.setToolTip(value)
                        self.setItem(n, col, item)
                        self.resizeRowToContents(n)
            if has_error:
                QDir().remove(path)

    def filter_task(self, index: int):
        if index:
            for row in range(self.rowCount()):
                if self.tasks[row].status == index - 1:
                    self.showRow(row)
                else:
                    self.hideRow(row)
        else:
            for row in range(self.rowCount()):
                self.showRow(row)

    def edit_task(self):
        row = self.currentRow()
        if (task := self.tasks[row]).status == Task.States.RUNNING:
            editable = False
        else:
            editable = True
        self.taskEditor.set_info(task, row, editable)
        self.setDisabled(True)
        self.taskEditor.show()

    def clear_task(self):
        self.clearContents()
        self.setRowCount(0)
        self.tasks.clear()
        self.tasks.save()

    def show_menu(self, point: QPoint = QPoint(), *, popup=True):
        for act in self.acts:
            act.setEnabled(True)
        running = True if self.tasks.cur_index > -1 else False
        if running:
            self.clearTaskAct.setDisabled(True)
        if selection := self.selectedRanges():
            top_row = selection[0].topRow()
            if len(selection) == 1 and selection[0].rowCount() == 1:
                if top_row == self.tasks.cur_index:
                    self.waitingAct.setDisabled(True)
                    self.editAct.setDisabled(True)
                    self.abortAct.setDisabled(True)
                    self.editAct.setDisabled(True)
                    self.clearMessageAct.setDisabled(True)
                    self.deleteAct.setDisabled(True)
            else:
                if running:
                    for select in selection:
                        if self.tasks.cur_index in range(select.topRow(), select.bottomRow() + 1):
                            self.clearMessageAct.setDisabled(True)
        else:
            self.editAct.setDisabled(True)
            self.deleteAct.setDisabled(True)
            self.abortAct.setDisabled(True)
            self.waitingAct.setDisabled(True)
            self.openOutputDirAct.setDisabled(True)
            self.openOutputAct.setDisabled(True)
            self.openInputDirAct.setDisabled(True)
            self.openInputAct.setDisabled(True)
            self.clearMessageAct.setDisabled(True)
        if popup:
            self.menu.popup(self.mapToGlobal(point))

    def delete_task(self):
        selection = self.selectedRanges()
        has_error = False
        failed_index = []
        for select in reversed(selection):
            for row in reversed(range(select.topRow(), select.bottomRow() + 1)):
                file_name = self.tasks[row].file_name
                if self.tasks.remove(row):
                    self.removeRow(row)
                    if TASK_DIR.remove(file_name):
                        print('删除成功')
                    else:
                        try:
                            with open(TASK_DIR.absoluteFilePath(file_name), 'w', errors='ignore'):
                                pass
                        except Exception as e:
                            print(str(e))
                            has_error = True
                else:
                    failed_index.append(row+1)
        if has_error:
            self.tasks.save()
        if self.tasks.cur_index != -1:
            self.parent.numLine.setText(f'{self.tasks.cur_index + 1}/{len(self.tasks)}')
        if failed_index:
            msg = ', '.join(failed_index)
            QMessageBox.warning(self,
                                LANG_UI_TXT.info.error,
                                f'任务{msg}正在运行，无法删除',
                                QMessageBox.Ok,
                                QMessageBox.Ok)

    def change_state(self):
        action = self.sender()
        selection = self.selectedRanges()
        cur_time = get_time()
        if action in (self.waitingAct, self.abortAct):
            for select in reversed(selection):
                for row in reversed(range(select.topRow(), select.bottomRow() + 1)):
                    task = self.tasks[row]
                    if self.tasks.cur_index != row:
                        msg = Task.States.WAITING if action == self.waitingAct else Task.States.ABORT
                        task.status = msg
                        task.start = ''
                        task.end = ''
                        self.parent.messageTreeWidget.append_message(f'[{cur_time}]更改状态：{msg.name}', task=task, save=False)
                        task.save()

    def change_task(self):
        self.parent.change_task()

    def clear_message(self):
        self.parent.clear_message()

    def open_file(self):
        sender = self.sender()
        col = 0 if sender == self.openInputAct else 1
        row = self.currentRow()
        item = self.item(row, col)
        for name in (item.text(), f'file:{item.text()}', f'file:///{item.text()}'):
            if QDesktopServices.openUrl(QUrl(name)):
                item.setForeground(QBrush(QColor(Qt.GlobalColor.black)))
                break
        else:
            if QFileInfo(item.text()).exists():
                QMessageBox.warning(
                    self,
                    LANG_UI_TXT.info.error,
                    f"{LANG_UI_TXT.info.fail_to_open_file}\n{item.text()}",
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
            else:
                item.setForeground(QBrush(QColor(Qt.GlobalColor.red)))
                if sender == self.openInputAct:
                    task = self.tasks[row]
                    task.status = Task.States.ERROR
                    task.save()
                QMessageBox.warning(
                    self,
                    LANG_UI_TXT.info.error,
                    f"{LANG_UI_TXT.info.not_found}\n{item.text()}",
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)

    def open_dir(self):
        sender = self.sender()
        column = 0 if sender == self.openInputDirAct else 1
        selection = self.selectedRanges()
        for row in reversed(range(selection[0].topRow(), selection[0].bottomRow() + 1)):
            if row != -1:
                item = self.item(row, column)
                file = QFileInfo(item.text())
                if sender == self.openInputDirAct and file.exists():
                    item.setForeground(QBrush(QColor(Qt.GlobalColor.black)))
                    QDesktopServices.openUrl(
                        QUrl(f'file:{file.absolutePath()}'))
                    QDesktopServices.openUrl(
                        QUrl(file.absolutePath()))
                elif sender == self.openOutputDirAct and \
                        (QDesktopServices.openUrl(QUrl(f'file:{file.absolutePath()}')) or QDesktopServices.openUrl(
                            QUrl(file.absolutePath()))):
                    item.setForeground(QBrush(QColor(Qt.GlobalColor.black)))
                else:
                    item.setForeground(QBrush(QColor(Qt.GlobalColor.red)))
                    row = self.currentRow()
                    task = self.tasks[row]
                    task.status = Task.States.ERROR
                    task.save()
                    QMessageBox.warning(self,
                                        LANG_UI_TXT.info.error,
                                        f"{LANG_UI_TXT.info.not_found}\n{file.absolutePath()}",
                                        QMessageBox.StandardButton.Ok,
                                        QMessageBox.StandardButton.Ok)

    def export_bat(self):
        selection = self.selectedRanges()
        commands = []
        msgs = []
        for select in reversed(selection):
            for row in reversed(range(select.topRow(), select.bottomRow() + 1)):
                task = self.tasks[row]
                task: Task
                input_path = task.input
                output_dir = QFileInfo(task.output).absoluteDir()
                base_name = QFileInfo(task.output).completeBaseName()
                raw_output = QFileInfo(output_dir, f'{base_name}.{SETTINGS.rawHevcExt}').absoluteFilePath()

                if task.type == 'vpy':
                    command = f'"{VSPIPE.absoluteFilePath()}" -c y4m "{task.input}" -| ' \
                              f'"{X265.absoluteFilePath()}" {task.command} -o "{raw_output}" --y4m --input -'
                    commands.append(command)
                elif task.type == 'avs':
                    command = f'"{AVS4X26X.absoluteFilePath()}" -L "{X265.absoluteFilePath()}" {task.command}' \
                              f' -o "{raw_output}" "{input_path}"'
                    commands.append(command)
                elif task.type == 'bat':
                    commands.append(task.command)
                elif task.type == 'yuv':
                    command = f'"{X265.absoluteFilePath()}" --input "{input_path}" {task.command} -o "{raw_output}"'
                    commands.append(command)
                elif task.type == 'raw':
                    msgs.append(f'{LANG_UI_TXT.info.task} {row + 1:02}: '
                                f'{LANG_UI_TXT.info.task_type_is} "{task.type}",'
                                f' {LANG_UI_TXT.info.unable_to_convert_bat}')
                else:
                    msgs.append(f'{LANG_UI_TXT.info.task} {row + 1:02}: '
                                f'{LANG_UI_TXT.info.task_type_is} "{task.type}", {LANG_UI_TXT.info.unrecognized}')
        if msgs:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                '\n'.join(msgs),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
        if commands:
            export_path = QFileDialog.getSaveFileName(self,
                                                      LANG_UI_TXT.fileDialog.save,
                                                      SETTINGS.recentDir,
                                                      f'{getattr(LANG_UI_TXT.fileType, "bat", "bat")} (*.bat)')[0]
            if export_path:
                if QFileInfo(export_path).isWritable():
                    with open(export_path, 'w') as f:
                        f.write('\n'.join(reversed(commands)))
                    QMessageBox.information(
                        self,
                        LANG_UI_TXT.info.success,
                        LANG_UI_TXT.info.success,
                        QMessageBox.StandardButton.Ok,
                        QMessageBox.StandardButton.Ok)
                else:
                    QMessageBox.warning(
                        self,
                        LANG_UI_TXT.info.error,
                        LANG_UI_TXT.info.permission,
                        QMessageBox.StandardButton.Ok,
                        QMessageBox.StandardButton.Ok)

    def task_finished(self):
        self.clearTaskAct.setEnabled(True)
        if not self.menu.isHidden():
            self.show_menu(self.menu.pos(), popup=False)


class InputTreeWidget(QTreeWidget):
    def __init__(self, parent: TaskEditionWidget):
        super().__init__(parent)
        self.parent = parent
        self.setDragEnabled(True)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e: QDragEnterEvent):
        if e.source() == self:
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QDropEvent):
        item = self.itemAt(e.position().toPoint())
        if item:
            row = self.indexOfTopLevelItem(item)
        else:
            row = self.topLevelItemCount()
        if e.source() == self:
            cur_row = self.indexOfTopLevelItem(self.currentItem())
            cur_item = self.takeTopLevelItem(cur_row)
            cur_type = self.parent.allTypes.pop(cur_row)
            if row > self.topLevelItemCount():
                row = self.topLevelItemCount()
            self.insertTopLevelItem(row, cur_item)
            self.parent.allTypes.insert(row, cur_type)
            self.parent.applyButton.setEnabled(True)
            self.parent.confirmButton.setEnabled(True)

    def keyReleaseEvent(self, a0) -> None:
        if a0.key() == Qt.Key.Key_Delete:
            if (row := self.currentIndex().row()) >= 0:
                self.takeTopLevelItem(row)
                del self.parent.allTypes[row]


class TaskAppendTreeWidget(QTreeWidget):
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

    def __init__(self, parent: TaskAppendWidget):
        super().__init__(parent)
        self.parent = parent
        self.home = QHBoxLayout(self)
        self.back = self.Back('#ffffff')
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
        self.setColumnCount(3)
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
        self.removeButton.setIcon(set_icon(svgs.remove))
        self.clearButton.setIcon(set_icon(svgs.clear))
        self.topButton.setIcon(set_icon(svgs.top))
        self.upButton.setIcon(set_icon(svgs.up))
        self.downButton.setIcon(set_icon(svgs.down))
        self.bottomButton.setIcon(set_icon(svgs.bottom))
        self.removeButton.clicked.connect(self.remove)
        self.clearButton.clicked.connect(self.clear)
        self.topButton.clicked.connect(self.top)
        self.upButton.clicked.connect(self.up)
        self.downButton.clicked.connect(self.down)
        self.bottomButton.clicked.connect(self.bottom)

    def add_input(self):
        self.addTopLevelItem(QTreeWidgetItem())
