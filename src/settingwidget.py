from PySide6.QtWidgets import QLineEdit, QLabel, \
    QVBoxLayout, QPushButton, QHBoxLayout, QComboBox, QTabWidget, QFontComboBox, \
    QCheckBox, QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout, QCompleter
from PySide6.QtGui import QRegularExpressionValidator
from PySide6.QtCore import QRegularExpression, Qt
import pymediainfo
import svgs
from MyWidgets import CheckThread, PathLineEdit, CodeEditor, ExtGroup
from data import *


class SettingWidget(QWidget):
    def __init__(self, parent, /, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        from x265 import MainWidget
        self.mainWidget: MainWidget = parent
        self.home = QVBoxLayout(self)
        self.tab = QTabWidget(self)
        self.buttonBox = QHBoxLayout()

        self.autoLoadSavCheckBox = QCheckBox(self)
        self.loadVideoCmdCheckBox = QCheckBox(self)
        self.svtCheckBox = QCheckBox(self)
        self.rememberRecentDirCheckBox = QCheckBox(self)

        self.group_box3_1 = QGroupBox(self)
        self.group_box3_2 = QGroupBox(self)
        self.group_box3_3 = QGroupBox(self)

        self.x265File = None
        self.vspipeFile = None
        self.avs4x26xFile = None
        self.mkvmergeFile = None
        self.mp4boxFile = None
        self.x265Thread = CheckThread('x265', ' --version', b'x265 [info]: HEVC encoder version', 0, X265_PATH)
        self.vspipeThread = CheckThread('vspipe', ' -v', b'VapourSynth Video Processing Library', 0, VSPIPE_PATH)
        self.avs4x26xThread = CheckThread('avs4x26x', ' -o', b'avs4x26x [error]: No supported input file found', -1,
                                          AVS4X26X_PATH)
        self.mkvmergeThread = CheckThread('mkvmerge', ' -V', b'mkvmerge v', 0, MKVMERGE_PATH)
        self.mp4boxThread = CheckThread('mp4box', ' -version', b'MP4Box - GPAC version', 0, MP4BOX_PATH)
        self.x265Line = QLineEdit(self)
        self.vspipeLine = QLineEdit(self)
        self.avs4x26xLine = QLineEdit(self)
        self.mkvmergeLine = QLineEdit(self)
        self.mp4boxLine = QLineEdit(self)
        self.mediaInfoLine = QLineEdit(self)
        self.ffms2Label = QLabel(self)
        self.lsmasLabel = QLabel(self)
        self.avisourceLabel = QLabel(self)
        self.imwriLabel = QLabel(self)
        self.descaleLabel = QLabel(self)
        self.reloadButton = QPushButton(self)

        self.preloadCheckBox = QCheckBox(self)
        self.preloadTimeoutSpin = QSpinBox(self)
        self.preloadTimeoutLabel = QLabel(self)
        self.encodeTimeoutSpin = QSpinBox(self)
        self.encodeTimeoutLabel = QLabel(self)
        self.cacheMethodLabel = QLabel(self)
        self.cacheMethodComboBox = QComboBox(self)
        self.cacheLine = PathLineEdit(QFileDialog.getExistingDirectory, parent=self)
        self.cacheLabel = QLabel(self)
        self.clearCacheButton = QPushButton(self)
        self.cacheSizeLabel = QLabel(self)
        self.rawHevcExtLabel = QLabel(self)
        self.rawHevcExtLine = QLineEdit(self)

        self.languageLabel = QLabel(self)
        self.cmdLabel = QLabel(self)
        self.fontLabel = QLabel(self)
        self.fontComboBox = QFontComboBox(self)
        self.languageComboBox = QComboBox(self)
        self.cmdLanguageComboBox = QComboBox(self)

        self.parseSpeedLabel = QLabel(self)
        self.parseSpeedSpinBox = QDoubleSpinBox(self)
        self.vpyLabel = QLabel(self)
        self.avsLabel = QLabel(self)
        self.vpyStyleLine = CodeEditor(CodeEditor.CodeType.Vpy)
        self.avsStyleLine = CodeEditor()
        self.entryLabel = QLabel(self)
        self.insertTextLayout = QHBoxLayout()
        self.baseNameButton = QPushButton(self)
        self.suffixButton = QPushButton(self)
        self.fileNameButton = QPushButton(self)
        self.pathButton = QPushButton(self)

        self.confirmBox = QHBoxLayout()
        self.cancelButton = QPushButton(self)
        self.applyButton = QPushButton(self)
        self.restartLabel = QLabel(self)
        self.tabWidgets = [QWidget(self) for _ in range(5)]

        self.init_cmd()
        self.init_media()
        self.init_encode()
        self.init_display()
        self.init_program()
        self.init_ui()

    def init_cmd(self):
        widget = self.tabWidgets[1]
        home = QFormLayout(widget)
        home.addRow(self.autoLoadSavCheckBox)
        home.addRow(self.loadVideoCmdCheckBox)
        home.addRow(self.svtCheckBox)
        home.addRow(self.rememberRecentDirCheckBox)

        self.autoLoadSavCheckBox.stateChanged.connect(self.enable_apply)
        self.loadVideoCmdCheckBox.stateChanged.connect(self.enable_apply)
        self.loadVideoCmdCheckBox.setDisabled(True)
        self.svtCheckBox.stateChanged.connect(self.enable_apply)
        self.rememberRecentDirCheckBox.stateChanged.connect(self.enable_apply)

    def init_media(self):
        widget = self.tabWidgets[2]
        home = QFormLayout(widget)
        home.addRow(self.parseSpeedLabel, self.parseSpeedSpinBox)
        home.addRow(self.vpyLabel, self.vpyStyleLine)
        home.addRow(self.avsLabel, self.avsStyleLine)
        home.addRow(self.entryLabel, self.insertTextLayout)

        self.parseSpeedSpinBox.setRange(0, 1)
        self.parseSpeedSpinBox.setSingleStep(0.1)
        self.parseSpeedSpinBox.setDecimals(1)
        self.parseSpeedSpinBox.valueChanged.connect(self.enable_apply)

        self.avsStyleLine.setPlainText(SETTINGS.avsTemplate)
        self.avsStyleLine.textChanged.connect(self.enable_apply)
        self.vpyStyleLine.setPlainText(SETTINGS.vpyTemplate)
        self.vpyStyleLine.textChanged.connect(self.enable_apply)

        self.insertTextLayout.addWidget(self.baseNameButton)
        self.insertTextLayout.addWidget(self.suffixButton)
        self.insertTextLayout.addWidget(self.fileNameButton)
        self.insertTextLayout.addWidget(self.pathButton)
        self.baseNameButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.baseNameButton.clicked.connect(self.insert_entry)
        self.suffixButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.suffixButton.clicked.connect(self.insert_entry)
        self.fileNameButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.fileNameButton.clicked.connect(self.insert_entry)
        self.pathButton.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.pathButton.clicked.connect(self.insert_entry)

    def init_encode(self):
        widget = self.tabWidgets[3]

        home1 = QFormLayout(self.group_box3_1)
        home2 = QFormLayout(self.group_box3_2)
        home3 = QFormLayout(self.group_box3_3)

        home = QVBoxLayout(widget)
        home.addWidget(self.group_box3_1)
        home.addWidget(self.group_box3_2)
        home.addWidget(self.group_box3_3)
        home.addStretch(1)

        part_cache = QHBoxLayout()
        part_cache.addWidget(self.clearCacheButton)
        part_cache.addWidget(self.cacheSizeLabel)
        part_cache.addStretch(1)
        home1.addRow(self.cacheMethodLabel, self.cacheMethodComboBox)
        home1.addRow(self.cacheLabel, self.cacheLine)
        home1.addRow(part_cache)

        home2.addRow(self.preloadCheckBox)
        home2.addRow(self.preloadTimeoutLabel, self.preloadTimeoutSpin)

        home3.addRow(self.encodeTimeoutLabel, self.encodeTimeoutSpin)
        home3.addRow(self.rawHevcExtLabel, self.rawHevcExtLine)

        self.cacheLine.setObjectName('encodeCacheDir')
        self.cacheLine.textChanged.connect(self.set_size_label)

        self.cacheMethodComboBox.addItems([''] * 2)
        self.cacheMethodComboBox.currentIndexChanged.connect(self.change_cache_method)
        self.clearCacheButton.clicked.connect(self.clear_cache)

        self.preloadCheckBox.stateChanged.connect(self.preload)
        self.preloadTimeoutSpin.setRange(0, 99999)
        self.preloadTimeoutSpin.valueChanged.connect(self.enable_apply)
        self.preloadTimeoutSpin.setDisabled(True)
        self.encodeTimeoutSpin.setRange(0, 99999)
        self.encodeTimeoutSpin.valueChanged.connect(self.enable_apply)

        self.rawHevcExtLine.setValidator(QRegularExpressionValidator(QRegularExpression(r'[^/\\\*><\|\?:"]+')))
        self.rawHevcExtLine.textChanged.connect(self.enable_apply)

    def init_display(self):
        widget = self.tabWidgets[0]
        home = QFormLayout(widget)
        home.addRow(self.languageLabel, self.languageComboBox)
        home.addRow(self.cmdLabel, self.cmdLanguageComboBox)
        home.addRow(self.fontLabel, self.fontComboBox)
        self.languageComboBox.currentTextChanged.connect(self.enable_apply)
        self.cmdLanguageComboBox.currentTextChanged.connect(self.enable_apply)

        self.fontComboBox.setCurrentText(SETTINGS.fontFamily)
        self.fontComboBox.setCompleter(
            QCompleter([self.fontComboBox.itemText(row) for row in range(self.fontComboBox.count())]))
        self.fontComboBox.completer().setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        self.fontComboBox.currentIndexChanged.connect(self.enable_apply)

    def init_program(self):
        home1 = QFormLayout(self.tabWidgets[4])
        home1.addRow('x265', self.x265Line)
        home1.addRow('vspipe', self.vspipeLine)
        home1.addRow('avs4x26x', self.avs4x26xLine)
        home1.addRow('mkvmerge', self.mkvmergeLine)
        home1.addRow('mp4box', self.mp4boxLine)
        home1.addRow('mediainfo', self.mediaInfoLine)
        home1.addRow('ffms2', self.ffms2Label)
        home1.addRow('lsmash', self.lsmasLabel)
        home1.addRow('avisource', self.avisourceLabel)
        home1.addRow('ImageMagick W-R', self.imwriLabel)
        home1.addRow('Descale', self.descaleLabel)
        part_button = QHBoxLayout()
        part_button.addStretch(1)
        part_button.addWidget(self.reloadButton)
        home1.addRow(part_button)

        self.x265Line.setReadOnly(True)
        self.vspipeLine.setReadOnly(True)
        self.avs4x26xLine.setReadOnly(True)
        self.mkvmergeLine.setReadOnly(True)
        self.mp4boxLine.setReadOnly(True)
        self.mediaInfoLine.setReadOnly(True)
        self.reloadButton.clicked.connect(self.reload)
        self.x265Thread.finishSignal.connect(self.check_program)
        self.vspipeThread.finishSignal.connect(self.check_program)
        self.avs4x26xThread.finishSignal.connect(self.check_program)
        self.mkvmergeThread.finishSignal.connect(self.check_program)
        self.mp4boxThread.finishSignal.connect(self.check_program)

    def init_ui(self):
        shadow(self)
        self.home.setContentsMargins(10, 10, 10, 10)

        self.buttonBox.addStretch(1)
        self.buttonBox.addWidget(self.restartLabel)
        self.buttonBox.addWidget(self.applyButton)
        self.buttonBox.addWidget(self.cancelButton)

        self.home.addWidget(self.tab)
        self.home.addLayout(self.buttonBox)

        self.tab.currentChanged.connect(self.change_tab)
        for widget in self.tabWidgets:
            widget.setContentsMargins(0, 0, 0, 0)
            self.tab.addTab(widget, '')

        self.cacheLine.textChanged.connect(self.enable_apply)
        self.cacheLine.setReadOnly(True)

        self.cancelButton.clicked.connect(self.cancel)
        self.cancelButton.setDisabled(True)
        self.applyButton.clicked.connect(self.apply)
        self.applyButton.setDisabled(True)
        self.applyButton.setIcon(set_icon(svgs.save))

    def init_language(self):
        setting_text = LANG_UI_TXT.SettingWidget
        self.cancelButton.setText(LANG_UI_TXT.button.Cancel)
        self.applyButton.setText(LANG_UI_TXT.button.Apply)
        self.cacheLabel.setText(setting_text.cache)
        self.languageLabel.setText(setting_text.label)
        self.cmdLabel.setText(setting_text.cmd)
        self.avsLabel.setText(setting_text.avs)
        self.fontLabel.setText(setting_text.font)
        self.vpyLabel.setText(setting_text.vpy)
        self.entryLabel.setText(setting_text.entry)
        self.baseNameButton.setText(setting_text.base_name)
        self.suffixButton.setText(setting_text.suffix)
        self.fileNameButton.setText(setting_text.file_name)
        self.pathButton.setText(setting_text.path)
        for n, text in enumerate(setting_text.tab):
            self.tab.setTabText(n, text)
        self.autoLoadSavCheckBox.setText(setting_text.auto_load_sav)
        self.loadVideoCmdCheckBox.setText(setting_text.load_video_cmd)
        self.svtCheckBox.setText(setting_text.svt)
        self.rememberRecentDirCheckBox.setText(setting_text.remember_temp_dir)
        self.clearCacheButton.setText(setting_text.clear_cache_files)
        for n, text in enumerate(setting_text.cache_modes):
            self.cacheMethodComboBox.setItemText(n, text)
        self.cacheMethodLabel.setText(setting_text.cache_mode)
        if self.restartLabel.text():
            self.restartLabel.setText(setting_text.need_restart)
        self.reloadButton.setText(setting_text.reload)
        for filter_name, label in zip((FFMS2, LSMASH, AVISOURCE, IMWRI, DESCALE),
                                      (self.ffms2Label,
                                       self.lsmasLabel,
                                       self.avisourceLabel,
                                       self.imwriLabel,
                                       self.descaleLabel)):
            if filter_name:
                label.setText(setting_text.enable)
            else:
                label.setText(setting_text.disable)
        self.preloadCheckBox.setText(setting_text.preload)
        self.preloadTimeoutLabel.setText(setting_text.preload_timeout)
        self.encodeTimeoutLabel.setText(setting_text.encode_timeout)
        self.parseSpeedLabel.setText(setting_text.parse_speed)
        self.rawHevcExtLabel.setText(setting_text.raw_hevc_ext)

    def init_font(self, font: QFont):
        for i in self.findChildren(QWidget):
            i.setFont(font)
        self.vpyStyleLine.init_font(font)
        self.avsStyleLine.init_font(font)
        self.tab.setFont(font)
        self.tab.tabBar().setFont(font)
        self.baseNameButton.setFont(font)
        self.suffixButton.setFont(font)
        self.fileNameButton.setFont(font)
        self.pathButton.setFont(font)

    def init_programs(self):
        def init_checkbox(checkbox: QCheckBox, setting: int) -> bool:
            if setting != 0:
                checkbox.setChecked(True)
                return True
            else:
                checkbox.setChecked(False)
                return False

        self.reload()
        if not QDir(SETTINGS.recentDir).exists():
            SETTINGS.recentDir = WORK_DIR.absolutePath()

        init_checkbox(self.autoLoadSavCheckBox, SETTINGS.autoLoadSav)
        init_checkbox(self.loadVideoCmdCheckBox, SETTINGS.loadVideoCmd)
        if init_checkbox(self.svtCheckBox, SETTINGS.svt):
            self.mainWidget.commandWidget.svtCheckBox.setEnabled(True)
        else:
            self.mainWidget.commandWidget.svtCheckBox.setDisabled(True)
        self.parseSpeedSpinBox.setValue(float(SETTINGS.parseSpeed))
        init_checkbox(self.rememberRecentDirCheckBox, SETTINGS.rememberRecentDir)
        init_checkbox(self.preloadCheckBox, SETTINGS.preload)

        self.preloadTimeoutSpin.setValue(SETTINGS.preloadTimeout)
        self.encodeTimeoutSpin.setValue(SETTINGS.encodeTimeout)
        SETTINGS.rawHevcExt = SETTINGS.rawHevcExt if SETTINGS.rawHevcExt else 'h265'
        self.rawHevcExtLine.setText(SETTINGS.rawHevcExt)

        if SETTINGS.cacheMethod == 0:
            self.cacheMethodComboBox.setCurrentIndex(0)
            if cache_path := SETTINGS.encodeCacheDir:
                _dir = QFileInfo(cache_path)
                if _dir.isDir() and (_dir.exists() or QDir().mkpath(cache_path)) and _dir.isWritable() and _dir.isReadable():
                    self.cacheLine.setText(cache_path)
                    ENCODE_CACHE_DIR.setPath(SETTINGS.encodeCacheDir)
                else:
                    ENCODE_CACHE_DIR.setPath('cache')
                    SETTINGS.encodeCacheDir = ENCODE_CACHE_DIR.absolutePath()
                    self.cacheLine.setText(ENCODE_CACHE_DIR.absolutePath())
            else:
                ENCODE_CACHE_DIR.setPath('cache')
                SETTINGS.encodeCacheDir = ENCODE_CACHE_DIR.absolutePath()
                QDir().mkpath(ENCODE_CACHE_DIR.absolutePath())
                self.cacheLine.setText(ENCODE_CACHE_DIR.absolutePath())
        else:
            self.cacheMethodComboBox.setCurrentIndex(1)

    def change_tab(self, index: int):
        if index == 3:
            self.set_size_label()

    def change_cache_method(self, index: int):
        if index == 1:
            self.cacheLine.setDisabled(True)
            self.cacheLabel.setDisabled(True)
            self.clearCacheButton.setDisabled(True)
            self.cacheSizeLabel.setDisabled(True)
        else:
            self.cacheLine.setEnabled(True)
            self.cacheLabel.setEnabled(True)
            self.clearCacheButton.setEnabled(True)
            self.cacheSizeLabel.setEnabled(True)
        self.enable_apply()

    def reload(self,
               *,
               check_x265=True,
               check_vspipe=True,
               check_avs4x26x=True,
               check_mkvmerge=True,
               check_mp4box=True,
               check_mediainfo=True,
               check_ffms2=True,
               check_lsmas=True,
               check_avisource=True,
               check_imwri=True,
               check_descale=True):
        if check_x265:
            self.x265Thread.begin()
        if check_vspipe:
            self.vspipeThread.begin()
        if check_avs4x26x:
            self.avs4x26xThread.begin()
        if check_mkvmerge:
            self.mkvmergeThread.begin()
        if check_mp4box:
            self.mp4boxThread.begin()
        if check_ffms2:
            self.check_ffms2()
        if check_lsmas:
            self.check_lsmas()
        if check_mediainfo:
            self.check_mediainfo()
        if check_avisource:
            self.check_avisource()
        if check_imwri:
            self.check_imwri()
        if check_descale:
            self.check_descale()

    def preload(self):
        if self.preloadCheckBox.isChecked():
            self.preloadTimeoutSpin.setEnabled(True)
        else:
            self.preloadTimeoutSpin.setDisabled(True)
        self.enable_apply()

    def enable_apply(self):
        self.applyButton.setEnabled(True)
        self.cancelButton.setEnabled(True)

    def check_program(self, result: tuple):
        obj_name, result, signal, path = result
        programs = {'x265': (self.check_x265, self.x265Thread),
                    'vspipe': (self.check_vspipe, self.vspipeThread),
                    'avs4x26x': (self.check_avs4x26x, self.avs4x26xThread),
                    'mkvmerge': (self.check_mkvmerge, self.mkvmergeThread),
                    'mp4box': (self.check_mp4box, self.mp4boxThread)}
        error = False
        func, process = programs[obj_name]
        if not func(result, signal, path) and not process.next():
            error = True
        if error:
            self.tab.setCurrentIndex(4)

    def check_x265(self, result: bytes, signal: int, path: str) -> bool:
        path = QFileInfo(path).absoluteFilePath()
        if result and self.x265Thread.correctResult in result and signal == self.x265Thread.correctSignal:
            X265.setFile(path)
            self.x265Line.setText(path)
            self.x265Line.setPlaceholderText('')
            if self.x265File:
                self.x265File.close()
            self.x265File = open(path, 'rb')
            return True
        else:
            X265.setFile('')
            self.x265Line.clear()
            if result is False:
                self.x265Line.setPlaceholderText(LANG_UI_TXT.info.permission)
            elif result is None:
                self.x265Line.setPlaceholderText(f'{path} {LANG_UI_TXT.info.not_exist}')
            else:
                self.x265Line.setPlaceholderText(LANG_UI_TXT.SettingWidget.disable)
            return False

    def check_vspipe(self, result: bytes, signal: int, path: str) -> bool:
        path = QFileInfo(path).absoluteFilePath()
        if result and self.vspipeThread.correctResult in result and signal == self.vspipeThread.correctSignal:
            VSPIPE.setFile(path)
            self.vspipeLine.setText(path)
            self.vspipeLine.setPlaceholderText('')
            if self.vspipeFile:
                self.vspipeFile.close()
            self.vspipeFile = open(path, 'rb')
            return True
        else:
            VSPIPE.setFile('')
            self.vspipeLine.clear()
            if result is False:
                self.vspipeLine.setPlaceholderText(LANG_UI_TXT.info.permission)
            elif result is None:
                self.vspipeLine.setPlaceholderText(f'{path} {LANG_UI_TXT.info.not_exist}')
            elif b'Failed to initialize VapourSynth environment' in result:
                self.vspipeLine.setPlaceholderText(LANG_UI_TXT.info.failed_to_initialize_VapourSynth_environment)
            else:
                self.vspipeLine.setPlaceholderText(LANG_UI_TXT.SettingWidget.disable)
            return False

    def check_avs4x26x(self, result: bytes, signal: int, path: str) -> bool:
        path = QFileInfo(path).absoluteFilePath()
        if result and self.avs4x26xThread.correctResult in result and signal == self.avs4x26xThread.correctSignal:
            AVS4X26X.setFile(path)
            self.avs4x26xLine.setText(path)
            self.avs4x26xLine.setPlaceholderText('')
            if self.avs4x26xFile:
                self.avs4x26xFile.close()
            self.avs4x26xFile = open(path, 'rb')
            return True
        else:
            AVS4X26X.setFile('')
            self.avs4x26xLine.clear()
            if result is False:
                self.avs4x26xLine.setPlaceholderText(LANG_UI_TXT.info.permission)
            elif result is None:
                self.avs4x26xLine.setPlaceholderText(f'{path} {LANG_UI_TXT.info.not_exist}')
            elif b'failed to load avisynth' in result:
                self.avs4x26xLine.setPlaceholderText(LANG_UI_TXT.info.failed_to_load_avisynth)
            else:
                self.avs4x26xLine.setPlaceholderText(LANG_UI_TXT.SettingWidget.disable)
            return False

    def check_mkvmerge(self, result: bytes, signal: int, path: str) -> bool:
        path = QFileInfo(path).absoluteFilePath()
        if result and self.mkvmergeThread.correctResult in result and signal == self.mkvmergeThread.correctSignal:
            MKVMERGE.setFile(path)
            self.mkvmergeLine.setText(path)
            self.mkvmergeLine.setPlaceholderText('')
            if self.mkvmergeFile:
                self.mkvmergeFile.close()
            self.mkvmergeFile = open(path, 'rb')
            return True
        else:
            MKVMERGE.setFile('')
            self.mkvmergeLine.clear()
            if result is False:
                self.avs4x26xLine.setPlaceholderText(LANG_UI_TXT.info.permission)
            elif result is None:
                self.avs4x26xLine.setPlaceholderText(f'{path} {LANG_UI_TXT.info.not_exist}')
            else:
                self.mkvmergeLine.setPlaceholderText(LANG_UI_TXT.SettingWidget.disable)
            return False

    def check_mp4box(self, result: bytes, signal: int, path: str) -> bool:
        path = QFileInfo(path).absoluteFilePath()
        if result and self.mp4boxThread.correctResult in result and signal == self.mp4boxThread.correctSignal:
            MP4BOX.setFile(path)
            self.mp4boxLine.setText(path)
            self.mp4boxLine.setPlaceholderText('')
            if self.mp4boxFile:
                self.mp4boxFile.close()
            self.mp4boxFile = open(path, 'rb')
            return True
        else:
            self.mp4boxLine.clear()
            MP4BOX.setFile('')
            if result is False:
                self.mp4boxLine.setPlaceholderText(LANG_UI_TXT.info.permission)
            elif result is None:
                self.mp4boxLine.setPlaceholderText(f'{path} {LANG_UI_TXT.info.not_exist}')
            else:
                self.mp4boxLine.setPlaceholderText(LANG_UI_TXT.SettingWidget.disable)
            return False

    def check_ffms2(self, ex_paths: list[QFileInfo] = None) -> bool:
        if FFMS2.check(ex_paths):
            self.ffms2Label.setText(LANG_UI_TXT.SettingWidget.enable)
            return True
        else:
            self.ffms2Label.setText(LANG_UI_TXT.SettingWidget.disable)
            return False

    def check_lsmas(self, ex_paths: list[QFileInfo] = None) -> bool:
        if LSMASH.check(ex_paths):
            self.lsmasLabel.setText(LANG_UI_TXT.SettingWidget.enable)
            return True
        else:
            self.lsmasLabel.setText(LANG_UI_TXT.SettingWidget.disable)
            return False

    def check_avisource(self, ex_paths: list[QFileInfo] = None) -> bool:
        if AVISOURCE.check(ex_paths):
            self.avisourceLabel.setText(LANG_UI_TXT.SettingWidget.enable)
            return True
        else:
            self.avisourceLabel.setText(LANG_UI_TXT.SettingWidget.disable)
            return False

    def check_imwri(self, ex_paths: list[QFileInfo] = None) -> bool:
        if IMWRI.check(ex_paths):
            self.imwriLabel.setText(LANG_UI_TXT.SettingWidget.enable)
            return True
        else:
            self.imwriLabel.setText(LANG_UI_TXT.SettingWidget.disable)
            return False

    def check_descale(self, ex_paths: list[QFileInfo] = None) -> bool:
        if DESCALE.check(ex_paths):
            self.mainWidget.toolsWidget.getnativeWidget.setEnabled(True)
            self.mainWidget.toolsWidget.getnativeWidget.init_scaler()
            self.descaleLabel.setText(LANG_UI_TXT.SettingWidget.enable)
            return True
        else:
            self.mainWidget.toolsWidget.getnativeWidget.setDisabled(True)
            self.descaleLabel.setText(LANG_UI_TXT.SettingWidget.disable)
            return False

    def check_mediainfo(self) -> bool:
        for file_info in MEDIAINFO_PATH:
            path = file_info.absoluteFilePath()
            if QFileInfo(path).exists():
                if pymediainfo.MediaInfo.can_parse(path):
                    MEDIAINFO.setFile(path)
                    self.mediaInfoLine.setText(path)
                    self.mediaInfoLine.setPlaceholderText('')
                    self.mainWidget.mediaInfoWidget.openButton.setEnabled(True)
                    return True
            else:
                MEDIAINFO.setFile('')
                self.mediaInfoLine.clear()
                self.mediaInfoLine.setPlaceholderText(f'{path} {LANG_UI_TXT.SettingWidget.disable}')
                self.mainWidget.mediaInfoWidget.openButton.setDisabled(True)
        else:
            return False

    def clear_cache(self):
        path = self.cacheLine.text()
        r = QMessageBox.question(self,
                                 LANG_UI_TXT.info.warning,
                                 f'{path}\n'
                                 f'{LANG_UI_TXT.info.cannot_be_recovered_after_clear}',
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                 QMessageBox.StandardButton.Yes)
        if r == QMessageBox.StandardButton.Yes:
            QDir(path).removeRecursively()
            QDir().mkpath(path)
            self.set_size_label()

    def get_dir_size(self, _dir: QDir) -> int:
        size = 0
        for file in _dir.entryInfoList(QDir.Filter.Files):
            size += file.size()
        for sub_dir in _dir.entryInfoList(filters=QDir.Filter.NoDotAndDotDot):
            size += self.get_dir_size(sub_dir)
        return size

    def set_size_label(self):
        if path := self.cacheLine.text():
            self.cacheSizeLabel.setText(get_size(self.get_dir_size(QDir(path))))
        else:
            self.cacheSizeLabel.clear()

    def insert_entry(self):
        sender = self.sender()
        if (previous_widget := self.focusWidget()) in (self.vpyStyleLine, self.avsStyleLine):
            previous_widget: CodeEditor
            if sender == self.baseNameButton:
                previous_widget.insertPlainText(BASENAME_CODE)
            elif sender == self.suffixButton:
                previous_widget.insertPlainText(SUFFIX_CODE)
            elif sender == self.fileNameButton:
                previous_widget.insertPlainText(FILENAME_CODE)
            elif sender == self.pathButton:
                previous_widget.insertPlainText(PATH_CODE)

    def apply(self):
        SETTINGS.autoLoadSav = 1 if self.autoLoadSavCheckBox.isChecked() else 0
        SETTINGS.loadVideoCmd = 1 if self.loadVideoCmdCheckBox.isChecked() else 0

        if self.svtCheckBox.isChecked():
            SETTINGS.svt = 1
            self.mainWidget.commandWidget.svtCheckBox.setEnabled(True)
        else:
            SETTINGS.svt = 0
            self.mainWidget.commandWidget.svtCheckBox.setChecked(False)
            self.mainWidget.commandWidget.svtCheckBox.setDisabled(True)
        SETTINGS.rememberRecentDir = 1 if self.rememberRecentDirCheckBox.isChecked() else 0
        SETTINGS.preload = 1 if self.preloadCheckBox.isChecked() else 0
        SETTINGS.preloadTimeout = self.preloadTimeoutSpin.value()
        SETTINGS.encodeTimeout = self.encodeTimeoutSpin.value()

        SETTINGS.parseSpeed = self.parseSpeedSpinBox.value()
        SETTINGS.avsTemplate = self.avsStyleLine.toPlainText()
        SETTINGS.vpyTemplate = self.vpyStyleLine.toPlainText()

        if self.cacheMethodComboBox.currentIndex() != SETTINGS.cacheMethod:
            self.restartLabel.setText(LANG_UI_TXT.SettingWidget.need_restart)
        else:
            self.restartLabel.clear()
        SETTINGS.conf.setValue(SETTINGS.key_section['cacheMethod'], self.cacheMethodComboBox.currentIndex())
        SETTINGS.rawHevcExt = self.rawHevcExtLine.text()
        self.mainWidget.encodeWidget.taskAppendWidget.outputVideoList.set_ext(ExtGroup(SETTINGS.rawHevcExt))
        self.mainWidget.encodeWidget.taskAppendWidget.taskEditor.outputLine.set_ext(ExtGroup(SETTINGS.rawHevcExt, 'mp4', 'mkv'))
        self.mainWidget.encodeWidget.taskOperationWidget.taskTableWidget.taskEditor.outputLine.set_ext(ExtGroup(SETTINGS.rawHevcExt, 'mp4', 'mkv'))
        self.mainWidget.encodeWidget.taskAppendWidget.change_output_type(
            self.mainWidget.encodeWidget.taskAppendWidget.outputTypeComboBox.currentText())

        if cache_path := self.cacheLine.text():
            _dir = QDir(cache_path)
            if (_dir.exists() or WORK_DIR.mkpath(cache_path)) and _dir.mkpath('.unwatched') and _dir.isReadable():
                SETTINGS.encodeCacheDir = cache_path
                ENCODE_CACHE_DIR.setPath(cache_path)
            else:
                ENCODE_CACHE_DIR.setPath('cache')
                SETTINGS.encodeCacheDir = ENCODE_CACHE_DIR.absolutePath()
                self.cacheLine.setText(ENCODE_CACHE_DIR.absolutePath())
        else:
            ENCODE_CACHE_DIR.setPath('cache')
            SETTINGS.encodeCacheDir = ENCODE_CACHE_DIR.absolutePath()
            QDir().mkpath(ENCODE_CACHE_DIR.absolutePath())
            self.cacheLine.setText(ENCODE_CACHE_DIR.absolutePath())

        if self.languageComboBox.currentText() != SETTINGS.language_codes.get(SETTINGS.language):
            for code, language in SETTINGS.language_codes.items():
                if language == self.languageComboBox.currentText():
                    self.mainWidget.set_ui_language(code)
                    break
            else:
                QMessageBox.warning(self,
                                    LANG_UI_TXT.info.error,
                                    f'{self.languageComboBox.currentText()}{LANG_UI_TXT.info.language_text_not_found}',
                                    QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok)

        if self.cmdLanguageComboBox.currentText() != SETTINGS.language_codes.get(SETTINGS.cmdLanguage):
            for code, language in SETTINGS.language_codes.items():
                if language == self.cmdLanguageComboBox.currentText():
                    self.mainWidget.set_cmd_language(code)
                    break
            else:
                QMessageBox.warning(self,
                                    LANG_UI_TXT.info.error,
                                    f'{self.cmdLanguageComboBox.currentText()}{LANG_UI_TXT.info.language_text_not_found}',
                                    QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok)
        if (font_family := self.fontComboBox.currentText()) != SETTINGS.fontFamily:
            font = QFont(font_family)
            font.setPixelSize(FONT_SIZE)
            self.mainWidget.set_font(font)
            SETTINGS.fontFamily = font_family

        self.set_size_label()

        self.applyButton.setDisabled(True)
        self.cancelButton.setDisabled(True)

    def cancel(self):
        self.cacheLine.setText(SETTINGS.encodeCacheDir)
        self.avsStyleLine.setPlainText(SETTINGS.avsTemplate)
        self.vpyStyleLine.setPlainText(SETTINGS.vpyTemplate)
        self.cmdLanguageComboBox.setCurrentText(SETTINGS.language_codes.get(SETTINGS.cmdLanguage))
        self.languageComboBox.setCurrentText(SETTINGS.language_codes.get(SETTINGS.language))
        self.fontComboBox.setCurrentText(SETTINGS.fontFamily)
        self.applyButton.setDisabled(True)
        self.cancelButton.setDisabled(True)
        self.autoLoadSavCheckBox.setChecked(True if SETTINGS.autoLoadSav == 1 else False)
        self.loadVideoCmdCheckBox.setChecked(True if SETTINGS.loadVideoCmd == 1 else False)
        self.svtCheckBox.setChecked(True if SETTINGS.svt == 1 else False)
        self.rememberRecentDirCheckBox.setChecked(True if SETTINGS.rememberRecentDir == 1 else False)
        self.cacheMethodComboBox.setCurrentIndex(SETTINGS.cacheMethod)
        self.rawHevcExtLine.setText(SETTINGS.rawHevcExt)
