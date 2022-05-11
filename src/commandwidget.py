import json
from nt import cpu_count
from PySide6.QtCore import QRegularExpression
from PySide6.QtWidgets import QTabWidget, QCheckBox, QSpinBox, QSlider, QDoubleSpinBox, QTabBar, \
    QMenu, QMenuBar
from PySide6.QtGui import QRegularExpressionValidator

import pymediainfo
from MyWidgets import *
from data import *


class CommandWidget(QWidget):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        from x265 import MainWidget
        self.mainWidget: MainWidget = parent
        self.__commands = COMMANDS
        self.profiles = (
            '',                    # 0
            'main',                # 1
            'main-intra',          # 2
            'mainstillpicture',    # 3
            'main444-8',           # 4
            'main444-intra',       # 5
            'main444-stillpicture',# 6
            'main10',              # 7
            'main10-intra',        # 8
            'main422-10',          # 9
            'main422-10-intra',    # 10
            'main444-10',          # 11
            'main444-10-intra',    # 12
            'main12',              # 13
            'main12-intra',        # 14
            'main422-12',          # 15
            'main422-12-intra',    # 16
            'main444-12',          # 17
            'main444-12-intra')    # 18
        self.tunes = (
            'psnr',
            'ssim',
            'grain',
            'zero-latency',
            'fast-decode',
            'animation')
        self.ctu = (1, 1, 0, 0, 0, 0, 0, 0, 0, 0) # 0:64, 1: 32, 2: 16
        self.min_cu_size = (1, 2, 2, 2, 2, 2, 2, 2, 2, 2) # 0:32, 1: 16, 2: 8
        self.bframes = (3, 3, 4, 4, 4, 4, 4, 8, 8, 8)
        self.b_adapt = (0, 0, 0, 0, 0, 2, 2, 2, 2, 2)
        self.rc_lookahead = (5, 10, 15, 15, 15, 20, 25, 40, 40, 60)
        self.lookahead_slices = (8, 8, 8, 8, 8, 8, 4, 1, 1, 1)
        self.scenecut = (0, 40, 40, 40, 40, 40, 40, 40, 40, 40)
        self.ref = (1, 1, 2, 2, 3, 3, 4, 5, 5, 5)
        self.limit_refs = (0, 0, 3, 3, 3, 3, 3, 1, 0, 0)
        self.me = (0, 1, 1, 1, 1, 1, 3, 3, 3, 3)
        self.merange = (57, 57, 57, 57, 57, 57, 57, 57, 57, 92)
        self.subme = (0, 1, 1, 2, 2, 2, 3, 4, 4, 5)
        self.rect = (
            False,
            False,
            False,
            False,
            False,
            False,
            True,
            True,
            True,
            True)
        self.amp = (
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            True,
            True,
            True)
        self.limit_modes = (
            False,
            False,
            False,
            False,
            False,
            False,
            True,
            True,
            False,
            False)
        self.max_merge = (2, 2, 2, 2, 2, 2, 3, 4, 5, 5)
        self.early_skip = (
            True,
            True,
            True,
            True,
            False,
            True,
            False,
            False,
            False,
            False)
        self.rskip = (1, 1, 1, 1, 1, 1, 1, 1, 1, 0)
        self.fast_intra = (
            True,
            True,
            True,
            True,
            True,
            False,
            False,
            False,
            False,
            False)
        self.b_intra = (
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            True,
            True,
            True)
        self.sao = (
            False,
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True)
        self.signhide = (
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True)
        self.weightp = (
            False,
            False,
            True,
            True,
            True,
            True,
            True,
            True,
            True,
            True)
        self.weightb = (
            False,
            False,
            False,
            False,
            False,
            False,
            False,
            True,
            True,
            True)
        self.aq_mode = (0, 0, 2, 2, 2, 2, 2, 2, 2, 2)
        self.rdLevel = (2, 2, 2, 2, 2, 3, 4, 6, 6, 6)
        self.rdoq_level = (0, 0, 0, 0, 0, 0, 2, 2, 2, 2)
        self.tu_intra = (1, 1, 1, 1, 1, 1, 1, 3, 3, 4)
        self.tu_inter = (1, 1, 1, 1, 1, 1, 1, 3, 3, 4)
        self.limit_tu = (0, 0, 0, 0, 0, 0, 0, 4, 0, 0)
        self.__presets = (
            'ultrafast',
            'superfast',
            'veryfast',
            'faster',
            'fast',
            'medium',
            'slow',
            'slower',
            'veryslow',
            'placebo')

        self.winTitleChange = ''
        self.winTitleFile = ''

        self.currentDefault = DEFAULT.copy()

        self.openButton = PathPushButton(QFileDialog.getOpenFileName,
                                         ExtGroup('json'),
                                         True,
                                         self)
        self.saveButton = PathPushButton(QFileDialog.getSaveFileName, ExtGroup('json'), False, self)
        self.saveAsButton = PathPushButton(QFileDialog.getSaveFileName, ExtGroup('json'), True, self)
        self.closeButton = QPushButton(self)
        self.saveSuccess = True
        self.searchComboBox = QComboBox()
        self.tab = QTabWidget(self)
        self.commandPlainTextEdit = QPlainTextEdit(self)
        self.copyButton = QToolButton(self)
        self.resetButton = QToolButton(self)
        self.exportButton = QToolButton(self)

        self.titleLine = QLineEdit(self)
        self.versionLabel = QLabel(self)

        self.profileWidget = QWidget(self)
        self.qualityWidget = QWidget(self)
        self.analysisWidget = QWidget(self)
        self.frameWidget = QWidget(self)
        self.quantizationWidget = QWidget(self)
        self.yuiWidget = QWidget(self)
        self.bitStreamWidget = QWidget(self)
        self.exportWidget = BatchExportWidget(self)

        self.logLevelComboBox = CommandComboBox(self)
        self.progressCheckBox = QCheckBox('progress', self)
        self.csvLine = PathLineEdit(QFileDialog.getSaveFileName, ExtGroup('log'), self)
        self.csvLogLevelComboBox = CommandComboBox(self)
        self.inputDepthComboBox = CommandComboBox(self)
        self.ditherCheckBox = QCheckBox('dither', self)
        self.inputResWidthSpin = QSpinBox(self)
        self.inputResHeightSpin = QSpinBox(self)
        self.cspComboBox = CommandComboBox(self)
        self.fpsComboBox = CommandComboBox(self)
        self.interlaceComboBox = CommandComboBox(self)
        self.frameDupCheckBox = QCheckBox('frame-dup', self)
        self.dupThresholdSpin = QSpinBox(self)
        self.seekSpin = QSpinBox(self)
        self.framesSpin = QSpinBox(self)
        self.chunkStartSpin = QSpinBox(self)
        self.chunkEndSpin = QSpinBox(self)
        self.fieldCheckBox = QCheckBox('field', self)
        self.ssimCheckBox = QCheckBox('ssim', self)
        self.psnrCheckBox = QCheckBox('psnr', self)
        self.presetLabel = QLabel('medium', self)
        self.presetSlider = QSlider(self)
        self.tuneComboBox = CommandComboBox(self)
        self.profileComboBox = CommandComboBox(self)
        self.levelComboBox = CommandComboBox(self)
        self.highTierCheckBox = QCheckBox('high-tier', self)
        self.refSpin = QSpinBox(self)
        self.allowNonConformanceCheckBox = QCheckBox('allow-non-conformance', self)
        self.uhdBDCheckBox = QCheckBox('uhd-bd', self)
        self.outputDepthComboBox = CommandComboBox(self)
        self.encodeModeComboBox = CommandComboBox(self)
        self.bitrateSpin = QSpinBox(self)
        self.crfSpin = QDoubleSpinBox(self)
        self.crfMaxSpin = QDoubleSpinBox(self)
        self.crfMinSpin = QDoubleSpinBox(self)
        self.vbvBufsizeSpin = QSpinBox(self)
        self.vbvMaxrateSpin = QSpinBox(self)
        self.vbvInitSpin = QDoubleSpinBox(self)
        self.vbvEndSpin = QDoubleSpinBox(self)
        self.vbvEndFrAdjSpin = QDoubleSpinBox(self)
        self.minVbvFullnessSpin = QDoubleSpinBox(self)
        self.maxVbvFullnessSpin = QDoubleSpinBox(self)
        self.constVbvCheckBox = QCheckBox('const-vbv', self)
        self.qpSpin = QSpinBox(self)
        self.qpstepSpin = QSpinBox(self)
        self.qpminSpin = QSpinBox(self)
        self.qpmaxSpin = QSpinBox(self)
        self.passSpin = QSpinBox(self)
        self.statsLine = PathLineEdit(QFileDialog.getOpenFileName, ExtGroup('log'), self)
        self.slowFirstpassCheckBox = QCheckBox('slow-firstpass', self)
        self.multiPassOptAnalysisCheckBox = QCheckBox('multi-pass-opt-analysis', self)
        self.multiPassOptDistortionCheckBox = QCheckBox('multi-pass-opt-distortion', self)
        self.strictCbrCheckBox = QCheckBox('strict-cbr', self)
        self.rcGrainCheckBox = QCheckBox('rc-grain', self)
        self.rdSpin = QSpinBox(self)
        self.ctuComboBox = CommandComboBox(self)
        self.minCUComboBox = CommandComboBox(self)
        self.limitRefsSpin = QSpinBox(self)
        self.limitModesCheckBox = QCheckBox('limit-modes', self)
        self.rectCheckBox = QCheckBox('rect', self)
        self.ampCheckBox = QCheckBox('amp', self)
        self.earlySkipCheckBox = QCheckBox('early-skip', self)
        self.rskipSpinBox = QSpinBox(self)
        self.rskipEdgeThresholdSpinBox = QSpinBox(self)
        self.splitrdSkipCheckBox = QCheckBox('splitrd-skip', self)
        self.fastIntraCheckBox = QCheckBox('fast-intra', self)
        self.bIntraCheckBox = QCheckBox('b-intra', self)
        self.cuLosslessCheckBox = QCheckBox('cu-lossless', self)
        self.tskipFastCheckBox = QCheckBox('tskip-fast', self)
        self.rdRefineCheckBox = QCheckBox('rd-refine', self)
        self.analysisSaveLine = PathLineEdit(QFileDialog.getSaveFileName, ExtGroup('dat'), self)
        self.analysisLoadLine = PathLineEdit(QFileDialog.getOpenFileName, ExtGroup('dat'), self)
        self.analysisReuseFileLine = PathLineEdit(QFileDialog.getOpenFileName, ExtGroup('dat'), self)
        self.analysisSaveReuseLevelSpin = QSpinBox(self)
        self.analysisLoadReuseLevelSpin = QSpinBox(self)
        self.refineMvTypeLine = CommandLineEdit(self)
        self.refineCtuDistortionSpin = QSpinBox(self)
        self.scaleFactorSpin = QSpinBox(self)
        self.refineIntraSpin = QSpinBox(self)
        self.refineInterSpin = QSpinBox(self)
        self.dynamicRefineCheckBox = QCheckBox('dynamic-refine', self)
        self.refineMVCheckBox = QCheckBox('refine-mv', self)
        self.rdoqLevelSpin = QSpinBox(self)
        self.tuIntraDepthSpin = QSpinBox(self)
        self.tuInterDepthSpin = QSpinBox(self)
        self.limitTuSpin = QSpinBox(self)
        self.nrIntraSpin = QSpinBox(self)
        self.nrInterSpin = QSpinBox(self)
        self.tskipCheckBox = QCheckBox('tskip', self)
        self.rdpenaltySpin = QSpinBox(self)
        self.maxTUComboBox = CommandComboBox(self)
        self.dynamicRdSpin = QSpinBox(self)
        self.ssimRdCheckBox = QCheckBox('ssim-rd', self)
        self.psyRdSpin = QDoubleSpinBox(self)
        self.psyRdoqSpin = QDoubleSpinBox(self)
        self.maxMergeSpin = QSpinBox(self)
        self.meComboBox = CommandComboBox(self)
        self.submeSpin = QSpinBox(self)
        self.merangeSpin = QSpinBox(self)
        self.temporalMvpCheckBox = QCheckBox('temporal-mvp', self)
        self.weightpCheckBox = QCheckBox('weightp', self)
        self.weightbCheckBox = QCheckBox('weightb', self)
        self.analyzeSrcPicsCheckBox = QCheckBox('analyze-src-pics', self)
        self.hmeCheckBox = QCheckBox('hme', self)
        self.hmeSearch1 = QSpinBox(self)
        self.hmeSearch2 = QSpinBox(self)
        self.hmeSearch3 = QSpinBox(self)
        self.hmeRange1 = QSpinBox(self)
        self.hmeRange2 = QSpinBox(self)
        self.hmeRange3 = QSpinBox(self)
        self.strongIntraSmoothingCheckBox = QCheckBox('strong-intra-smoothing', self)
        self.constrainedIntraCheckBox = QCheckBox('constrained-intra', self)
        self.openGopCheckBox = QCheckBox('open-gop', self)
        self.keyintSpin = QSpinBox(self)
        self.minKeyintSpin = QSpinBox(self)
        self.scenecutSpin = QSpinBox(self)
        self.scenecutBiasSpin = QDoubleSpinBox(self)
        self.histScenecutCheckBox = QCheckBox('hist-scenecut', self)
        self.histThresholdSpin = QDoubleSpinBox(self)
        self.radlSpin = QSpinBox(self)
        self.ctuInfoComboBox = CommandComboBox(self)
        self.intraRefreshCheckBox = QCheckBox('intra-refresh', self)
        self.rcLookaheadSpin = QSpinBox(self)
        self.gopLookaheadSpin = QSpinBox(self)
        self.lookaheadSlicesSpin = QSpinBox(self)
        self.lookaheadthreadsSpin = QSpinBox(self)
        self.bAdaptSpin = QSpinBox(self)
        self.bframesSpin = QSpinBox(self)
        self.bframeBiasSpin = QSpinBox(self)
        self.bPyramidCheckBox = QCheckBox('b-pyramid', self)
        self.forceFlushSpin = QSpinBox(self)
        self.fadesCheckBox = QCheckBox('fades', self)
        self.asmComboBox = CommandComboBox(self)
        self.frameThreadsSpin = QSpinBox(self)
        self.poolsLine = CommandLineEdit(self)
        self.wppCheckBox = QCheckBox('wpp', self)
        self.pmodeCheckBox = QCheckBox('pmode', self)
        self.pmeCheckBox = QCheckBox('pme', self)
        self.slicesSpin = QSpinBox(self)
        self.copyPictureCheckBox = QCheckBox('copy-pic', self)
        self.aqModeSpin = QSpinBox(self)
        self.aqStrengthSpin = QDoubleSpinBox(self)

        self.hevcAqCheckBox = QCheckBox('hevc-aq', self)
        self.aqMotionCheckBox = QCheckBox('aq-motion', self)
        self.qgSizeComboBox = CommandComboBox(self)
        self.cutreeCheckBox = QCheckBox('cutree', self)
        self.cbqpoffsSpin = QSpinBox(self)
        self.crqpoffsSpin = QSpinBox(self)
        self.ipratioSpin = QDoubleSpinBox(self)
        self.pbratioSpin = QDoubleSpinBox(self)
        self.qcompSpin = QDoubleSpinBox(self)
        self.qblurSpin = QDoubleSpinBox(self)
        self.cplxblurSpin = QDoubleSpinBox(self)
        self.zonesLine = CommandLineEdit(self)
        self.zonefileLine = PathLineEdit(QFileDialog.getOpenFileName, ExtGroup('txt'), self)
        self.scenecutAwareQpSpin = QSpinBox(self)
        self.maskingStrengthLine = CommandLineEdit(self)
        self.vbvLiveMultiPassCheckBox = QCheckBox('vbv-live-multi-pass', self)
        self.signhideCheckBox = QCheckBox('signhide', self)
        self.qpfileLine = PathLineEdit(QFileDialog.getOpenFileName, ExtGroup('txt'), self)
        self.scalingListLine = PathLineEdit(QFileDialog.getOpenFileName, ExtGroup('txt'), self)
        self.lambdaFileLine = PathLineEdit(QFileDialog.getOpenFileName, ExtGroup('txt'), self)
        self.maxAusizeFactorSpin = QDoubleSpinBox(self)
        self.deblockCheckBox = QCheckBox('deblock', self)
        self.deblockSpin1 = QSpinBox(self)
        self.deblockSpin2 = QSpinBox(self)
        self.saoCheckBox = QCheckBox('sao', self)
        self.saoNoneDeblockCheckBox = QCheckBox('sao-non-deblock', self)
        self.limitSaoCheckBox = QCheckBox('limit-sao', self)
        self.selectiveSaoSpin = QSpinBox(self)
        self.sarComboBox = CommandComboBox(self)
        self.displayWindowSpinL = QSpinBox(self)
        self.displayWindowSpinT = QSpinBox(self)
        self.displayWindowSpinR = QSpinBox(self)
        self.displayWindowSpinB = QSpinBox(self)
        self.overscanComboBox = CommandComboBox(self)
        self.videoformatComboBox = CommandComboBox(self)
        self.rangeComboBox = CommandComboBox(self)
        self.colorprimComboBox = CommandComboBox(self)
        self.transferComboBox = CommandComboBox(self)
        self.colormatrixComboBox = CommandComboBox(self)
        self.chromalocSpin = QSpinBox(self)
        self.masterDisplayLine = CommandLineEdit(self)
        self.maxCllLine = CommandLineEdit(self)
        self.cllCheckBox = QCheckBox('cll', self)
        self.hdr10CheckBox = QCheckBox('hdr10', self)
        self.hdr10OptCheckBox = QCheckBox('hdr10-opt', self)
        self.dhdr10InfoLine = PathLineEdit(QFileDialog.getOpenFileName, ExtGroup('json'), self)
        self.dhdr10OptCheckBox = QCheckBox('dhdr10-opt', self)
        self.minLumaSpin = QSpinBox(self)
        self.maxLumaSpin = QSpinBox(self)
        self.naluFileLine = PathLineEdit(QFileDialog.getOpenFileName, ExtGroup('txt'), self)
        self.atcSeiSpin = QSpinBox(self)
        self.picStructSpin = QSpinBox(self)
        self.annexbCheckBox = QCheckBox('annexb', self)
        self.repeatHeadersCheckBox = QCheckBox('repeat-headers', self)
        self.audCheckBox = QCheckBox('aud', self)
        self.hrdCheckBox = QCheckBox('hrd', self)
        self.hrdConcatCheckBox = QCheckBox('hrd-concat', self)
        self.dolbyVisionProfileComboBox = CommandComboBox(self)
        self.dolbyVisionRpuLine = CommandLineEdit(self)
        self.infoCheckBox = QCheckBox('info', self)
        self.hashComboBox = CommandComboBox(self)
        self.temporalLayersCheckBox = QCheckBox('temporal-layers', self)
        self.log2MaxPocLsbSpin = QSpinBox(self)
        self.vuiTimingInfoCheckBox = QCheckBox('vui-timing-info', self)
        self.vuiHrdInfoCheckBox = QCheckBox('vui-hrd-info', self)
        self.optQpPpsCheckBox = QCheckBox('opt-qp-pps', self)
        self.optRefListLengthPpsCheckBox = QCheckBox('opt-ref-list-length-pps', self)
        self.multiPassOptRpsCheckBox = QCheckBox('multi-pass-opt-rps', self)
        self.optCuDeltaQpCheckBox = QCheckBox('opt-cu-delta-qp', self)
        self.idrRecoverySeiCheckBox = QCheckBox('idr-recovery-sei', self)
        self.singleSeiCheckBox = QCheckBox('single-sei', self)
        self.customLine = QPlainTextEdit(self)
        self.lowpassDctCheckBox = QCheckBox('lowpass-dct', self)
        self.reconLine = PathLineEdit(QFileDialog.getSaveFileName, ExtGroup('yuv', 'y4m'), self)
        self.reconDepthSpin = QSpinBox(self)
        self.reconY4mExecLine = CommandLineEdit(self)
        self.svtCheckBox = QCheckBox('svt', self)
        self.svtHmeCheckBox = QCheckBox('svt-hme', self)
        self.svtSearchWidthSpin = QSpinBox(self)
        self.svtSearchHeightSpin = QSpinBox(self)
        self.svtCompressedTenBitFormatCheckBox = QCheckBox('svt-compressed-ten-bit-format', self)
        self.svtSpeedControlCheckBox = QCheckBox('svt-speed-control', self)
        self.svtPresetTunerSpin = QSpinBox(self)
        self.svtHierarchicalLevelSpin = QSpinBox(self)
        self.svtBaseLayerSwitchModeSpin = QSpinBox(self)
        self.svtPredStructSpin = QSpinBox(self)
        self.svtFpsInVpsCheckBox = QCheckBox('svt-fps-in-vps', self)

        self.buttons = (
            self.openButton,
            self.saveButton,
            self.saveAsButton,
            self.closeButton)

        self.widgets = (
            self.profileWidget,
            self.qualityWidget,
            self.analysisWidget,
            self.frameWidget,
            self.quantizationWidget,
            self.yuiWidget,
            self.bitStreamWidget)
        self.groupBoxes = [ColorFormLayout(self) for _ in range(50)]

        self.doubleSpins: tuple[QDoubleSpinBox] = tuple(self.findChildren(QDoubleSpinBox, options=Qt.FindChildOption.FindDirectChildrenOnly))
        self.spins: tuple[QSpinBox] = tuple(self.findChildren(QSpinBox, options=Qt.FindChildOption.FindDirectChildrenOnly))
        self.comboBoxes: tuple[CommandComboBox] = tuple(self.findChildren(CommandComboBox, options=Qt.FindChildOption.FindDirectChildrenOnly))
        self.checkBoxes: tuple[QCheckBox] = tuple(self.findChildren(QCheckBox, options=Qt.FindChildOption.FindDirectChildrenOnly))
        self.toolButtons = (
            self.copyButton,
            self.resetButton,
            self.exportButton)
        self.commandLines: tuple[CommandLineEdit] = tuple(self.findChildren(CommandLineEdit, options=Qt.FindChildOption.FindDirectChildrenOnly))
        self.pathLines: tuple[PathLineEdit] = tuple(self.findChildren(PathLineEdit, options=Qt.FindChildOption.FindDirectChildrenOnly))

        self.init_profile()
        self.init_quality()
        self.init_analysis()
        self.init_frame()
        self.init_quantization()
        self.init_vui()
        self.init_bitstream()

        self.allItems = {item.objectName(): item for item in self.doubleSpins + self.spins + self.comboBoxes +
                         self.commandLines + self.checkBoxes + self.pathLines +
                         (self.customLine, self.presetSlider)}

        self.profileWidgetLabels = []
        for i in self.findChildren(QLabel):
            if i.text():
                self.profileWidgetLabels.append(i)
        self.profileWidgetLabels.remove(self.presetLabel)
        self.init_ui()

    def init_profile(self):
        home = QHBoxLayout()
        self.profileWidget.setLayout(home)

        form1 = self.groupBoxes[0]
        form2 = self.groupBoxes[1]
        form3 = self.groupBoxes[2]
        form4 = self.groupBoxes[3]
        form5 = self.groupBoxes[4]
        form6 = self.groupBoxes[5]
        form7 = self.groupBoxes[6]
        form8 = self.groupBoxes[7]

        box1 = QVBoxLayout()
        box2 = QVBoxLayout()
        box3 = QVBoxLayout()

        home.addLayout(box1)
        home.setStretch(0, 1)
        home.addLayout(box2)
        home.setStretch(1, 1)
        home.addLayout(box3)
        home.setStretch(2, 1)
        box1.addWidget(form1)
        box1.addWidget(form2)
        box1.addWidget(form3)
        box1.addStretch(1)
        box2.addWidget(form4)
        box2.addWidget(form5)
        box2.addWidget(form6)
        box2.addWidget(form7)
        box2.addStretch(1)
        box3.addWidget(form8)
        box3.addStretch(1)

        self.inputDepthComboBox.setObjectName('input-depth')
        self.inputDepthComboBox.addItem('')
        self.inputDepthComboBox.addItems([str(i) for i in range(8, 17)])

        self.ditherCheckBox.setObjectName('dither')

        self.inputResWidthSpin.setObjectName('width')
        self.inputResHeightSpin.setObjectName('height')
        for i in (self.inputResWidthSpin, self.inputResHeightSpin):
            i.setRange(0, 8192)
            i.setSingleStep(100)

        self.cspComboBox.setObjectName('input-csp')
        self.cspComboBox.addItems(('i400', 'i420', 'i422', 'i444', 'NV12', 'nv16'))

        self.fpsComboBox.setObjectName('fps')
        self.fpsComboBox.addItems(
            ('24000/1001',
             '24',
             '25',
             '30000/1001',
             '30',
             '50',
             '60000/1001',
             '60'))
        self.fpsComboBox.setEditable(True)
        self.fpsComboBox.editTextChanged.connect(self.command_change)
        self.fpsComboBox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.fpsComboBox.setValidator(QRegularExpressionValidator(QRegularExpression(r'[0-9]+[/\.][0-9]+')))
        self.fpsComboBox.lineEdit().setClearButtonEnabled(True)

        self.interlaceComboBox.setObjectName('interlace')
        self.interlaceComboBox.addItems(('',) * 3)

        self.frameDupCheckBox.setObjectName('frame-dup')

        self.dupThresholdSpin.setObjectName('dup-threshold')
        self.dupThresholdSpin.setRange(1, 99)

        self.seekSpin.setObjectName('seek')
        self.seekSpin.setRange(0, 999999)

        self.framesSpin.setObjectName('frames')
        self.framesSpin.setRange(0, 9999999)
        self.framesSpin.setSingleStep(100)

        self.chunkStartSpin.setObjectName('chunk-start')
        self.chunkStartSpin.setRange(0, 999999)

        self.chunkEndSpin.setObjectName('chunk-end')
        self.chunkEndSpin.setRange(0, 999999)

        self.fieldCheckBox.setObjectName('field')

        self.presetLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.presetSlider.setObjectName('preset')
        self.presetSlider.setRange(0, 9)
        self.presetSlider.setOrientation(Qt.Orientation.Horizontal)
        self.presetSlider.setTickPosition(QSlider.TickPosition.TicksAbove)
        self.presetSlider.valueChanged.connect(self.preset)

        self.tuneComboBox.setObjectName('tune')
        self.tuneComboBox.addItems(('',) + self.tunes)

        self.profileComboBox.setObjectName('profile')
        self.profileComboBox.addItems(self.profiles)

        self.profileComboBox.view().setMinimumHeight(120)

        self.levelComboBox.setObjectName('level-idc')
        self.levelComboBox.addItems(
            ('',
             '1.0',
             '2.0',
             '2.1',
             '3.0',
             '3.1',
             '4.0',
             '4.1',
             '5.0',
             '5.1',
             '5.2',
             '6.0',
             '6.1',
             '6.2',
             '8.5'))

        self.highTierCheckBox.setObjectName('high-tier')

        self.refSpin.setObjectName('ref')
        self.refSpin.setRange(1, 16)

        self.allowNonConformanceCheckBox.setObjectName('allow-non-conformance')

        self.uhdBDCheckBox.setObjectName('uhd-bd')

        self.outputDepthComboBox.setObjectName('output-depth')
        self.outputDepthComboBox.addItems(('', '8', '10', '12'))

        self.encodeModeComboBox.setObjectName('encoding mode')
        self.encodeModeComboBox.addItems(('CRF', 'ABR', 'CQP', 'lossless'))

        self.bitrateSpin.setObjectName('bitrate')
        self.bitrateSpin.setSingleStep(100)
        self.bitrateSpin.setRange(1, 99999999)

        self.crfSpin.setObjectName('crf')
        self.crfSpin.setDecimals(1)
        self.crfSpin.setSingleStep(0.1)
        self.crfSpin.setRange(0, 51)

        self.qpSpin.setObjectName('qp')
        self.qpSpin.setRange(0, 51)

        self.passSpin.setObjectName('pass')
        self.passSpin.setRange(0, 3)

        self.ssimCheckBox.setObjectName('ssim')

        self.psnrCheckBox.setObjectName('psnr')

        form1.form.addRow(self.presetLabel)
        form1.form.addRow(self.presetSlider)
        form1.form.addRow('tune', self.tuneComboBox)

        form2.form.addRow(' ', self.encodeModeComboBox)
        form2.form.addRow(' ', self.bitrateSpin)
        form2.form.addRow('pass', self.passSpin)
        form2.form.addRow('CRF', self.crfSpin)
        form2.form.addRow('QP', self.qpSpin)
        form2.form.addRow(self.strictCbrCheckBox)

        form3.form.addRow(self.ssimCheckBox)
        form3.form.addRow(self.psnrCheckBox)

        form4.form.addRow(' ', self.outputDepthComboBox)
        form4.form.addRow('profile', self.profileComboBox)
        form4.form.addRow('level', self.levelComboBox)
        form4.form.addRow(self.highTierCheckBox)

        form5.form.addRow('ref', self.refSpin)
        form5.form.addRow('limit-refs', self.limitRefsSpin)

        form6.form.addRow(self.allowNonConformanceCheckBox)

        form7.form.addRow(self.uhdBDCheckBox)

        form8.form.addRow(' ', self.inputDepthComboBox)
        form8.form.addRow(' ', self.inputResWidthSpin)
        form8.form.addRow(' ', self.inputResHeightSpin)
        form8.form.addRow(' ', self.cspComboBox)
        form8.form.addRow(' ', self.fpsComboBox)
        form8.form.addRow(' ', self.interlaceComboBox)
        form8.form.addRow(' ', self.seekSpin)
        form8.form.addRow(self.frameDupCheckBox)
        form8.form.addRow(' ', self.dupThresholdSpin)
        form8.form.addRow(' ', self.framesSpin)
        form8.form.addRow(self.ditherCheckBox)
        form8.form.addRow('chunk-start', self.chunkStartSpin)
        form8.form.addRow('chunk-end', self.chunkEndSpin)
        form8.form.addRow(self.fieldCheckBox)

    def init_quality(self):
        home = QHBoxLayout(self.qualityWidget)

        form1 = self.groupBoxes[8]
        form2 = self.groupBoxes[9]
        form3 = self.groupBoxes[10]
        form4 = self.groupBoxes[11]
        form5 = self.groupBoxes[12]
        form6 = self.groupBoxes[13]

        box1 = QVBoxLayout()
        box2 = QVBoxLayout()
        box3 = QVBoxLayout()

        home.addLayout(box1)
        home.addLayout(box2)
        home.addLayout(box3)
        home.setStretch(0, 1)
        home.setStretch(1, 1)
        home.setStretch(2, 1)
        box1.addWidget(form1)
        box1.addWidget(form2)
        box1.addStretch(1)
        box2.addWidget(form3)
        box2.addWidget(form4)
        box2.addStretch(1)
        box3.addWidget(form5)
        box3.addWidget(form6)
        box3.addStretch(1)

        self.asmComboBox.setObjectName('asm')
        self.asmComboBox.addItems(
            ('',
             'MMX2',
             'SSE',
             'SSE2',
             'SSE3',
             'SSSE3',
             'SSE4',
             'SSE4.1',
             'SSE4.2',
             'AVX',
             'XOP',
             'FMA4',
             'AVX2',
             'FMA3',
             ''))

        self.frameThreadsSpin.setObjectName('frame-threads')
        self.frameThreadsSpin.setRange(0, 16)

        self.poolsLine.setObjectName('pools')

        self.wppCheckBox.setObjectName('wpp')

        self.pmodeCheckBox.setObjectName('pmode')

        self.pmeCheckBox.setObjectName('pme')

        self.crfMaxSpin.setObjectName('crf-max')
        self.crfMaxSpin.setDecimals(1)
        self.crfMaxSpin.setSingleStep(0.1)
        self.crfMaxSpin.setRange(-0.1, 51.0)

        self.crfMinSpin.setObjectName('crf-min')
        self.crfMinSpin.setDecimals(1)
        self.crfMinSpin.setSingleStep(0.1)
        self.crfMinSpin.setRange(-0.1, 51.0)

        self.vbvBufsizeSpin.setObjectName('vbv-bufsize')
        self.vbvBufsizeSpin.setSingleStep(100)
        self.vbvBufsizeSpin.setRange(0, 999999999)

        self.vbvMaxrateSpin.setObjectName('vbv-maxrate')
        self.vbvMaxrateSpin.setSingleStep(100)
        self.vbvMaxrateSpin.setRange(0, 999999999)

        self.vbvInitSpin.setObjectName('vbv-init')
        self.vbvInitSpin.setDecimals(1)
        self.vbvInitSpin.setSingleStep(0.1)
        self.vbvInitSpin.setRange(0, 1)

        self.vbvEndSpin.setObjectName('vbv-end')
        self.vbvEndSpin.setDecimals(1)
        self.vbvEndSpin.setSingleStep(0.1)
        self.vbvEndSpin.setRange(0, 1)

        self.vbvEndFrAdjSpin.setObjectName('vbv-end-fr-adj')
        self.vbvEndFrAdjSpin.setDecimals(1)
        self.vbvEndFrAdjSpin.setSingleStep(0.1)
        self.vbvEndFrAdjSpin.setRange(0, 9999999)

        self.minVbvFullnessSpin.setObjectName('min-vbv-fullness')
        self.minVbvFullnessSpin.setDecimals(2)
        self.minVbvFullnessSpin.setRange(0, 100)

        self.maxVbvFullnessSpin.setObjectName('max-vbv-fullness')
        self.maxVbvFullnessSpin.setDecimals(2)
        self.maxVbvFullnessSpin.setRange(0, 100)

        self.constVbvCheckBox.setObjectName('const-vbv')

        self.qpstepSpin.setObjectName('qpstep')
        self.qpstepSpin.setRange(-99999, 99999)

        self.qpminSpin.setObjectName('qpmin')
        self.qpminSpin.setRange(0, 69)

        self.qpmaxSpin.setObjectName('qpmax')
        self.qpmaxSpin.setRange(0, 69)

        self.scenecutAwareQpSpin.setObjectName('scenecut-aware-qp')
        self.scenecutAwareQpSpin.setRange(0, 3)

        self.maskingStrengthLine.setObjectName('masking-strength')

        self.vbvLiveMultiPassCheckBox.setObjectName('vbv-live-multi-pass')

        self.statsLine.setObjectName('stats')

        self.slowFirstpassCheckBox.setObjectName('slow-firstpass')

        self.multiPassOptAnalysisCheckBox.setObjectName('multi-pass-opt-analysis')

        self.multiPassOptDistortionCheckBox.setObjectName('multi-pass-opt-distortion')

        self.analysisReuseFileLine.setObjectName('analysis-reuse-file')

        self.strictCbrCheckBox.setObjectName('strict-cbr')

        form1.form.addRow(self.slowFirstpassCheckBox)
        form1.form.addRow(self.multiPassOptAnalysisCheckBox)
        form1.form.addRow(self.multiPassOptDistortionCheckBox)
        form1.form.addRow(QLabel('analysis-reuse-file'))
        form1.form.addRow(self.analysisReuseFileLine)
        form1.form.addRow(QLabel('stats'))
        form1.form.addRow(self.statsLine)

        form2.form.addRow('qpstep', self.qpstepSpin)
        form2.form.addRow('qpmin', self.qpminSpin)
        form2.form.addRow('qpmax', self.qpmaxSpin)
        form2.form.addRow('scenecut-aware-qp', self.scenecutAwareQpSpin)
        form2.form.addRow('masking-strength', self.maskingStrengthLine)

        form3.form.addRow('crf-max', self.crfMaxSpin)
        form3.form.addRow('crf-min', self.crfMinSpin)

        form4.form.addRow('vbv-bufsize', self.vbvBufsizeSpin)
        form4.form.addRow('vbv-maxrate', self.vbvMaxrateSpin)
        form4.form.addRow('vbv-init', self.vbvInitSpin)
        form4.form.addRow('vbv-end', self.vbvEndSpin)
        form4.form.addRow('vbv-end-fr-adj', self.vbvEndFrAdjSpin)
        form4.form.addRow('min-vbv-fullness', self.minVbvFullnessSpin)
        form4.form.addRow('max-vbv-fullness', self.maxVbvFullnessSpin)
        form4.form.addRow(self.constVbvCheckBox)
        form4.form.addRow(self.vbvLiveMultiPassCheckBox)

        form5.form.addRow('asm', self.asmComboBox)
        form5.form.addRow(self.copyPictureCheckBox)

        form6.form.addRow('frame-threads', self.frameThreadsSpin)
        form6.form.addRow(QLabel('pools'))
        form6.form.addRow(self.poolsLine)
        form6.form.addRow(self.wppCheckBox)
        form6.form.addRow(self.pmodeCheckBox)
        form6.form.addRow(self.pmeCheckBox)
        form6.form.addRow('slices', self.slicesSpin)

    def init_analysis(self):
        home = QHBoxLayout()

        form1 = self.groupBoxes[14]
        form2 = self.groupBoxes[15]
        form3 = self.groupBoxes[16]
        form4 = self.groupBoxes[17]
        form5 = self.groupBoxes[18]
        form6 = self.groupBoxes[19]
        form7 = self.groupBoxes[20]

        box1 = QVBoxLayout()
        box2 = QVBoxLayout()
        box3 = QVBoxLayout()

        home.addLayout(box1)
        home.addLayout(box2)
        home.addLayout(box3)
        home.setStretch(0, 1)
        home.setStretch(1, 1)
        home.setStretch(2, 1)

        box1.addWidget(form1)
        box1.addWidget(form2)
        box1.addStretch(1)
        box2.addWidget(form3)
        box2.addWidget(form4)
        box2.addWidget(form5)
        box2.addStretch(1)
        box3.addWidget(form6)
        box3.addWidget(form7)
        box3.addStretch(1)

        self.rdSpin.setObjectName('rd')
        self.rdSpin.setRange(0, 6)

        self.ctuComboBox.setObjectName('ctu')
        self.ctuComboBox.addItems(('64', '32', '16'))

        self.minCUComboBox.setObjectName('min-cu-size')
        self.minCUComboBox.addItems(('32', '16', '8'))

        self.limitRefsSpin.setObjectName('limit-refs')
        self.limitRefsSpin.setRange(0, 3)

        self.limitModesCheckBox.setObjectName('limit-modes')

        self.rectCheckBox.setObjectName('rect')

        self.ampCheckBox.setObjectName('amp')

        self.earlySkipCheckBox.setObjectName('early-skip')

        self.rskipSpinBox.setObjectName('rskip')
        self.rskipSpinBox.setRange(0, 2)

        self.rskipEdgeThresholdSpinBox.setObjectName('rskip-edge-threshold')
        self.rskipEdgeThresholdSpinBox.setRange(0, 100)

        self.splitrdSkipCheckBox.setObjectName('splitrd-skip')

        self.fastIntraCheckBox.setObjectName('fast-intra')

        self.cuLosslessCheckBox.setObjectName('cu-lossless')

        self.tskipFastCheckBox.setObjectName('tskip-fast')

        self.rdRefineCheckBox.setObjectName('rd-refine')

        self.analysisSaveLine.setObjectName('analysis-save')

        self.analysisLoadLine.setObjectName('analysis-load')

        self.analysisSaveReuseLevelSpin.setObjectName('analysis-save-reuse-level')
        self.analysisSaveReuseLevelSpin.setRange(1, 10)

        self.analysisLoadReuseLevelSpin.setObjectName('analysis-load-reuse-level')
        self.analysisLoadReuseLevelSpin.setRange(1, 10)

        self.refineMvTypeLine.setObjectName('refine-mv-type')

        self.refineCtuDistortionSpin.setObjectName('refine-ctu-distortion')
        self.refineCtuDistortionSpin.setRange(0, 1)

        self.scaleFactorSpin.setObjectName('scale-factor')
        self.scaleFactorSpin.setRange(0, 2)

        self.refineIntraSpin.setObjectName('refine-intra')
        self.refineIntraSpin.setRange(0, 4)

        self.refineInterSpin.setObjectName('refine-inter')
        self.refineInterSpin.setRange(0, 3)

        self.dynamicRefineCheckBox.setObjectName('dynamic-refine')

        self.refineMVCheckBox.setObjectName('refine-mv')

        self.rdoqLevelSpin.setObjectName('rdoq-level')
        self.rdoqLevelSpin.setRange(-1, 2)

        self.tuIntraDepthSpin.setObjectName('tu-intra-depth')
        self.tuIntraDepthSpin.setRange(1, 4)

        self.tuInterDepthSpin.setObjectName('tu-inter-depth')
        self.tuInterDepthSpin.setRange(1, 4)

        self.limitTuSpin.setObjectName('limit-tu')
        self.limitTuSpin.setRange(0, 4)

        self.tskipCheckBox.setObjectName('tskip')

        self.rdpenaltySpin.setObjectName('rdpenalty')
        self.rdpenaltySpin.setRange(0, 2)

        self.maxTUComboBox.setObjectName('max-tu-size')
        self.maxTUComboBox.addItems(('32', '16', '8', '4'))

        self.dynamicRdSpin.setObjectName('dynamic-rd')
        self.dynamicRdSpin.setRange(0, 4)

        self.ssimRdCheckBox.setObjectName('ssim-rd')

        self.psyRdSpin.setObjectName('psy-rd')
        self.psyRdSpin.setRange(0, 5.0)
        self.psyRdSpin.setDecimals(1)
        self.psyRdSpin.setSingleStep(0.1)

        self.psyRdoqSpin.setObjectName('psy-rdoq')
        self.psyRdoqSpin.setRange(0, 50.0)
        self.psyRdoqSpin.setDecimals(1)
        self.psyRdoqSpin.setSingleStep(0.1)
        self.analysisWidget.setLayout(home)

        form1.form.addRow('rd', self.rdSpin)
        form1.form.addRow(self.fastIntraCheckBox)
        form1.form.addRow(self.cuLosslessCheckBox)
        form1.form.addRow(self.rdRefineCheckBox)
        form1.form.addRow(self.ssimRdCheckBox)
        form1.form.addRow('psy-rd', self.psyRdSpin)
        form1.form.addRow('dynamic-rd', self.dynamicRdSpin)

        form2.form.addRow('ctu', self.ctuComboBox)
        form2.form.addRow('min-cu-size', self.minCUComboBox)
        form2.form.addRow('max-tu-size', self.maxTUComboBox)
        form2.form.addRow('tu-intra-depth', self.tuIntraDepthSpin)
        form2.form.addRow('tu-inter-depth', self.tuInterDepthSpin)
        form2.form.addRow('limit-tu', self.limitTuSpin)
        form2.form.addRow('rdpenalty', self.rdpenaltySpin)

        form3.form.addRow(self.rectCheckBox)
        form3.form.addRow(self.ampCheckBox)
        form3.form.addRow(self.limitModesCheckBox)

        form4.form.addRow('rdoq-level', self.rdoqLevelSpin)
        form4.form.addRow('psy-rdoq', self.psyRdoqSpin)

        form5.form.addRow(self.earlySkipCheckBox)
        form5.form.addRow('rskip', self.rskipSpinBox)
        form5.form.addRow('rskip-edge-threshold', self.rskipEdgeThresholdSpinBox)
        form5.form.addRow(self.tskipCheckBox)
        form5.form.addRow(self.tskipFastCheckBox)
        form5.form.addRow(self.splitrdSkipCheckBox)

        form6.form.addRow(self.dynamicRefineCheckBox)
        form6.form.addRow('refine-intra', self.refineIntraSpin)
        form6.form.addRow('refine-inter', self.refineInterSpin)
        form6.form.addRow(self.refineMVCheckBox)
        form6.form.addRow(QLabel('refine-mv-type', self))
        form6.form.addRow(self.refineMvTypeLine)
        form6.form.addRow('refine-ctu-distortion', self.refineCtuDistortionSpin)

        form7.form.addRow(QLabel('analysis-save', self))
        form7.form.addRow(self.analysisSaveLine)
        form7.form.addRow('analysis-save-reuse-level', self.analysisSaveReuseLevelSpin)
        form7.form.addRow(QLabel('analysis-load', self))
        form7.form.addRow(self.analysisLoadLine)
        form7.form.addRow('analysis-load-reuse-level', self.analysisLoadReuseLevelSpin)
        form7.form.addRow('scale-factor', self.scaleFactorSpin)

    def init_frame(self):
        home = QHBoxLayout()

        form1 = self.groupBoxes[21]
        form2 = self.groupBoxes[22]
        form3 = self.groupBoxes[23]
        form4 = self.groupBoxes[24]
        form5 = self.groupBoxes[25]
        form6 = self.groupBoxes[26]
        form7 = self.groupBoxes[27]

        box1 = QVBoxLayout()
        box2 = QVBoxLayout()
        box3 = QVBoxLayout()
        home.setStretch(0, 1)
        home.setStretch(1, 1)
        home.setStretch(2, 1)

        home.addLayout(box1)
        home.addLayout(box2)
        home.addLayout(box3)

        box1.addWidget(form1)
        box1.addWidget(form3)
        box1.addStretch(1)
        box2.addWidget(form4)
        box2.addWidget(form2)
        box2.addStretch(1)
        box3.addWidget(form5)
        box3.addWidget(form6)
        box3.addWidget(form7)
        box3.addStretch(1)

        self.bIntraCheckBox.setObjectName('b-intra')

        self.nrIntraSpin.setObjectName('nr-intra')
        self.nrIntraSpin.setRange(0, 2000)

        self.nrInterSpin.setObjectName('nr-inter')
        self.nrInterSpin.setRange(0, 2000)

        self.maxMergeSpin.setObjectName('max-merge')
        self.maxMergeSpin.setRange(1, 5)

        self.meComboBox.setObjectName('me')
        self.meComboBox.addItems(('dia', 'hex', 'umh', 'star', 'sea', 'full'))

        self.submeSpin.setObjectName('subme')
        self.submeSpin.setRange(0, 7)

        self.merangeSpin.setObjectName('merange')
        self.merangeSpin.setRange(0, 32768)

        self.temporalMvpCheckBox.setObjectName('temporal-mvp')

        self.weightpCheckBox.setObjectName('weightp')

        self.weightbCheckBox.setObjectName('weightb')

        self.analyzeSrcPicsCheckBox.setObjectName('analyze-src-pics')

        self.hmeCheckBox.setObjectName('hme')

        self.hmeSearch1.setObjectName('hme-search1')
        self.hmeSearch1.setRange(0, 5)

        self.hmeSearch2.setObjectName('hme-search2')
        self.hmeSearch2.setRange(0, 5)

        self.hmeSearch3.setObjectName('hme-search3')
        self.hmeSearch3.setRange(0, 5)

        self.hmeRange1.setObjectName('hme-range1')
        self.hmeRange1.setRange(0, 32768)

        self.hmeRange2.setObjectName('hme-range2')
        self.hmeRange2.setRange(0, 32768)

        self.hmeRange3.setObjectName('hme-range3')
        self.hmeRange3.setRange(0, 32768)

        self.strongIntraSmoothingCheckBox.setObjectName('strong-intra-smoothing')

        self.constrainedIntraCheckBox.setObjectName('constrained-intra')

        self.openGopCheckBox.setObjectName('open-gop')

        self.keyintSpin.setObjectName('keyint')
        self.keyintSpin.setRange(-1, 9999)

        self.minKeyintSpin.setObjectName('min-keyint')
        self.minKeyintSpin.setRange(0, 9999)

        self.scenecutSpin.setObjectName('scenecut')
        self.scenecutSpin.setRange(0, 99999)

        self.scenecutBiasSpin.setObjectName('scenecut-bias')
        self.scenecutBiasSpin.setRange(0, 100.0)
        self.scenecutBiasSpin.setDecimals(1)
        self.scenecutBiasSpin.setSingleStep(1)

        self.histScenecutCheckBox.setObjectName('hist-scenecut')

        self.histThresholdSpin.setObjectName('hist-threshold')
        self.histThresholdSpin.setRange(0, 2)
        self.histThresholdSpin.setDecimals(2)
        self.histThresholdSpin.setSingleStep(0.1)

        self.radlSpin.setObjectName('radl')
        self.radlSpin.setRange(0, 16)

        self.ctuInfoComboBox.setObjectName('ctu-info')
        self.ctuInfoComboBox.addItems(('0', '1', '2', '4', '6'))

        self.intraRefreshCheckBox.setObjectName('intra-refresh')

        self.rcLookaheadSpin.setObjectName('rc-lookahead')
        self.rcLookaheadSpin.setRange(0, 250)

        self.gopLookaheadSpin.setObjectName('gop-lookahead')
        self.gopLookaheadSpin.setRange(0, 999)

        self.lookaheadSlicesSpin.setObjectName('lookahead-slices')
        self.lookaheadSlicesSpin.setRange(0, 16)

        self.lookaheadthreadsSpin.setObjectName('lookahead-threads')
        self.lookaheadthreadsSpin.setRange(0, cpu_count() // 2)

        self.bAdaptSpin.setObjectName('b-adapt')
        self.bAdaptSpin.setRange(0, 2)

        self.bframesSpin.setObjectName('bframes')
        self.bframesSpin.setRange(0, 16)

        self.bframeBiasSpin.setObjectName('bframe-bias')
        self.bframeBiasSpin.setRange(-90, 100)

        self.bPyramidCheckBox.setObjectName('b-pyramid')

        self.forceFlushSpin.setObjectName('force-flush')
        self.forceFlushSpin.setRange(0, 2)

        self.fadesCheckBox.setObjectName('fades')

        self.frameWidget.setLayout(home)

        hme_search_layout = QHBoxLayout()
        hme_search_layout.addWidget(self.hmeSearch1)
        hme_search_layout.addWidget(self.hmeSearch2)
        hme_search_layout.addWidget(self.hmeSearch3)

        hme_range_layout = QHBoxLayout()
        hme_range_layout.addWidget(self.hmeRange1)
        hme_range_layout.addWidget(self.hmeRange2)
        hme_range_layout.addWidget(self.hmeRange3)

        form1.form.addRow('max-merge', self.maxMergeSpin)
        form1.form.addRow('me', self.meComboBox)
        form1.form.addRow('subme', self.submeSpin)
        form1.form.addRow('merange', self.merangeSpin)
        form1.form.addRow(self.weightbCheckBox)
        form1.form.addRow(self.weightpCheckBox)
        form1.form.addRow(self.temporalMvpCheckBox)
        form1.form.addRow(self.analyzeSrcPicsCheckBox)
        form1.form.addRow(self.temporalMvpCheckBox)
        form1.form.addRow(self.analyzeSrcPicsCheckBox)
        form1.form.addRow(self.hmeCheckBox)
        form1.form.addRow('hme-search', hme_search_layout)
        form1.form.addRow('hme-range', hme_range_layout)

        form2.form.addRow('rc-lookahead', self.rcLookaheadSpin)
        form2.form.addRow('gop-lookahead', self.gopLookaheadSpin)
        form2.form.addRow('lookahead-slices', self.lookaheadSlicesSpin)
        form2.form.addRow('lookahead-threads', self.lookaheadthreadsSpin)

        form3.form.addRow(self.openGopCheckBox)
        form3.form.addRow('keyint', self.keyintSpin)
        form3.form.addRow('min-keyint', self.minKeyintSpin)

        form4.form.addRow('scenecut', self.scenecutSpin)
        form4.form.addRow('scenecut-bias', self.scenecutBiasSpin)
        form4.form.addRow(self.histScenecutCheckBox)
        form4.form.addRow('hist-threshold', self.histThresholdSpin)
        form4.form.addRow('radl', self.radlSpin)
        form4.form.addRow(self.intraRefreshCheckBox)
        form4.form.addRow('force-flush', self.forceFlushSpin)

        form5.form.addRow(self.strongIntraSmoothingCheckBox)
        form5.form.addRow(self.constrainedIntraCheckBox)

        form6.form.addRow('b-adapt', self.bAdaptSpin)
        form6.form.addRow('bframes', self.bframesSpin)
        form6.form.addRow('bframe-bias', self.bframeBiasSpin)
        form6.form.addRow(self.bPyramidCheckBox)

        form7.form.addRow('nr-intra', self.nrIntraSpin)
        form7.form.addRow('nr-inter', self.nrInterSpin)
        form7.form.addRow(self.bIntraCheckBox)
        form7.form.addRow('ctu-info', self.ctuInfoComboBox)
        form7.form.addRow(self.fadesCheckBox)

    def init_quantization(self):
        home = QHBoxLayout()

        form1 = self.groupBoxes[28]
        form2 = self.groupBoxes[29]
        form3 = self.groupBoxes[30]
        form4 = self.groupBoxes[31]
        form5 = self.groupBoxes[32]
        form6 = self.groupBoxes[33]
        form7 = self.groupBoxes[34]
        form8 = self.groupBoxes[35]

        box1 = QVBoxLayout()
        box2 = QVBoxLayout()
        box3 = QVBoxLayout()

        home.addLayout(box1)
        home.addLayout(box2)
        home.addLayout(box3)
        home.setStretch(0, 1)
        home.setStretch(1, 1)
        home.setStretch(2, 1)

        box1.addWidget(form1)
        box1.addWidget(form2)
        box1.addWidget(form3)
        box1.addStretch(1)
        box2.addWidget(form4)
        box2.addWidget(form5)
        box2.addWidget(form6)
        box2.addStretch(1)
        box3.addWidget(form7)
        box3.addWidget(form8)
        box3.addStretch(1)

        self.slicesSpin.setObjectName('slices')
        self.slicesSpin.setRange(1, 99)

        self.copyPictureCheckBox.setObjectName('copy-pic')

        self.aqModeSpin.setObjectName('aq-mode')
        self.aqModeSpin.setRange(0, 4)

        self.aqStrengthSpin.setObjectName('aq-strength')
        self.aqStrengthSpin.setDecimals(1)
        self.aqStrengthSpin.setSingleStep(0.1)
        self.aqStrengthSpin.setRange(0, 3)

        self.hevcAqCheckBox.setObjectName('hevc-aq')

        self.aqMotionCheckBox.setObjectName('aq-motion')

        self.qgSizeComboBox.setObjectName('qg-size')
        self.qgSizeComboBox.addItems(('64', '32', '16', '8'))

        self.cutreeCheckBox.setObjectName('cutree')

        self.cbqpoffsSpin.setObjectName('cbqpoffs')
        self.cbqpoffsSpin.setRange(-12, 12)

        self.crqpoffsSpin.setObjectName('crqpoffs')
        self.crqpoffsSpin.setRange(-12, 12)

        self.ipratioSpin.setObjectName('ipratio')
        self.ipratioSpin.setDecimals(1)
        self.ipratioSpin.setSingleStep(0.1)
        self.ipratioSpin.setRange(0, 999999)

        self.pbratioSpin.setObjectName('pbratio')
        self.pbratioSpin.setDecimals(1)
        self.pbratioSpin.setSingleStep(0.1)
        self.pbratioSpin.setRange(0, 99999)

        self.qcompSpin.setObjectName('qcomp')
        self.qcompSpin.setDecimals(2)
        self.qcompSpin.setSingleStep(0.05)
        self.qcompSpin.setRange(0.5, 1)

        self.qblurSpin.setObjectName('qblur')
        self.qblurSpin.setDecimals(1)
        self.qblurSpin.setSingleStep(0.1)
        self.qblurSpin.setRange(0, 99999)

        self.cplxblurSpin.setObjectName('cplxblur')
        self.cplxblurSpin.setDecimals(1)
        self.cplxblurSpin.setRange(0, 99999)

        self.rcGrainCheckBox.setObjectName('rc-grain')

        self.zonesLine.setObjectName('zones')

        self.zonefileLine.setObjectName('zonefile')

        self.signhideCheckBox.setObjectName('signhide')

        self.qpfileLine.setObjectName('qpfile')

        self.scalingListLine.setObjectName('scaling-list')

        self.lambdaFileLine.setObjectName('lambda-file')

        self.maxAusizeFactorSpin.setObjectName('max-ausize-factor')
        self.maxAusizeFactorSpin.setDecimals(1)
        self.maxAusizeFactorSpin.setSingleStep(0.1)
        self.maxAusizeFactorSpin.setRange(0.5, 1)

        self.deblockCheckBox.setObjectName('deblock')
        self.deblockSpin1.setObjectName('tC offset')
        self.deblockSpin2.setObjectName('Beta offset')
        self.deblockSpin1.setRange(-6, 6)
        self.deblockSpin2.setRange(-6, 6)

        self.saoCheckBox.setObjectName('sao')

        self.saoNoneDeblockCheckBox.setObjectName('sao-non-deblock')

        self.limitSaoCheckBox.setObjectName('limit-sao')

        self.selectiveSaoSpin.setObjectName('selective-sao')

        self.quantizationWidget.setLayout(home)

        form1.form.addRow('aq-mode', self.aqModeSpin)
        form1.form.addRow('aq-strenth', self.aqStrengthSpin)
        form1.form.addRow(self.aqMotionCheckBox)
        form1.form.addRow(self.hevcAqCheckBox)

        form2.form.addRow(self.saoCheckBox)
        form2.form.addRow(self.saoNoneDeblockCheckBox)
        form2.form.addRow(self.limitSaoCheckBox)
        form2.form.addRow('selective-sao', self.selectiveSaoSpin)

        form3.form.addRow(self.deblockCheckBox)
        form3.form.addRow('tC', self.deblockSpin1)
        form3.form.addRow('Beta', self.deblockSpin2)

        form4.form.addRow('cbqpoffs', self.cbqpoffsSpin)
        form4.form.addRow('crqpoffs', self.crqpoffsSpin)
        form4.form.addRow('ipratio', self.ipratioSpin)
        form4.form.addRow('pbratio', self.pbratioSpin)

        form5.form.addRow(QLabel('zones'))
        form5.form.addRow(self.zonesLine)
        form5.form.addRow(QLabel('zonefile'))
        form5.form.addRow(self.zonefileLine)

        form6.form.addRow('qblur', self.qblurSpin)
        form6.form.addRow('cplxblur', self.cplxblurSpin)

        form7.form.addRow(self.signhideCheckBox)
        form7.form.addRow(QLabel('qpfile'))
        form7.form.addRow(self.qpfileLine)
        form7.form.addRow(QLabel('scaling-list'))
        form7.form.addRow(self.scalingListLine)
        form7.form.addRow(QLabel('lambda-file'))
        form7.form.addRow(self.lambdaFileLine)
        form7.form.addRow('max-ausize-factor', self.maxAusizeFactorSpin)

        form8.form.addRow('qg-size', self.qgSizeComboBox)
        form8.form.addRow(self.cutreeCheckBox)
        form8.form.addRow('qcomp', self.qcompSpin)
        form8.form.addRow(self.rcGrainCheckBox)

    def init_vui(self):
        home = QHBoxLayout()

        form1 = self.groupBoxes[36]
        form2 = self.groupBoxes[37]
        form3 = self.groupBoxes[38]
        form4 = self.groupBoxes[39]
        form5 = self.groupBoxes[40]

        box1 = QVBoxLayout()
        box2 = QVBoxLayout()
        box3 = QVBoxLayout()

        home.addLayout(box1)
        home.addLayout(box2)
        home.addLayout(box3)
        home.setStretch(0, 1)
        home.setStretch(1, 1)
        home.setStretch(2, 1)

        box1.addWidget(form1)
        box1.addWidget(form2)
        box1.addStretch(1)
        box2.addWidget(form3)
        box2.addWidget(form4)
        box2.addStretch(1)
        box3.addWidget(form5)
        box3.addStretch(1)

        self.sarComboBox.setObjectName('sar')
        self.sarComboBox.addItems(
            ('1:1',
             '12:11',
             '10:11',
             '16:11',
             '40:33',
             '24:11',
             '20:11',
             '32:11',
             '80:33',
             '18:11',
             '15:11',
             '64:33',
             '160:99',
             '4:3',
             '3:2',
             '2:1'))
        self.sarComboBox.setEditable(True)
        self.sarComboBox.editTextChanged.connect(self.command_change)
        self.sarComboBox.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(r'[0-9]+:[0-9]+')))
        self.sarComboBox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.sarComboBox.lineEdit().setClearButtonEnabled(True)

        self.displayWindowSpinL.setObjectName('displayWindowSpinL')
        self.displayWindowSpinT.setObjectName('displayWindowSpinT')
        self.displayWindowSpinR.setObjectName('displayWindowSpinR')
        self.displayWindowSpinB.setObjectName('displayWindowSpinB')

        for spin in (self.displayWindowSpinL, self.displayWindowSpinT,
                     self.displayWindowSpinR, self.displayWindowSpinB):
            spin.setRange(0, 9999)
            spin.setValue(0)

        self.overscanComboBox.setObjectName('overscan')
        self.overscanComboBox.addItems(('', 'show', 'crop'))

        self.videoformatComboBox.setObjectName('videoformat')
        self.videoformatComboBox.addItems(
            ('', 'component', 'pal', 'ntsc', 'secam', 'mac', 'undefined'))

        self.rangeComboBox.setObjectName('range')
        self.rangeComboBox.addItems(('', 'full', 'limited'))

        self.colorprimComboBox.setObjectName('colorprim')
        self.colorprimComboBox.addItems(
            ('',
             'bt709',
             'unknown',
             'reserved',
             'bt470m',
             'bt470bg',
             'smpte170m',
             'smpte240m',
             'film',
             'bt2020',
             'smpte428',
             'smpte431',
             'smpte432'))

        self.transferComboBox.setObjectName('transfer')
        self.transferComboBox.addItems(
            ('',
             'bt709',
             'unknown',
             'reserved',
             'bt470m',
             'bt470bg',
             'smpte170m',
             'smpte240m',
             'linear',
             'log100',
             'log316',
             'iec61966-2-4',
             'bt1361e',
             'iec61966-2-1',
             'bt2020-10',
             'bt2020-12',
             'smpte2084',
             'smpte428',
             'arib-std-b67'))

        self.colormatrixComboBox.setObjectName('colormatrix')
        self.colormatrixComboBox.addItems(
            ('',
             'GBR',
             'bt709',
             'undef',
             'reserved',
             'fcc',
             'bt470bg',
             'smpte170m',
             'smpte240m',
             'YCgCo',
             'bt2020nc',
             'bt2020c',
             'smpte2085',
             'chroma-derived-nc',
             'chroma-derived-c',
             'ictcp'))

        self.chromalocSpin.setObjectName('chromaloc')
        self.chromalocSpin.setRange(-1, 5)

        self.masterDisplayLine.setObjectName('master-display')

        self.maxCllLine.setObjectName('max-cll')

        self.cllCheckBox.setObjectName('cll')

        self.hdr10CheckBox.setObjectName('hdr10')

        self.hdr10OptCheckBox.setObjectName('hdr10-opt')

        self.dhdr10InfoLine.setObjectName('dhdr10-info')

        self.dhdr10OptCheckBox.setObjectName('dhdr10-opt')

        self.minLumaSpin.setObjectName('min-luma')
        self.minLumaSpin.setRange(-1, 4095)

        self.maxLumaSpin.setObjectName('max-luma')
        self.maxLumaSpin.setRange(-1, 4095)

        self.naluFileLine.setObjectName('nalu-file')

        self.atcSeiSpin.setObjectName('atc-sei')
        self.atcSeiSpin.setRange(-1, 999)

        self.picStructSpin.setObjectName('pic-struct')
        self.picStructSpin.setRange(-1, 12)

        self.svtCheckBox.setObjectName('svt')

        self.svtHmeCheckBox.setObjectName('svt-hme')

        self.svtSearchWidthSpin.setObjectName('svt-search-width')
        self.svtSearchWidthSpin.setRange(0, 256)

        self.svtSearchHeightSpin.setObjectName('svt-search-height')
        self.svtSearchHeightSpin.setRange(0, 256)

        self.svtCompressedTenBitFormatCheckBox.setObjectName('svt-compressed-ten-bit-format')

        self.svtSpeedControlCheckBox.setObjectName('svt-speed-control')

        self.svtPresetTunerSpin.setObjectName('svt-preset-tuner')
        self.svtPresetTunerSpin.setRange(-1, 1)

        self.svtHierarchicalLevelSpin.setObjectName('svt-hierarchical-level')
        self.svtHierarchicalLevelSpin.setRange(0, 3)

        self.svtBaseLayerSwitchModeSpin.setObjectName('svt-base-layer-switch-mode')
        self.svtBaseLayerSwitchModeSpin.setRange(0, 1)

        self.svtPredStructSpin.setObjectName('svt-pred-struct')
        self.svtPredStructSpin.setRange(0, 2)

        self.svtFpsInVpsCheckBox.setObjectName('svt-fps-in-vps')

        self.yuiWidget.setLayout(home)
        form1.form.addRow('sar', self.sarComboBox)
        form1.form.addRow('overscan', self.overscanComboBox)
        form1.form.addRow(QLabel('display-windows'))
        form1.form.addRow('左', self.displayWindowSpinL)
        form1.form.addRow('上', self.displayWindowSpinT)
        form1.form.addRow('右', self.displayWindowSpinR)
        form1.form.addRow('下', self.displayWindowSpinB)

        form2.form.addRow(self.hdr10CheckBox)
        form2.form.addRow(self.hdr10OptCheckBox)
        form2.form.addRow('dhdr10-info', self.dhdr10InfoLine)
        form2.form.addRow(self.dhdr10OptCheckBox)
        form2.form.addRow('master-display', self.masterDisplayLine)
        form2.form.addRow('max-cll', self.maxCllLine)

        form3.form.addRow('videoformat', self.videoformatComboBox)
        form3.form.addRow('range', self.rangeComboBox)
        form3.form.addRow('colorprim', self.colorprimComboBox)
        form3.form.addRow('transfer', self.transferComboBox)
        form3.form.addRow('colormatrix', self.colormatrixComboBox)
        form3.form.addRow('chromaloc', self.chromalocSpin)
        form3.form.addRow(self.cllCheckBox)
        form3.form.addRow('min-luma', self.minLumaSpin)
        form3.form.addRow('max-luma', self.maxLumaSpin)

        form4.form.addRow('nalu-file', self.naluFileLine)
        form4.form.addRow('atc-sei', self.atcSeiSpin)
        form4.form.addRow('pic-struct', self.picStructSpin)

        form5.form.addRow(self.svtCheckBox)
        form5.form.addRow(self.svtHmeCheckBox)
        form5.form.addRow('svt-search-width', self.svtSearchWidthSpin)
        form5.form.addRow('svt-search-height', self.svtSearchHeightSpin)
        form5.form.addRow(self.svtCompressedTenBitFormatCheckBox)
        form5.form.addRow(self.svtSpeedControlCheckBox)
        form5.form.addRow('svt-preset-tuner', self.svtPresetTunerSpin)
        form5.form.addRow('svt-hierarchical-level', self.svtHierarchicalLevelSpin)
        form5.form.addRow('svt-base-layer-switch-mode', self.svtBaseLayerSwitchModeSpin)
        form5.form.addRow('svt-pred-struct', self.svtPredStructSpin)
        form5.form.addRow(self.svtFpsInVpsCheckBox)

    def init_bitstream(self):
        home = QHBoxLayout(self.bitStreamWidget)

        form1 = self.groupBoxes[41]
        form2 = self.groupBoxes[42]
        form3 = self.groupBoxes[43]
        form4 = self.groupBoxes[44]
        form5 = self.groupBoxes[45]
        form6 = self.groupBoxes[46]
        form7 = self.groupBoxes[47]
        form8 = self.groupBoxes[48]
        form9 = self.groupBoxes[49]

        box1 = QVBoxLayout()
        box2 = QVBoxLayout()
        box3 = QVBoxLayout()

        home.addLayout(box1)
        home.addLayout(box2)
        home.addLayout(box3)
        home.setStretch(0, 1)
        home.setStretch(1, 1)
        home.setStretch(2, 1)

        box1.addWidget(form1)
        box1.addWidget(form2)
        box1.addWidget(form3)
        box1.addWidget(form4)
        box1.addStretch(1)
        box2.addWidget(form5)
        box2.addWidget(form6)
        box2.addWidget(form7)
        box2.addStretch(1)
        box3.addWidget(form8)
        box3.addWidget(form9)

        self.annexbCheckBox.setObjectName('annexb')

        self.repeatHeadersCheckBox.setObjectName('repeat-headers')

        self.audCheckBox.setObjectName('aud')

        self.hrdCheckBox.setObjectName('hrd')

        self.hrdConcatCheckBox.setObjectName('hrd-concat')

        self.dolbyVisionProfileComboBox.setObjectName('dolby-vision-profile')
        self.dolbyVisionProfileComboBox.addItems(('0', '5', '8.1', '8.2'))

        self.dolbyVisionRpuLine.setObjectName('dolby-vision-rpu')

        self.infoCheckBox.setObjectName('info')

        self.hashComboBox.setObjectName('hash')
        self.hashComboBox.addItems(('', 'MD5', 'CRC', 'Checksum'))

        self.temporalLayersCheckBox.setObjectName('temporal-layers')

        self.log2MaxPocLsbSpin.setObjectName('log2-max-poc-lsb')
        self.log2MaxPocLsbSpin.setRange(0, 999)

        self.vuiTimingInfoCheckBox.setObjectName('vui-timing-info')

        self.vuiHrdInfoCheckBox.setObjectName('vui-hrd-info')

        self.optQpPpsCheckBox.setObjectName('opt-qp-pps')

        self.optRefListLengthPpsCheckBox.setObjectName('opt-ref-list-length-pps')

        self.multiPassOptRpsCheckBox.setObjectName('multi-pass-opt-rps')

        self.optCuDeltaQpCheckBox.setObjectName('opt-cu-delta-qp')

        self.idrRecoverySeiCheckBox.setObjectName('idr-recovery-sei')

        self.singleSeiCheckBox.setObjectName('single-sei')

        self.logLevelComboBox.setObjectName('log-level')
        self.logLevelComboBox.addItems(('',) * 6)

        self.progressCheckBox.setObjectName('progress')

        self.csvLine.setObjectName('csv')

        self.csvLogLevelComboBox.setObjectName('csv-log-level')
        self.csvLogLevelComboBox.addItems(('',) * 3)

        self.customLine.setObjectName('custom')

        self.lowpassDctCheckBox.setObjectName('lowpass-dct')

        self.reconLine.setObjectName('recon')

        self.reconDepthSpin.setObjectName('recon-depth')
        self.reconDepthSpin.setRange(7, 7)

        self.reconY4mExecLine.setObjectName('recon-y4m-exec')

        form1.form.addRow(self.audCheckBox)
        form1.form.addRow(self.hrdCheckBox)
        form1.form.addRow(self.hrdConcatCheckBox)

        form2.form.addRow(self.optQpPpsCheckBox)
        form2.form.addRow(self.optRefListLengthPpsCheckBox)
        form2.form.addRow(self.multiPassOptRpsCheckBox)
        form2.form.addRow(self.optCuDeltaQpCheckBox)

        form3.form.addRow(self.vuiTimingInfoCheckBox)
        form3.form.addRow(self.vuiHrdInfoCheckBox)

        form4.form.addRow(self.lowpassDctCheckBox)

        form5.form.addRow('dolby-vision-profile', self.dolbyVisionProfileComboBox)
        form5.form.addRow('dolby-vision-rpu', self.dolbyVisionRpuLine)

        form6.form.addRow('recon', self.reconLine)
        form6.form.addRow('recon-depth', self.reconDepthSpin)
        form6.form.addRow('recon-y4m-exec', self.reconY4mExecLine)

        form7.form.addRow('log-level', self.logLevelComboBox)
        form7.form.addRow(self.progressCheckBox)
        form7.form.addRow(QLabel('csv'))
        form7.form.addRow(self.csvLine)
        form7.form.addRow(QLabel('csv-log-level'))
        form7.form.addRow(self.csvLogLevelComboBox)

        form8.form.addRow(self.annexbCheckBox)
        form8.form.addRow(self.repeatHeadersCheckBox)
        form8.form.addRow(self.infoCheckBox)
        form8.form.addRow('hash', self.hashComboBox)
        form8.form.addRow(self.temporalLayersCheckBox)
        form8.form.addRow('log2-max-poc-lsb', self.log2MaxPocLsbSpin)
        form8.form.addRow(self.idrRecoverySeiCheckBox)
        form8.form.addRow(self.singleSeiCheckBox)

        form9.form.addRow(self.customLine)

    def init_ui(self):
        shadow(self)
        home = QVBoxLayout()
        part_button = QHBoxLayout()
        part_code = QHBoxLayout()
        part_code_operation = QVBoxLayout()
        self.openButton.select_signal.connect(self.open)
        self.openButton.setIcon(set_icon(svgs.open))
        self.saveButton.select_signal.connect(self.save)
        self.saveButton.setIcon(set_icon(svgs.save))
        self.saveAsButton.select_signal.connect(self.save_as)
        self.saveAsButton.setIcon(set_icon(svgs.save_as))
        self.closeButton.clicked.connect(self.close_project)
        self.closeButton.setIcon(set_icon(svgs.close))
        for i in self.widgets:
            i.layout().setSpacing(10)
            i.layout().setContentsMargins(10, 10, 10, 10)
        for i in self.buttons:
            i.setFixedSize(128, 48)
            i.setIconSize(QSize(32, 32))
        self.commandPlainTextEdit.setReadOnly(True)
        self.customLine.textChanged.connect(self.custom)
        for i in self.comboBoxes:
            for n in range(i.count()):
                i.setItemData(n, QSize(16, 24), Qt.ItemDataRole.SizeHintRole)
            if i not in (self.fpsComboBox, self.sarComboBox):
                i.currentIndexChanged.connect(self.command_change)
        for i in self.checkBoxes:
            i.stateChanged.connect(self.command_change)
        for i in (self.commandLines + self.pathLines):
            i.textChanged.connect(self.command_change)
        for i in self.spins + self.doubleSpins:
            i.setWrapping(True)
            i.valueChanged.connect(self.command_change)
        names = list(self.allItems)
        names.append('lossless')
        names.sort(key=str.lower)
        self.searchComboBox.addItems(names)
        self.searchComboBox.setEditable(True)
        self.searchComboBox.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.searchComboBox.setMaxVisibleItems(20)
        self.searchComboBox.setValidator(
            QRegularExpressionValidator(
                QRegularExpression(r'[A-Za-z0-9][A-Za-z0-9 -]+')))
        self.searchComboBox.setCompleter(QCompleter(names))
        self.searchComboBox.currentTextChanged.connect(self.find_item)
        self.searchComboBox.lineEdit().setClearButtonEnabled(True)
        for i in range(self.searchComboBox.count()):
            self.searchComboBox.setItemData(i, QSize(16, 24), Qt.ItemDataRole.SizeHintRole)
        self.searchComboBox.setEditText('')

        self.titleLine.setReadOnly(True)

        part_title = QHBoxLayout()
        part_title.addWidget(self.titleLine)
        part_title.addWidget(self.versionLabel)

        self.setLayout(home)
        home.setContentsMargins(10, 10, 10, 10)
        home.addLayout(part_button)
        home.addLayout(part_title)
        home.addWidget(self.tab)
        home.addWidget(self.commandPlainTextEdit)
        home.addLayout(part_code)

        part_button.addWidget(self.openButton)
        part_button.addWidget(self.saveButton)
        part_button.addWidget(self.saveAsButton)
        part_button.addWidget(self.closeButton)
        part_button.addStretch(1)
        part_button.addWidget(self.searchComboBox)

        part_code.addWidget(self.commandPlainTextEdit)
        part_code.addLayout(part_code_operation)

        part_code_operation.addWidget(self.copyButton)
        part_code_operation.addWidget(self.resetButton)
        part_code_operation.addWidget(self.exportButton)

        self.copyButton.setIcon(set_icon(svgs.copy))
        self.copyButton.setIconSize(QSize(32, 32))
        self.copyButton.clicked.connect(self.copy_code)
        self.resetButton.setIcon(set_icon(svgs.eraser))
        self.resetButton.setIconSize(QSize(32, 32))
        self.resetButton.clicked.connect(self.reset)
        self.exportButton.setIcon(set_icon(svgs.bat))
        self.exportButton.setIconSize(QSize(32, 32))
        self.exportButton.clicked.connect(self.exportWidget.show)

        self.tab.addTab(self.profileWidget, '')
        self.tab.addTab(self.qualityWidget, '')
        self.tab.addTab(self.analysisWidget, '')
        self.tab.addTab(self.frameWidget, '')
        self.tab.addTab(self.quantizationWidget, '')
        self.tab.addTab(self.yuiWidget, '')
        self.tab.addTab(self.bitStreamWidget, '')

        self.commandPlainTextEdit.textChanged.connect(self.save_state_change)
        self.commandPlainTextEdit.setFixedHeight(128)

    def init_language(self, *, init_length: bool = True):
        self.exportWidget.init_language()
        self.title_change()

        for n in range(self.tab.count()):
            self.tab.setTabText(n, LANG_UI_TXT.commandWidget.tab[n])

        for button, text in zip(self.toolButtons, LANG_UI_TXT.commandWidget.tools):
            button.setToolTip(text)

        for i, text in zip(self.buttons, LANG_UI_TXT.commandWidget.buttons):
            i.setText(text)
        for i in (
                self.chunkStartSpin,
                self.chunkEndSpin,
                self.passSpin,
                self.crfMaxSpin,
                self.crfMinSpin,
                self.vbvEndSpin,
                self.rdoqLevelSpin,
                self.nrIntraSpin,
                self.nrInterSpin,
                self.rdpenaltySpin,
                self.dynamicRdSpin,
                self.scenecutSpin,
                self.radlSpin,
                self.refineCtuDistortionSpin,
                self.aqModeSpin):
            i.setSpecialValueText(LANG_UI_TXT.commandWidget.disable)
        for i in (
                self.inputResWidthSpin,
                self.inputResHeightSpin,
                self.chromalocSpin,
                self.minLumaSpin,
                self.maxLumaSpin,
                self.atcSeiSpin,
                self.picStructSpin,
                self.framesSpin,
                self.reconDepthSpin,
                self.svtSearchWidthSpin,
                self.svtSearchHeightSpin,
                self.svtPresetTunerSpin):
            i.setSpecialValueText(LANG_UI_TXT.commandWidget.undefined)
        self.minKeyintSpin.setSpecialValueText(LANG_UI_TXT.commandWidget.auto)
        self.frameThreadsSpin.setSpecialValueText(LANG_UI_TXT.commandWidget.auto)
        self.framesSpin.setSpecialValueText(LANG_UI_TXT.commandWidget.auto)
        self.asmComboBox.setItemText(0, LANG_UI_TXT.commandWidget.auto)
        self.asmComboBox.setItemText(14, LANG_UI_TXT.commandWidget.disable)

        for i in (
                self.overscanComboBox,
                self.videoformatComboBox,
                self.rangeComboBox,
                self.colorprimComboBox,
                self.transferComboBox,
                self.colormatrixComboBox,
                self.profileComboBox,
                self.hashComboBox,
                self.inputDepthComboBox,
                self.outputDepthComboBox,
                self.tuneComboBox):
            i.setItemText(0, LANG_UI_TXT.commandWidget.undefined)
        if init_length:
            self.init_length()

    def init_cmd_language(self, *, init_length: bool = True):
        def init_combobox(*combo_boxes):
            for comboBox in combo_boxes:
                for row in range(comboBox.count()):
                    comboBox.setItemText(
                        row, getattr(CMD_LANG_TXT.comboBoxes, comboBox.objectName())[row])

        for group, title in zip(self.groupBoxes, CMD_LANG_TXT.titles):
            group.setTitle(title)

        for i, text in zip(self.profileWidgetLabels, CMD_LANG_TXT.profileWidgetLabels):
            i.setText(text)
        init_combobox(
            self.logLevelComboBox,
            self.csvLogLevelComboBox,
            self.interlaceComboBox)

        self.levelComboBox.setItemText(0, getattr(CMD_LANG_TXT.comboBoxes, 'level-idc'))
        if init_length:
            self.init_length()

    def init_length(self):
        for i in self.comboBoxes:
            length = [QFontMetrics(i.font()).horizontalAdvance(i.itemText(n)) for n in range(i.count())]
            if length:
                if i.lineEdit() and i.lineEdit().isClearButtonEnabled():
                    i.setFixedWidth(max(length) + 55)
                else:
                    i.setFixedWidth(max(length) + 30)
        for i in self.spins + self.doubleSpins:
            length = (QFontMetrics(i.font()).horizontalAdvance(i.textFromValue(i.maximum())),
                      QFontMetrics(i.font()).horizontalAdvance(i.textFromValue(i.minimum())),
                      QFontMetrics(i.font()).horizontalAdvance(i.specialValueText()))
            i.setFixedWidth(max(length) + 24)

    def init_font(self, font: QFont, *, init_length: bool = True):
        self.exportWidget.init_font(font)
        for i in self.findChildren(QWidget):
            i.setFont(font)
        new_font = QFont(font)
        new_font.setBold(True)
        for group in self.groupBoxes:
            group.setFont(new_font)
        if init_length:
            self.init_length()

    def command_change(self, value, *, widget=None):
        sender = self.sender() if not widget else widget
        obj_name = sender.objectName()
        if type(sender) == QSpinBox:  # SpinBox
            pal = QPalette()
            if self.currentDefault[obj_name] != value:
                pal.setColor(QPalette.ColorRole.Text, QColor(255, 0, 0))
            else:
                pal.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            sender.lineEdit().setPalette(pal)
            if sender == self.bitrateSpin:
                self.__commands['bitrate'] = f'--bitrate {value}'
            elif sender in (self.inputResHeightSpin, self.inputResWidthSpin):
                width = self.inputResWidthSpin.value()
                height = self.inputResHeightSpin.value()
                self.__commands['input-res'] = '' if 0 in (height, width) \
                    else f'--input-res {width}x{height}'
            elif sender == self.passSpin:
                self.vbvLiveMultiPassCheckBox.setDisabled(True)
                if value == 0:
                    self.statsLine.setDisabled(True)
                    self.__commands['stats'] = ''
                    self.slowFirstpassCheckBox.setDisabled(True)
                    self.__commands['slow-firstpass'] = ''
                else:
                    self.statsLine.setEnabled(True)
                    self.check(self.statsLine)
                    if value == 2:
                        self.statsLine.dialog_type = QFileDialog.getOpenFileName
                        self.scenecutAwareQpSpin.setEnabled(True)
                        self.check(self.scenecutAwareQpSpin)
                        if self.__commands['vbv-bufsize'] != '' and self.__commands['vbv-maxrate'] != '':
                            self.vbvLiveMultiPassCheckBox.setEnabled(True)
                            self.check(self.vbvLiveMultiPassCheckBox)
                    else:
                        self.scenecutAwareQpSpin.setDisabled(True)
                        self.__commands['scenecut-aware-qp'] = ''
                        if value == 1:
                            self.statsLine.dialog_type = QFileDialog.getSaveFileName
                            if self.encodeModeComboBox.currentIndex() in (1, 3):
                                self.slowFirstpassCheckBox.setEnabled(True)
                                self.check(self.slowFirstpassCheckBox)
                            else:
                                self.slowFirstpassCheckBox.setDisabled(True)
                                self.__commands['slow-firstpass'] = ''
                        elif value == 3:
                            self.statsLine.dialog_type = QFileDialog.getSaveFileName
                self.check(sender)
            elif sender == self.rdoqLevelSpin:
                if value in (-1, 0):
                    if value == -1:
                        self.__commands['rdoq-level'] = '--no-rdoq-level'
                    else:
                        self.check(sender)
                    self.psyRdoqSpin.setDisabled(True)
                    self.__commands['psy-rdoq'] = ''
                else:
                    self.psyRdoqSpin.setEnabled(True)
                    self.check(self.psyRdoqSpin, sender)
            elif sender in (self.deblockSpin1, self.deblockSpin2):
                tc = self.deblockSpin1.value()
                beta = self.deblockSpin2.value()
                self.__commands['deblock'] = '' if tc == beta == 0 else f'--deblock {tc}:{beta}'
            elif sender == self.rdSpin:
                if value < 3 or self.__commands['lossless'] != '':
                    self.cuLosslessCheckBox.setDisabled(True)
                    self.__commands['cu-lossless'] = ''
                else:
                    self.cuLosslessCheckBox.setEnabled(True)
                    self.check(self.cuLosslessCheckBox)
                for i in (self.tskipCheckBox, self.ssimRdCheckBox, self.psyRdSpin):
                    if value < 3:
                        i.setDisabled(True)
                        self.__commands[i.objectName()] = ''
                    else:
                        i.setEnabled(True)
                        self.check(i)
                if value < 5:
                    self.dynamicRdSpin.setEnabled(True)
                    self.rdRefineCheckBox.setDisabled(True)
                    self.optCuDeltaQpCheckBox.setDisabled(True)
                    self.__commands['rd-refine'] = ''
                    self.__commands['opt-cu-delta-qp'] = ''
                    self.check(self.dynamicRdSpin)
                else:
                    self.dynamicRdSpin.setDisabled(True)
                    self.__commands['dynamic-rd'] = ''
                    self.rdRefineCheckBox.setEnabled(True)
                    self.optCuDeltaQpCheckBox.setEnabled(True)
                    self.check(
                        self.rdRefineCheckBox,
                        self.optCuDeltaQpCheckBox)
                self.check(sender)
            elif sender == self.keyintSpin:
                index = self.outputDepthComboBox.currentIndex()
                self.outputDepthComboBox.setCurrentIndex(0)
                self.outputDepthComboBox.setCurrentIndex(1)
                self.outputDepthComboBox.setCurrentIndex(index)
                self.check(sender)
            elif sender == self.rskipSpinBox:
                self.check(sender)
                if self.rskipSpinBox.value() == 2:
                    self.rskipEdgeThresholdSpinBox.setEnabled(True)
                else:
                    self.rskipEdgeThresholdSpinBox.setDisabled(True)
            elif sender in (self.vbvMaxrateSpin, self.vbvBufsizeSpin):
                another = self.vbvBufsizeSpin if sender == self.vbvMaxrateSpin else self.vbvMaxrateSpin
                if value:
                    if another.value() == 0:
                        another.setValue(value)
                else:
                    another.setValue(0)
                if value and another.value():
                    self.hrdCheckBox.setEnabled(True)
                    self.check(sender, self.hrdCheckBox)
                    if self.passSpin.value() == 2:
                        self.vbvLiveMultiPassCheckBox.setEnabled(True)
                    else:
                        self.vbvLiveMultiPassCheckBox.setDisabled(True)
                    if self.hrdCheckBox.isChecked():
                        self.vuiHrdInfoCheckBox.setEnabled(True)
                        self.check(sender, self.vuiHrdInfoCheckBox)
                    else:
                        self.vuiHrdInfoCheckBox.setDisabled(True)
                        self.__commands['vui-hrd-info'] = ''
                else:
                    self.hrdCheckBox.setDisabled(True)
                    self.vuiHrdInfoCheckBox.setDisabled(True)
                    self.__commands['vui-hrd-info'] = ''
                    self.__commands['hrd'] = ''
                    self.check(sender)
            elif sender == self.scenecutAwareQpSpin:
                if value:
                    self.maskingStrengthLine.setEnabled(True)
                    self.check(self.maskingStrengthLine)
                else:
                    self.maskingStrengthLine.setDisabled(True)
                    self.__commands['masking-strength'] = ''
                self.check(sender)
            elif sender in (
                    self.displayWindowSpinL,
                    self.displayWindowSpinT,
                    self.displayWindowSpinR,
                    self.displayWindowSpinB):
                left = self.displayWindowSpinL.value()
                top = self.displayWindowSpinT.value()
                right = self.displayWindowSpinR.value()
                bottom = self.displayWindowSpinB.value()
                self.__commands['display-window'] = '' if left == top == right == bottom == 0 \
                    else f'--display-window {left},{top},{right},{bottom} '
            elif sender == self.lookaheadSlicesSpin:
                self.pools()
                self.check(sender)
            elif sender == self.bframesSpin:
                self.radlSpin.setRange(0, value)
                self.check(sender)
            elif sender == self.framesSpin:
                self.profile(self.outputDepthComboBox.currentIndex())
                self.check(sender)
            elif sender in (self.analysisLoadReuseLevelSpin, self.analysisSaveReuseLevelSpin):
                if 7 <= value <= 9 or (not self.analysisLoadLine.text() and not self.analysisSaveLine.text()):
                    self.scaleFactorSpin.setDisabled(True)
                    self.__commands['scale-factor'] = ''
                else:
                    self.scaleFactorSpin.setEnabled(True)
                    self.check(self.scaleFactorSpin)
                self.check(sender)
            elif sender in (self.hmeRange1, self.hmeRange2, self.hmeRange3):
                if self.hmeRange1.value() == 16 and self.hmeRange2.value() == 32 and self.hmeRange3.value() == 48:
                    self.__commands['hme-range'] = ''
                else:
                    hme_range = ','.join(spin.text() for spin in (self.hmeRange1, self.hmeRange2, self.hmeRange3))
                    self.__commands['hme-range'] = f'--hme-range {hme_range}'
            elif sender in (self.hmeSearch1, self.hmeSearch2, self.hmeSearch3):
                if self.hmeSearch1.value() == 1 and self.hmeSearch2.value() == 2 and self.hmeSearch3.value() == 2:
                    self.__commands['hme-search'] = ''
                else:
                    hme_search = ','.join(spin.text() for spin in (self.hmeSearch1, self.hmeSearch2, self.hmeSearch3))
                    self.__commands['hme-search'] = f'--hme-search {hme_search}'
            else:
                self.check(sender)

        elif type(sender) == QDoubleSpinBox:  # DoubleSpinBox
            pal = QPalette()
            if self.currentDefault[obj_name] != value:
                pal.setColor(QPalette.ColorRole.Text, QColor(255, 0, 0))
            else:
                pal.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            sender.lineEdit().setPalette(pal)
            self.check(sender)

        elif type(sender) == QCheckBox:  # CheckBox
            pal = QPalette()
            if self.currentDefault[obj_name] is not sender.isChecked():
                pal.setColor(QPalette.ColorRole.WindowText, QColor(255, 0, 0))
            else:
                pal.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            sender.setPalette(pal)
            if sender == self.deblockCheckBox:
                if value:
                    self.deblockSpin1.setEnabled(True)
                    self.deblockSpin2.setEnabled(True)
                    tc = self.deblockSpin1.value()
                    beta = self.deblockSpin2.value()
                    self.__commands['deblock'] = '' if tc == beta == 0 else f'--deblock {tc}:{beta}'
                else:
                    self.deblockSpin1.setEnabled(False)
                    self.deblockSpin2.setEnabled(False)
                    self.__commands['deblock'] = '--no-deblock'
            elif sender == self.slowFirstpassCheckBox:
                if value:
                    self.__commands['slow-firstpass'] = ''
                    for i in (
                            self.refSpin,
                            self.meComboBox,
                            self.submeSpin,
                            self.rectCheckBox,
                            self.ampCheckBox,
                            self.maxMergeSpin,
                            self.earlySkipCheckBox,
                            self.fastIntraCheckBox,
                            self.rdSpin):
                        self.check(i)
                else:
                    self.__commands['slow-firstpass'] = '--no-slow-firstpass'
                    self.__commands[self.fastIntraCheckBox.objectName()] = ''
                    self.__commands[self.rectCheckBox.objectName()] = ''
                    self.__commands[self.ampCheckBox.objectName()] = ''
                    self.__commands[self.earlySkipCheckBox.objectName()] = ''
                    self.__commands[self.refSpin.objectName()] = ''
                    self.__commands[self.maxMergeSpin.objectName()] = ''
                    self.__commands[self.meComboBox.objectName()] = ''
                    self.__commands[self.submeSpin.objectName()] = ''
                    self.__commands[self.rdSpin.objectName()] = ''
                for i in (
                        self.refSpin,
                        self.meComboBox,
                        self.submeSpin,
                        self.rectCheckBox,
                        self.ampCheckBox,
                        self.maxMergeSpin,
                        self.earlySkipCheckBox,
                        self.fastIntraCheckBox,
                        self.rdSpin):
                    i.setEnabled(value)
            elif sender in (self.wppCheckBox, self.pmodeCheckBox, self.pmeCheckBox):
                if sender in (self.pmodeCheckBox, self.pmeCheckBox):
                    if value \
                            or self.__commands['pass'] == '' \
                            or self.__commands['analysis-save'] != '' \
                            or self.__commands['analysis-load'] != '':
                        self.multiPassOptDistortionCheckBox.setDisabled(True)
                        self.multiPassOptAnalysisCheckBox.setDisabled(True)
                    else:
                        self.multiPassOptDistortionCheckBox.setEnabled(True)
                        self.multiPassOptAnalysisCheckBox.setEnabled(True)
                    if sender == self.pmodeCheckBox:
                        if value \
                                or (self.multiPassOptAnalysisCheckBox.isChecked()
                                    or self.multiPassOptDistortionCheckBox.isChecked()):
                            self.analysisLoadLine.setDisabled(True)
                            self.analysisSaveLine.setDisabled(True)
                        else:
                            self.analysisLoadLine.setEnabled(True)
                            self.analysisSaveLine.setEnabled(True)

                self.pools()
                self.check(sender)
            elif sender in (self.allowNonConformanceCheckBox, self.bPyramidCheckBox):
                if self.allowNonConformanceCheckBox.isChecked():
                    self.refSpin.setRange(1, 16)
                else:
                    if self.bPyramidCheckBox.isChecked():
                        self.refSpin.setRange(1, 6)
                    else:
                        self.refSpin.setRange(1, 7)
                self.check(sender)
            elif sender in (self.multiPassOptAnalysisCheckBox, self.multiPassOptDistortionCheckBox):
                if self.multiPassOptAnalysisCheckBox.isChecked() or self.multiPassOptDistortionCheckBox.isChecked():
                    self.analysisReuseFileLine.setEnabled(True)
                    self.analysisSaveLine.setDisabled(True)
                    self.analysisLoadLine.setDisabled(True)
                    self.pmodeCheckBox.setDisabled(True)
                    self.pmeCheckBox.setDisabled(True)
                    self.__commands['pme'] = ''
                    self.__commands['pmode'] = ''
                    self.check(self.analysisReuseFileLine)
                else:
                    self.analysisReuseFileLine.setDisabled(True)
                    self.__commands['analysis-reuse-file'] = ''
                    self.analysisSaveLine.setEnabled(True)
                    self.analysisLoadLine.setEnabled(True)
                    self.pmodeCheckBox.setEnabled(True)
                    self.pmeCheckBox.setEnabled(True)
                    self.check(self.pmodeCheckBox, self.pmeCheckBox)
                self.check(sender)
            elif sender == self.hrdCheckBox:
                if value:
                    self.vuiHrdInfoCheckBox.setEnabled(True)
                    self.check(self.vuiHrdInfoCheckBox)
                else:
                    self.vuiHrdInfoCheckBox.setDisabled(True)
                    self.__commands['vui-hrd-info'] = ''
                self.check(sender)
            elif sender == self.svtCheckBox:
                if value:
                    self.svtHmeCheckBox.setEnabled(True)
                    self.svtSearchWidthSpin.setEnabled(True)
                    self.svtSearchHeightSpin.setEnabled(True)
                    self.svtCompressedTenBitFormatCheckBox.setEnabled(True)
                    self.svtSpeedControlCheckBox.setEnabled(True)
                    self.svtPresetTunerSpin.setEnabled(True)
                    self.svtHierarchicalLevelSpin.setEnabled(True)
                    self.svtBaseLayerSwitchModeSpin.setEnabled(True)
                    self.svtPredStructSpin.setEnabled(True)
                    self.svtFpsInVpsCheckBox.setEnabled(True)
                    self.check(self.svtHmeCheckBox, self.svtSearchWidthSpin, self.svtSearchHeightSpin,
                               self.svtCompressedTenBitFormatCheckBox, self.svtSpeedControlCheckBox,
                               self.svtPresetTunerSpin, self.svtHierarchicalLevelSpin,
                               self.svtBaseLayerSwitchModeSpin, self.svtPredStructSpin, self.svtFpsInVpsCheckBox)
                else:
                    self.svtHmeCheckBox.setDisabled(True)
                    self.svtSearchWidthSpin.setDisabled(True)
                    self.svtSearchHeightSpin.setDisabled(True)
                    self.svtCompressedTenBitFormatCheckBox.setDisabled(True)
                    self.svtSpeedControlCheckBox.setDisabled(True)
                    self.svtPresetTunerSpin.setDisabled(True)
                    self.svtHierarchicalLevelSpin.setDisabled(True)
                    self.svtBaseLayerSwitchModeSpin.setDisabled(True)
                    self.svtPredStructSpin.setDisabled(True)
                    self.svtFpsInVpsCheckBox.setDisabled(True)
                    self.__commands['svt-hme'] = ''
                    self.__commands['svt-search-width'] = ''
                    self.__commands['svt-search-height'] = ''
                    self.__commands['svt-compressed-ten-bit-format'] = ''
                    self.__commands['svt-speed-control'] = ''
                    self.__commands['svt-preset-tuner'] = ''
                    self.__commands['svt-hierarchical-level'] = ''
                    self.__commands['svt-base-layer-switch-mode'] = ''
                    self.__commands['svt-pred-struct'] = ''
                    self.__commands['svt-fps-in-vps'] = ''
                self.check(sender)
            else:
                self.check(sender)

        elif type(sender) == PathLineEdit:
            pal = QPalette()
            if self.currentDefault[obj_name] != value:
                pal.setColor(QPalette.ColorRole.Text, QColor(255, 0, 0))
            else:
                pal.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            sender.setPalette(pal)
            if sender == self.analysisSaveLine:
                if value:
                    self.analysisLoadLine.setDisabled(True)
                    self.analysisLoadReuseLevelSpin.setDisabled(True)
                    self.pmodeCheckBox.setDisabled(True)
                    self.analysisSaveReuseLevelSpin.setEnabled(True)
                    self.refineCtuDistortionSpin.setEnabled(True)
                    self.multiPassOptDistortionCheckBox.setDisabled(True)
                    self.multiPassOptAnalysisCheckBox.setDisabled(True)
                    self.analysisReuseFileLine.setDisabled(True)
                    self.__commands['analysis-load'] = ''
                    self.__commands['analysis-load-reuse-level'] = ''
                    self.__commands['pmode'] = ''
                    self.__commands['multi-pass-opt-analysis'] = ''
                    self.__commands['multi-pass-opt-distortion'] = ''
                    self.__commands['analysis-reuse-file'] = ''
                    self.check(self.analysisSaveReuseLevelSpin, self.refineCtuDistortionSpin)
                    if 7 <= self.analysisSaveReuseLevelSpin.value() <= 9:
                        self.scaleFactorSpin.setDisabled(True)
                        self.__commands['scale-factor'] = ''
                    else:
                        self.scaleFactorSpin.setEnabled(True)
                        self.check(self.scaleFactorSpin)
                else:
                    self.analysisSaveReuseLevelSpin.setDisabled(True)
                    self.analysisLoadLine.setEnabled(True)

                    self.__commands['analysis-save-reuse-level'] = ''
                    self.check(self.analysisLoadLine)
                    if self.analysisLoadLine.text():
                        self.multiPassOptDistortionCheckBox.setDisabled(True)
                        self.multiPassOptAnalysisCheckBox.setDisabled(True)
                        self.analysisLoadReuseLevelSpin.setEnabled(True)
                        self.__commands['multi-pass-opt-analysis'] = ''
                        self.__commands['multi-pass-opt-distortion'] = ''
                        if 7 <= self.analysisLoadReuseLevelSpin.value() <= 9:
                            self.scaleFactorSpin.setDisabled(True)
                            self.__commands['scale-factor'] = ''
                        else:
                            self.scaleFactorSpin.setEnabled(True)
                            self.check(self.scaleFactorSpin)

                        self.check(self.analysisLoadReuseLevelSpin)
                    else:
                        if self.__commands['pass'] != '':
                            self.multiPassOptDistortionCheckBox.setEnabled(True)
                            self.multiPassOptAnalysisCheckBox.setEnabled(True)
                            self.check(self.multiPassOptDistortionCheckBox, self.multiPassOptAnalysisCheckBox)
                        self.refineCtuDistortionSpin.setDisabled(True)
                        self.__commands['refine-ctu-distortion'] = ''
                        if self.poolsLine.text() != 'none':
                            self.pmodeCheckBox.setEnabled(True)
                            self.scaleFactorSpin.setDisabled(True)
                            self.__commands['scale-factor'] = ''
                            self.check(self.pmodeCheckBox)
                self.check(sender)
            elif sender == self.analysisLoadLine:
                if value:
                    self.analysisSaveLine.setDisabled(True)
                    self.analysisSaveReuseLevelSpin.setDisabled(True)
                    self.pmodeCheckBox.setDisabled(True)
                    self.analysisLoadReuseLevelSpin.setEnabled(True)
                    self.refineCtuDistortionSpin.setEnabled(True)
                    self.multiPassOptAnalysisCheckBox.setDisabled(True)
                    self.multiPassOptDistortionCheckBox.setDisabled(True)
                    self.analysisReuseFileLine.setDisabled(True)
                    self.__commands['analysis-save'] = ''
                    self.__commands['analysis-save-reuse-level'] = ''
                    self.__commands['pmode'] = ''
                    self.__commands['multi-pass-opt-analysis'] = ''
                    self.__commands['multi-pass-opt-distortion'] = ''
                    self.__commands['analysis-reuse-file'] = ''
                    self.check(self.analysisLoadReuseLevelSpin, self.refineCtuDistortionSpin)
                    if 7 <= self.analysisLoadReuseLevelSpin.value() <= 9:
                        self.scaleFactorSpin.setDisabled(True)
                        self.__commands['scale-factor'] = ''
                    else:
                        self.scaleFactorSpin.setEnabled(True)
                        self.check(self.scaleFactorSpin)
                else:
                    self.analysisLoadReuseLevelSpin.setDisabled(True)
                    self.analysisSaveLine.setEnabled(True)
                    self.__commands['analysis-load-reuse-level'] = ''
                    self.check(self.analysisSaveLine)
                    if self.analysisSaveLine.text():
                        self.analysisSaveReuseLevelSpin.setEnabled(True)
                        self.scaleFactorSpin.setEnabled(True)
                        self.multiPassOptAnalysisCheckBox.setDisabled(True)
                        self.multiPassOptDistortionCheckBox.setDisabled(True)
                        self.analysisReuseFileLine.setDisabled(True)

                        self.__commands['multi-pass-opt-analysis'] = ''
                        self.__commands['multi-pass-opt-distortion'] = ''
                        self.__commands['analysis-reuse-file'] = ''
                        self.check(self.analysisSaveReuseLevelSpin)
                        if 7 <= self.analysisSaveReuseLevelSpin.value() <= 9:
                            self.scaleFactorSpin.setDisabled(True)
                            self.__commands['scale-factor'] = ''
                        else:
                            self.scaleFactorSpin.setEnabled(True)
                            self.check(self.scaleFactorSpin)
                    else:
                        if self.__commands['pass'] != '':
                            self.multiPassOptDistortionCheckBox.setEnabled(True)
                            self.multiPassOptAnalysisCheckBox.setEnabled(True)
                            self.check(self.multiPassOptDistortionCheckBox, self.multiPassOptAnalysisCheckBox)
                        self.analysisReuseFileLine.setDisabled(True)
                        self.refineCtuDistortionSpin.setDisabled(True)
                        self.__commands['refine-ctu-distortion'] = ''
                        if self.poolsLine.text() != 'none':
                            self.pmodeCheckBox.setEnabled(True)
                            self.scaleFactorSpin.setDisabled(True)
                            self.__commands['scale-factor'] = ''
                            self.check(self.pmodeCheckBox)
                self.check(sender)
            else:
                self.check(sender)

        elif type(sender) == CommandLineEdit:  # LineEdit
            pal = QPalette()
            if self.currentDefault[obj_name] != value:
                pal.setColor(QPalette.ColorRole.Text, QColor(255, 0, 0))
            else:
                pal.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            sender.setPalette(pal)
            if sender == self.customLine:
                self.__commands['custom'] = f'{value}' if value else ''
            elif sender == self.poolsLine:
                pool = False if value == 'none' else True
                for i in (
                        self.lookaheadSlicesSpin,
                        self.pmeCheckBox,
                        self.wppCheckBox):
                    if pool:
                        i.setEnabled(True)
                        self.check(i)
                    else:
                        i.setDisabled(True)
                        self.__commands[i.objectName()] = ''
                if not pool:
                    self.pmodeCheckBox.setDisabled(True)
                    self.__commands['pmode'] = ''
                elif self.analysisLoadLine.text() or self.analysisSaveLine.text():
                    self.pmodeCheckBox.setDisabled(True)
                    self.__commands['pmode'] = ''
                else:
                    self.pmodeCheckBox.setEnabled(True)
                    self.check(self.pmodeCheckBox)
                self.check(sender)

            else:
                self.check(sender)

        elif type(sender) == CommandComboBox:  # ComboBox
            if sender == self.tuneComboBox:
                self.tune()
            elif sender == self.encodeModeComboBox:
                self.slowFirstpassCheckBox.setDisabled(True)
                self.__commands['slow-firstpass'] = ''
                if value == 3:
                    self.__commands['lossless'] = '--lossless'
                    self.crfSpin.setDisabled(True)
                    self.bitrateSpin.setDisabled(True)
                    self.passSpin.setEnabled(True)
                    self.qpSpin.setDisabled(True)
                    self.__commands['cu-lossless'] = ''
                    self.__commands['bitrate'] = ''
                    self.__commands['qp'] = ''
                    self.__commands['crf'] = ''
                    self.cuLosslessCheckBox.setDisabled(True)
                    self.command_change(self.passSpin.value(), widget=self.passSpin)
                else:
                    self.__commands['lossless'] = ''
                    if self.rdSpin.value() >= 3:
                        self.cuLosslessCheckBox.setEnabled(True)
                        self.check(self.cuLosslessCheckBox)
                    if value == 0:
                        self.__commands['pass'] = ''
                        self.__commands['bitrate'] = ''
                        self.__commands['qp'] = ''
                        self.crfSpin.setEnabled(True)
                        self.bitrateSpin.setDisabled(True)
                        self.passSpin.setDisabled(True)
                        self.qpSpin.setDisabled(True)
                        self.check(self.crfSpin)
                    elif value == 1:
                        self.__commands['crf'] = ''
                        self.__commands['qp'] = ''
                        self.crfSpin.setDisabled(True)
                        self.bitrateSpin.setEnabled(True)
                        self.passSpin.setEnabled(True)
                        self.qpSpin.setDisabled(True)
                        self.__commands['bitrate'] = f'--bitrate {self.bitrateSpin.value()}'
                        self.command_change(self.passSpin.value(), widget=self.passSpin)
                    elif value == 2:
                        self.__commands['pass'] = ''
                        self.__commands['bitrate'] = ''
                        self.__commands['crf'] = ''
                        self.crfSpin.setDisabled(True)
                        self.bitrateSpin.setDisabled(True)
                        self.passSpin.setDisabled(True)
                        self.qpSpin.setEnabled(True)
                        self.__commands['qp'] = f'--qp {self.qpSpin.value()}'
                        self.command_change(self.passSpin.value(), widget=self.passSpin)
            elif sender == self.outputDepthComboBox:
                self.profile(value)
                self.check(sender)
            elif sender == self.levelComboBox:
                if value in range(0, 6):
                    self.highTierCheckBox.setDisabled(True)
                    self.__commands['high-tier'] = ''
                else:
                    self.highTierCheckBox.setEnabled(True)
                    self.check(self.highTierCheckBox)
                self.check(sender)
            elif sender == self.asmComboBox:
                if value == 0:
                    self.__commands[obj_name] = ''
                elif value == 14:
                    self.__commands[obj_name] = '--no-asm'
                else:
                    self.__commands[obj_name] = f'--asm {sender.currentText()}'
            elif sender == self.ctuComboBox:
                text = sender.currentText()
                ctu = int(text)
                if ctu == 16:
                    self.minCUComboBox.view().setRowHidden(0, True)
                else:
                    self.minCUComboBox.view().setRowHidden(0, False)
                if self.__commands['min-cu-size'] == '':
                    self.to_default(self.minCUComboBox)
                min_cu = int(self.minCUComboBox.currentText())
                is_default = True if self.__commands['qg-size'] == '' else False
                for row in range(self.qgSizeComboBox.count()):
                    if ctu >= int(self.qgSizeComboBox.itemText(row)) >= min_cu:
                        self.qgSizeComboBox.view().setRowHidden(row, False)
                    else:
                        self.qgSizeComboBox.view().setRowHidden(row, True)
                self.currentDefault[self.qgSizeComboBox.objectName()] = self.ctuComboBox.currentIndex()
                if is_default or ctu == int(self.qgSizeComboBox.currentText()):
                    self.to_default(self.qgSizeComboBox)
                self.check(sender, self.minCUComboBox, self.qgSizeComboBox)
            elif sender == self.minCUComboBox:
                text = sender.currentText()
                min_cu = int(text)
                if min_cu == 32:
                    self.ctuComboBox.view().setRowHidden(2, True)
                else:
                    self.ctuComboBox.view().setRowHidden(2, False)
                is_default = True if self.__commands['qg-size'] == '' else False
                ctu = int(self.ctuComboBox.currentText())
                for row in range(self.qgSizeComboBox.count()):
                    if ctu >= int(self.qgSizeComboBox.itemText(row)) >= min_cu:
                        self.qgSizeComboBox.view().setRowHidden(row, False)
                    else:
                        self.qgSizeComboBox.view().setRowHidden(row, True)
                if is_default:
                    self.to_default(self.qgSizeComboBox)
                self.check(sender)
            elif sender == self.sarComboBox:
                self.__commands['sar'] = f'--sar {value}' if value else ''
            elif sender == self.fpsComboBox:
                self.__commands['fps'] = f'--fps {value}' if value else ''
            elif sender == self.logLevelComboBox:
                self.__commands['log-level'] = '' if value == 3 else f'--log-level {value - 1}'
            elif sender == self.csvLogLevelComboBox:
                self.__commands['csv-log-level'] = f'--csv-log-level {value}' if value else ''
            elif sender == self.hashComboBox:
                self.__commands['hash'] = f'--hash {sender.currentIndex()}' if sender.currentIndex() else ''
            else:
                self.check(sender)
            if type(self.currentDefault[obj_name]) == str:
                equal = sender.currentText() == self.currentDefault[obj_name]
            else:
                equal = self.currentDefault[obj_name] == value
            pal = QPalette()
            if equal:
                pal.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            else:
                pal.setColor(QPalette.ColorRole.Text, QColor(255, 0, 0))
            sender.setPalette(pal)
        self.refresh_command()

    def pools(self):
        if self.lookaheadSlicesSpin.value() in range(2) and \
                not self.wppCheckBox.isChecked() and \
                not self.pmodeCheckBox.isChecked() and \
                not self.pmeCheckBox.isChecked():
            self.poolsLine.setDisabled(True)
            self.__commands['pools'] = ''
        else:
            self.poolsLine.setEnabled(True)
            self.check(self.poolsLine)

    def profile(self, value: int):
        profile = self.profileComboBox.currentIndex()
        hide_rows = set()
        if self.framesSpin.value() != 1:
            hide_rows |= {3, 6}
        if self.keyintSpin.value() in range(2) or self.framesSpin.value() == 1:
            hide_rows |= {1, 4, 7, 9, 11, 13, 15, 17}
        if value == 1:
            hide_rows |= set(range(7, 19))
        elif value == 2:
            hide_rows |= set(range(1, 7))
            hide_rows |= set(range(13, 19))
        elif value == 3:
            hide_rows |= set(range(1, 13))
        for row in range(self.profileComboBox.count()):
            if row in hide_rows:
                self.profileComboBox.view().setRowHidden(row, True)
            else:
                self.profileComboBox.view().setRowHidden(row, False)
        if profile in hide_rows:
            self.profileComboBox.setCurrentIndex(0)

    def custom(self):
        document = self.customLine.document()
        commands = []
        for i in range(document.blockCount()):
            block = document.findBlockByNumber(i)
            text = block.text().strip()
            commands.append(text)
        self.__commands['custom'] = ' '.join(commands)
        self.refresh_command()

    def reset(self):
        for i in self.allItems.values():
            i.setEnabled(True)
        self.presetSlider.setValue(5)
        for n in range(self.profileComboBox.count()):
            if n in (3, 6):
                self.profileComboBox.view().setRowHidden(n, True)
            else:
                self.profileComboBox.view().setRowHidden(n, False)
        if self.profileComboBox.currentIndex() in (3, 6):
            self.profileComboBox.setCurrentIndex(0)
        self.highTierCheckBox.setDisabled(True)
        self.rdRefineCheckBox.setDisabled(True)
        self.psyRdoqSpin.setDisabled(True)
        self.bitrateSpin.setDisabled(True)
        self.qpSpin.setDisabled(True)
        self.passSpin.setDisabled(True)
        self.statsLine.setDisabled(True)
        self.multiPassOptAnalysisCheckBox.setDisabled(True)
        self.multiPassOptDistortionCheckBox.setDisabled(True)
        self.hrdCheckBox.setDisabled(True)
        self.slowFirstpassCheckBox.setDisabled(True)
        self.scenecutAwareQpSpin.setDisabled(True)
        self.maskingStrengthLine.setDisabled(True)
        self.vbvLiveMultiPassCheckBox.setDisabled(True)
        self.rskipEdgeThresholdSpinBox.setDisabled(True)
        self.scaleFactorSpin.setDisabled(True)
        self.analysisLoadReuseLevelSpin.setDisabled(True)
        self.analysisSaveReuseLevelSpin.setDisabled(True)
        self.analysisReuseFileLine.setDisabled(True)
        self.refineCtuDistortionSpin.setDisabled(True)
        self.vuiHrdInfoCheckBox.setDisabled(True)
        if SETTINGS.svt == 0:
            self.svtCheckBox.setDisabled(True)
        self.svtHmeCheckBox.setDisabled(True)
        self.svtSearchWidthSpin.setDisabled(True)
        self.svtSearchHeightSpin.setDisabled(True)
        self.svtCompressedTenBitFormatCheckBox.setDisabled(True)
        self.svtSpeedControlCheckBox.setDisabled(True)
        self.svtPresetTunerSpin.setDisabled(True)
        self.svtHierarchicalLevelSpin.setDisabled(True)
        self.svtBaseLayerSwitchModeSpin.setDisabled(True)
        self.svtPredStructSpin.setDisabled(True)
        self.svtFpsInVpsCheckBox.setDisabled(True)

        self.customLine.clear()

        for lineEdit in (self.commandLines + self.pathLines):
            lineEdit.setText(DEFAULT[lineEdit.objectName()])
        pal = QPalette()

        for comboBox in self.comboBoxes:
            value = DEFAULT[comboBox.objectName()]
            if type(value) == int:
                comboBox.setCurrentIndex(value)
            elif comboBox.lineEdit():
                comboBox.setCurrentText(value)
            pal.setColor(QPalette.ColorRole.ButtonText, QColor(0, 0, 0))
            comboBox.setPalette(pal)
        for checkBox in self.checkBoxes:
            checkBox.setChecked(DEFAULT[checkBox.objectName()])
            pal.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            checkBox.setPalette(pal)
        for spinBox in (self.spins + self.doubleSpins):
            spinBox.setValue(DEFAULT[spinBox.objectName()])
            pal.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            spinBox.lineEdit().setPalette(pal)
        self.__commands.reset()
        self.currentDefault.update(DEFAULT.copy())
        self.refresh_command()

    def to_default(self, item):
        value = self.currentDefault.get(item.objectName())
        if type(item) == CommandComboBox:
            if type(value) == int:
                item.setCurrentIndex(value)
            elif item.lineEdit():
                item.setCurrentText(value)
            else:
                QMessageBox.warning(
                    self,
                    LANG_UI_TXT.info.error,
                    f'{item.objectName()}: {type(value)} {value}',
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
            pal = QPalette()
            pal.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            item.setPalette(pal)
        elif type(item) == QCheckBox:
            pal = QPalette()
            pal.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
            item.setPalette(pal)
            item.setChecked(value)
        elif type(item) in (QSpinBox, QDoubleSpinBox):
            pal = QPalette()
            pal.setColor(QPalette.ColorRole.Text, QColor(0, 0, 0))
            item.lineEdit().setPalette(pal)
            item.setValue(value)
        else:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                item.objectName(),
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)

    def preset(self, index: int):
        self.presetLabel.setText(self.__presets[index])
        pal = QPalette()
        if self.presetSlider.value() == 5:
            pal.setColor(QPalette.ColorRole.WindowText, QColor(0, 0, 0))
        else:
            pal.setColor(QPalette.ColorRole.WindowText, QColor(255, 0, 0))
        self.presetLabel.setPalette(pal)
        self.__commands['preset'] = '' if index == 5 else f'--preset {self.__presets[index]}'
        self.currentDefault[self.ctuComboBox.objectName()] = self.ctu[index]
        self.currentDefault[self.minCUComboBox.objectName()] = self.min_cu_size[index]
        self.currentDefault[self.bframesSpin.objectName()] = self.bframes[index]
        self.currentDefault[self.bAdaptSpin.objectName()] = self.b_adapt[index]
        self.currentDefault[self.rcLookaheadSpin.objectName()] = self.rc_lookahead[index]
        self.currentDefault[self.lookaheadSlicesSpin.objectName()] = self.lookahead_slices[index]
        self.currentDefault[self.scenecutSpin.objectName()] = self.scenecut[index]
        self.currentDefault[self.refSpin.objectName()] = self.ref[index]
        self.currentDefault[self.limitRefsSpin.objectName()] = self.limit_refs[index]
        self.currentDefault[self.meComboBox.objectName()] = self.me[index]
        self.currentDefault[self.merangeSpin.objectName()] = self.merange[index]
        self.currentDefault[self.submeSpin.objectName()] = self.subme[index]
        self.currentDefault[self.rectCheckBox.objectName()] = self.rect[index]
        self.currentDefault[self.ampCheckBox.objectName()] = self.amp[index]
        self.currentDefault[self.limitModesCheckBox.objectName()] = self.limit_modes[index]
        self.currentDefault[self.maxMergeSpin.objectName()] = self.max_merge[index]
        self.currentDefault[self.earlySkipCheckBox.objectName()] = self.early_skip[index]
        self.currentDefault[self.rskipSpinBox.objectName()] = self.rskip[index]
        self.currentDefault[self.fastIntraCheckBox.objectName()] = self.fast_intra[index]
        self.currentDefault[self.bIntraCheckBox.objectName()] = self.b_intra[index]
        self.currentDefault[self.saoCheckBox.objectName()] = self.sao[index]
        self.currentDefault[self.signhideCheckBox.objectName()] = self.signhide[index]
        self.currentDefault[self.weightpCheckBox.objectName()] = self.weightp[index]
        self.currentDefault[self.weightbCheckBox.objectName()] = self.weightb[index]
        self.currentDefault[self.aqModeSpin.objectName()] = self.aq_mode[index]
        self.currentDefault[self.rdSpin.objectName()] = self.rdLevel[index]
        self.currentDefault[self.rdoqLevelSpin.objectName()] = self.rdoq_level[index]
        self.currentDefault[self.tuIntraDepthSpin.objectName()] = self.tu_intra[index]
        self.currentDefault[self.tuInterDepthSpin.objectName()] = self.tu_inter[index]
        self.currentDefault[self.limitTuSpin.objectName()] = self.limit_tu[index]
        for i in (
                self.ctuComboBox,
                self.minCUComboBox,
                self.bframesSpin,
                self.bAdaptSpin,
                self.rcLookaheadSpin,
                self.lookaheadSlicesSpin,
                self.scenecutSpin,
                self.refSpin,
                self.limitRefsSpin,
                self.meComboBox,
                self.merangeSpin,
                self.submeSpin,
                self.rectCheckBox,
                self.ampCheckBox,
                self.limitModesCheckBox,
                self.maxMergeSpin,
                self.earlySkipCheckBox,
                self.rskipSpinBox,
                self.fastIntraCheckBox,
                self.bIntraCheckBox,
                self.saoCheckBox,
                self.signhideCheckBox,
                self.weightpCheckBox,
                self.weightbCheckBox,
                self.aqModeSpin,
                self.rdSpin,
                self.rdoqLevelSpin,
                self.tuIntraDepthSpin,
                self.tuInterDepthSpin,
                self.limitTuSpin):
            if self.__commands[i.objectName()] == '':
                self.to_default(i)
            self.check(i)
        self.tune()
        self.refresh_command()

    def tune(self):
        index = self.tuneComboBox.currentIndex()
        self.__commands['tune'] = f'--tune {self.tunes[index - 1]}' if index else ''
        preset = self.presetSlider.value()
        self.currentDefault[self.bAdaptSpin.objectName()] = self.b_adapt[preset]
        self.currentDefault[self.aqModeSpin.objectName()] = self.aq_mode[preset]
        self.currentDefault[self.cutreeCheckBox.objectName()] = True
        self.currentDefault[self.ipratioSpin.objectName()] = 1.4
        self.currentDefault[self.pbratioSpin.objectName()] = 1.3
        self.currentDefault[self.qpstepSpin.objectName()] = 4
        self.currentDefault[self.saoCheckBox.objectName()] = self.sao[preset]
        self.currentDefault[self.psyRdSpin.objectName()] = 2
        self.currentDefault[self.bframesSpin.objectName()] = self.bframes[preset]
        self.currentDefault[self.rcLookaheadSpin.objectName()] = self.rc_lookahead[preset]
        self.currentDefault[self.psyRdoqSpin.objectName()] = 1
        self.currentDefault[self.scenecutSpin.objectName()] = self.scenecut[preset]
        self.currentDefault[self.rskipSpinBox.objectName()] = self.rskip[preset]
        self.currentDefault[self.deblockCheckBox.objectName()] = True
        self.currentDefault[self.weightpCheckBox.objectName()] = self.weightp[preset]
        self.currentDefault[self.weightbCheckBox.objectName()] = self.weightb[preset]
        self.currentDefault[self.bIntraCheckBox.objectName()] = self.b_intra[preset]
        self.currentDefault[self.frameThreadsSpin.objectName()] = 0
        self.rcGrainCheckBox.setChecked(False)
        self.currentDefault[self.aqStrengthSpin.objectName()] = 1
        self.currentDefault[self.deblockSpin1.objectName()] = 0
        self.currentDefault[self.deblockSpin2.objectName()] = 0
        if index == 1:
            self.currentDefault[self.aqModeSpin.objectName()] = 0
            self.currentDefault[self.psyRdSpin.objectName()] = 0
            self.currentDefault[self.cutreeCheckBox.objectName()] = False
        elif index == 2:
            self.currentDefault[self.aqModeSpin.objectName()] = 2
            self.currentDefault[self.psyRdSpin.objectName()] = 0
        elif index == 3:
            self.currentDefault[self.aqModeSpin.objectName()] = 0
            self.currentDefault[self.cutreeCheckBox.objectName()] = False
            self.currentDefault[self.ipratioSpin.objectName()] = 1.1
            self.currentDefault[self.pbratioSpin.objectName()] = 1.0
            self.currentDefault[self.qpstepSpin.objectName()] = 1
            self.currentDefault[self.saoCheckBox.objectName()] = False
            self.currentDefault[self.psyRdoqSpin.objectName()] = 10
            self.currentDefault[self.psyRdSpin.objectName()] = 4
            self.currentDefault[self.rskipSpinBox.objectName()] = 0
            self.rcGrainCheckBox.setChecked(True)
        elif index == 4:
            self.currentDefault[self.bframesSpin.objectName()] = 0
            self.currentDefault[self.bAdaptSpin.objectName()] = 0
            self.currentDefault[self.rcLookaheadSpin.objectName()] = 0
            self.currentDefault[self.scenecutSpin.objectName()] = 0
            self.currentDefault[self.cutreeCheckBox.objectName()] = False
            self.currentDefault[self.frameThreadsSpin.objectName()] = 1
        elif index == 5:
            self.currentDefault[self.deblockCheckBox.objectName()] = False
            self.currentDefault[self.saoCheckBox.objectName()] = False
            self.currentDefault[self.weightpCheckBox.objectName()] = False
            self.currentDefault[self.weightbCheckBox.objectName()] = False
            self.currentDefault[self.bIntraCheckBox.objectName()] = False
        elif index == 6:
            self.currentDefault[self.psyRdSpin.objectName()] = 0.4
            self.currentDefault[self.aqStrengthSpin.objectName()] = 0.4
            self.currentDefault[self.deblockCheckBox.objectName()] = 0.4
            self.currentDefault[self.deblockSpin1.objectName()] = 1
            self.currentDefault[self.deblockSpin2.objectName()] = 1
            self.currentDefault[self.bframesSpin.objectName()] = 6
        for i in (
                self.aqModeSpin,
                self.psyRdSpin,
                self.cutreeCheckBox,
                self.ipratioSpin,
                self.pbratioSpin,
                self.qpstepSpin,
                self.saoCheckBox,
                self.psyRdoqSpin,
                self.rskipSpinBox,
                self.bframesSpin,
                self.deblockCheckBox,
                self.weightpCheckBox,
                self.weightbCheckBox,
                self.bAdaptSpin,
                self.bIntraCheckBox,
                self.frameThreadsSpin,
                self.scenecutSpin,
                self.aqStrengthSpin,
                self.rcLookaheadSpin):
            if self.__commands[i.objectName()] == '':
                self.to_default(i)
            self.check(i)
        self.refresh_command()

    def check(self, *args):
        for obj in args:
            obj_name = obj.objectName()
            default = self.currentDefault.get(obj_name)
            if (objType := type(obj)) == CommandComboBox:
                value = obj.currentIndex() if type(default) == int else obj.currentText()
                self.__commands[obj_name] = '' if value == default else f'--{obj_name} {obj.currentText()}'
            elif objType == QCheckBox:
                if obj.isChecked() == default:
                    self.__commands[obj_name] = ''
                elif obj.isChecked():
                    self.__commands[obj_name] = f'--{obj_name}'
                else:
                    self.__commands[obj_name] = f'--no-{obj_name}'
            elif objType == QSpinBox:
                self.__commands[obj_name] = '' if default == obj.value() else f'--{obj_name} {obj.value()}'
            elif objType == QDoubleSpinBox:
                self.__commands[
                    obj_name] = '' if default == obj.value() else f'--{obj_name} {round(obj.value(), obj.decimals())}'
            elif objType == PathLineEdit:
                self.__commands[obj_name] = f'--{obj_name} "{obj.text()}"' if \
                    obj.text() and self.currentDefault[obj.objectName()] != obj.text() else ''
            elif objType == CommandLineEdit:
                self.__commands[obj_name] = f'--{obj_name} {obj.text()}' if \
                    obj.text() and self.currentDefault[obj.objectName()] != obj.text() else ''
            else:
                print(f'check type error: {objType}')

    def refresh_command(self):
        self.commandPlainTextEdit.setPlainText(str(self.__commands))

    def save_state_change(self):
        self.saveButton.setEnabled(True)
        self.saveAsButton.setEnabled(True)
        self.closeButton.setEnabled(True)
        self.winTitleChange = '*'
        self.title_change()

    def open(self, files: tuple):
        if self.winTitleChange:
            answer = QMessageBox.question(
                self,
                LANG_UI_TXT.info.not_saved,
                LANG_UI_TXT.info.save_ask,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes)
            if answer == QMessageBox.StandardButton.Yes:
                self.saveButton.click()
                if not self.saveSuccess:
                    return None
            elif answer == QMessageBox.StandardButton.Cancel:
                return None

        self.open_file(files[0])

    def open_file(self, file_path: str):
        file = QFileInfo(file_path)
        if file.suffix().lower() == 'json':
            if file.isReadable():
                with open(file_path, 'r', encoding='utf-8') as f:
                    try:
                        data = json.load(f)
                        if len(data) == 3:
                            data, code, version = data
                            data: dict[str, list[..., bool]]
                            code: str
                            version: str
                            if not type(data) == dict:
                                raise TypeError('数据必须是字典')
                            if not type(code) == str:
                                raise TypeError('代码必须是字符')
                            if not type(version) == str:
                                raise TypeError('版本必须是字符')
                        else:
                            raise ValueError('json必须包含数据，命令以及版本')
                    except (json.JSONDecodeError, UnicodeDecodeError, EOFError):
                        QMessageBox.warning(
                            self,
                            LANG_UI_TXT.info.error,
                            LANG_UI_TXT.info.file_invalid,
                            QMessageBox.StandardButton.Ok,
                            QMessageBox.StandardButton.Ok)
                        SETTINGS.recentSavFile = ''
                    except (TypeError, ValueError) as e:
                        QMessageBox.warning(
                            self,
                            LANG_UI_TXT.info.error,
                            str(e),
                            QMessageBox.StandardButton.Ok,
                            QMessageBox.StandardButton.Ok)
                        SETTINGS.recentSavFile = ''
                    else:
                        if 'hdr' in data:
                            data['hdr10'] = data.pop('hdr')
                        if 'hdr-opt' in data:
                            data['hdr10-opt'] = data.pop('hdr-opt')
                        if custom := data.get('custom'):
                            if type(custom[0]) in (list, tuple):
                                data['custom'][0] = '\n'.join(custom[0])
                        commands = {key: value[0] for key, value in data.items()}

                        lacks = []
                        errors = []
                        preset = data.get('preset', (None, True))[0]
                        self.reset()
                        if preset is not None:
                            if self.presetSlider.maximum() >= preset >= self.presetSlider.minimum():
                                self.presetSlider.setValue(preset)
                            else:
                                errors.append('preset')
                        else:
                            lacks.append('preset')
                        for obj_name, i in self.allItems.items():
                            value, enable = data.pop(obj_name, [None, True])
                            if value is None:
                                lacks.append(obj_name)
                            else:
                                if type(i) == CommandComboBox:
                                    if type(value) == int:
                                        if value in range(i.count()):
                                            i.setCurrentIndex(value)
                                        else:
                                            errors.append(obj_name)
                                    elif type(value) == str:
                                        if i.lineEdit():
                                            i.setCurrentText(value)
                                        else:
                                            errors.append(obj_name)
                                    else:
                                        errors.append(obj_name)
                                elif type(i) in (CommandLineEdit, PathLineEdit):
                                    if type(value) == str:
                                        i.setText(value)
                                    else:
                                        errors.append(obj_name)
                                elif type(i) == QCheckBox:
                                    if type(value) == bool:
                                        i.setChecked(value)
                                    else:
                                        errors.append(obj_name)
                                elif type(i) in (QDoubleSpinBox, QSpinBox):
                                    if type(value) in (int, float):
                                        if i.maximum() >= value >= i.minimum():
                                            i.setValue(value)
                                        else:
                                            errors.append(obj_name)
                                    else:
                                        if i == self.rskipSpinBox:
                                            if value is True:
                                                self.rskipSpinBox.setValue(1)
                                            elif value is False:
                                                self.rskipSpinBox.setValue(0)
                                            else:
                                                errors.append(obj_name)
                                        else:
                                            errors.append(obj_name)
                                elif type(i) == QPlainTextEdit:
                                    if type(value) == str:
                                        i.setPlainText(value)
                                    elif type(value) in (list, tuple):
                                        for line in value:
                                            if type(line) == str:
                                                i.appendPlainText(line)
                                    else:
                                        errors.append(obj_name)
                                elif i == self.presetSlider:
                                    continue
                                if type(enable) == bool:
                                    i.setEnabled(enable)
                                    if not enable and obj_name in self.__commands:
                                        self.__commands[obj_name] = ''
                                else:
                                    errors.append(value)

                        if version != SAVE_VERSION:
                            QMessageBox.warning(
                                self,
                                LANG_UI_TXT.info.error,
                                LANG_UI_TXT.info.version_different,
                                QMessageBox.StandardButton.Ok,
                                QMessageBox.StandardButton.Ok)
                        if str(COMMANDS) != code:
                            QMessageBox.warning(
                                self,
                                LANG_UI_TXT.info.error,
                                LANG_UI_TXT.info.commands,
                                QMessageBox.StandardButton.Ok,
                                QMessageBox.StandardButton.Ok)
                            with open('Error.txt', 'a', errors='ignore') as error_file:
                                error_file.write(
                                    f'\n\n{get_time()}====================================================\n'
                                    '错误类型：存档与程序下方生成的参数不符\n'
                                    f'存档路径：{file_path}\n存档版本：{version}\n'
                                    f'应用程序版本：{SAVE_VERSION}\n\n')
                                for command, new in self.__commands.items():
                                    if item := self.allItems.get(command):
                                        if type(item) == CommandComboBox:
                                            if item.lineEdit():
                                                new = item.currentText()
                                            else:
                                                new = item.currentIndex()
                                        elif type(item) in (CommandLineEdit, PathLineEdit):
                                            new = item.text()
                                        elif type(item) == QCheckBox:
                                            new = item.isChecked()
                                        elif type(item) in (QDoubleSpinBox, QSpinBox):
                                            new = item.value()
                                        elif type(item) == QPlainTextEdit:
                                            new = item.toPlainText()
                                        elif item == self.presetSlider:
                                            new = self.presetSlider.value()
                                    elif command in ('input-res', 'hme-search', 'hme-range', 'lossless',
                                                     'display-window'):
                                        continue
                                    old = commands.get(command, '无')
                                    if old != new:
                                        error_file.write(f'参数：{command}\n存档：{old}\n程序内：{new}\n\n')

                        if SETTINGS.svt != 0:
                            self.svtCheckBox.setEnabled(True)
                        else:
                            self.svtCheckBox.setChecked(False)
                            self.svtCheckBox.setDisabled(True)
                        self.winTitleFile = file_path
                        self.versionLabel.setText(f'(ver:{version})')
                        self.winTitleChange = ''
                        self.saveButton.setDisabled(True)
                        self.title_change()
                        self.closeButton.setEnabled(True)
                        self.commandPlainTextEdit.textChanged.connect(self.save_state_change)
                        SETTINGS.recentSavFile = file_path
                        if lacks or errors:
                            warning = f'{LANG_UI_TXT.info.lack_command}\n{"，".join(lacks)}\n' \
                                      f'{LANG_UI_TXT.info.error}: \n{"，".join(errors)}'
                            QMessageBox.warning(
                                self,
                                LANG_UI_TXT.info.error,
                                warning,
                                QMessageBox.StandardButton.Ok,
                                QMessageBox.StandardButton.Ok)
                        if data:
                            warning = f'{LANG_UI_TXT.info.command_redundant}\n{"，".join(data)}'
                            QMessageBox.warning(
                                self,
                                LANG_UI_TXT.info.error,
                                warning,
                                QMessageBox.StandardButton.Ok,
                                QMessageBox.StandardButton.Ok)
            else:
                QMessageBox.warning(
                    self,
                    LANG_UI_TXT.info.error,
                    LANG_UI_TXT.info.permission,
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)
        else:
            mi = pymediainfo.MediaInfo.parse(file_path,
                                             library_file=MEDIAINFO.absoluteFilePath(),
                                             full=False,
                                             parse_speed=SETTINGS.parseSpeed).to_data().get(
                'tracks', [])
            valid_tracks = []
            for n, track in enumerate(mi):
                encoder = track.get('format', None)
                if track.get('track_type') == 'Video' and encoder == 'HEVC':
                    if track.get('encoding_settings'):
                        valid_tracks.append(n)
            if valid_tracks:
                num = valid_tracks[0]
                if len(valid_tracks) > 1:
                    for num in valid_tracks:
                        r = QMessageBox.question(self,
                                                 '视频轨过多',
                                                 f'合适的视频轨数量大于1，是否选择第{num}个轨道？',
                                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                        if r == QMessageBox.StandardButton.Yes:
                            break
                    else:
                        num = valid_tracks[0]
                        QMessageBox.information(self,
                                                '未选择',
                                                f'已自动选择合适的第1条轨道',
                                                QMessageBox.StandardButton.Ok)
                setting = mi[num].get('encoding_settings', None)
                settings = [i.strip() for i in setting.split('/')]
                SETTINGS.recentSavFile = file_path
                self.reset()

                '''
                    lack = []

                    for i in settings:
                        skip = True
                        if '=' in i:
                            command, value = i.split('=')
                            if command == 'scenecut-bias':
                                value = float(value) * 100
                                self.check_item(command, value)
                            elif command == 'rc':
                                command = self.encodeModeComboBox
                                value = value.upper()
                                self.check_item(command, value)
                            elif command == 'max-keyint':
                                self.check_item(self.keyintSpin, value)
                            elif command == 'max-cu-size':
                                self.check_item(self.ctuComboBox, value)
                            elif command == 'input-res':
                                width, height = value.split('x')
                                self.check_item(self.inputResWidthSpin, width)
                                self.check_item(self.inputResHeightSpin, height)
                            elif command == 'deblock':
                                if ':' in value and value.count(':') == 1:
                                    self.deblockCheckBox.setChecked(True)
                                    tc, beta = value.split(':')
                                    self.check_item(self.deblockSpin1, tc)
                                    self.check_item(self.deblockSpin2, beta)
                                else:
                                    self.deblockCheckBox.setChecked(False)
                            elif command in ('cpuid', 'analysis-reuse-mode'):
                                pass
                            elif command == 'left':
                                self.check_item(self.displayWindowSpinL, value)
                            elif command == 'top':
                                self.check_item(self.displayWindowSpinT, value)
                            elif command == 'right':
                                self.check_item(self.displayWindowSpinR, value)
                            elif command == 'bottom':
                                self.check_item(self.displayWindowSpinB, value)
                            elif command == 'recursion-skip':
                                self.check_item(self.rskipSpinBox, value)
                            elif command == 'overscan-crop':
                                self.check_item(self.overscanComboBox, int(value))
                            elif command == 'sar':
                                if value in ('0', '1'):
                                    value = '1:1'
                                self.check_item(command, value)
                            elif command in ('stats-write', 'stats-read', 'zone-count', 'display-window',
                                             'chromaloc-top', 'chromaloc-bottom', 'analysis-mode'):
                                pass
                            elif command == 'total-frames':
                                self.check_item(self.framesSpin, value)
                            else:
                                skip = False
                        elif i[:3] == 'no-':
                            command, value = i[3:], False
                            skip = False
                        else:
                            command, value = i, True
                            if command == '-----':
                                pass
                            else:
                                skip = False
                        if not skip:
                            if type(command) == str:
                                if command in self.__commands:
                                    self.check_item(command, value)
                                else:
                                    self.customLine.appendPlainText(f'--{command} {value}')
                                    lack.append(command)
                            else:
                                self.check_item(command, value)
                    if lack:
                        QMessageBox.warning(self, '警告', f'以下参数未能识别：{", ".join(lack)}')
                '''

            else:
                QMessageBox.warning(
                    self,
                    LANG_UI_TXT.info.error,
                    '未找到HEVC视频轨',
                    QMessageBox.StandardButton.Ok,
                    QMessageBox.StandardButton.Ok)

    def check_item(self, command, value):
        if type(command) == str:
            for obj_name, item in self.allItems.items():
                if obj_name == command:
                    break
            else:
                item = None
        else:
            item = command
        if item:
            if type(item) == QCheckBox:
                if value in (True, '1'):
                    item.setChecked(True)
                else:
                    item.setChecked(False)
            elif type(item) == QSpinBox:
                item.setValue(int(float(value)))
            elif type(item) == QDoubleSpinBox:
                item.setValue(float(value))
            elif type(item) == CommandComboBox:
                if type(value) == int:
                    item.setCurrentIndex(value)
                elif item.lineEdit():
                    item.setCurrentText(value)
                else:
                    print(item, command, value)
            elif type(item) == QLineEdit:
                if value != 0:
                    item.setText(value)
            else:
                print(item, command, value)
        else:
            print(command, value)

    def _save(self, file_path: str):
        data = {'preset': (self.presetSlider.value(), self.presetSlider.isEnabled())}
        for i in self.comboBoxes:
            if i.lineEdit():
                data[i.objectName()] = (i.currentText(), i.isEnabled())
            else:
                data[i.objectName()] = (i.currentIndex(), i.isEnabled())
        for i in self.checkBoxes:
            data[i.objectName()] = (i.isChecked(), i.isEnabled())
        for i in (self.commandLines + self.pathLines):
            data[i.objectName()] = (i.text(), i.isEnabled())
        for i in (self.spins + self.doubleSpins):
            data[i.objectName()] = (i.value(), i.isEnabled())

        data['custom'] = (self.customLine.toPlainText(), self.customLine.isEnabled())
        file_data = [data, str(COMMANDS), SAVE_VERSION]
        if QFileInfo(QFileInfo(file_path).absoluteDir().path()).isWritable():
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(file_data, f, ensure_ascii=False, sort_keys=True, indent=4)
            self.commandPlainTextEdit.textChanged.connect(self.save_state_change)

            QMessageBox.information(
                self,
                LANG_UI_TXT.info.success,
                LANG_UI_TXT.info.save_success,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
            return True
        else:
            QMessageBox.warning(
                self,
                LANG_UI_TXT.info.error,
                LANG_UI_TXT.info.permission,
                QMessageBox.StandardButton.Ok,
                QMessageBox.StandardButton.Ok)
            return False

    def save(self, dialog_tuple: tuple):
        if self.winTitleFile:
            path = self.winTitleFile
        else:
            func, filters = dialog_tuple
            path = func(self,
                        LANG_UI_TXT.fileDialog.save,
                        SETTINGS.recentDir,
                        filters)[0]
        if path:
            SETTINGS.recentDir = QFileInfo(path).absoluteDir().path()
            if self._save(path):
                self.saveButton.setDisabled(True)
                self.winTitleFile = path
                self.winTitleChange = ''
                self.title_change()
                self.versionLabel.setText(f'(ver:{SAVE_VERSION})')
                self.closeButton.setEnabled(True)
                self.saveSuccess = True
            else:
                self.saveSuccess = False
        else:
            self.saveSuccess = False

    def save_as(self, files: tuple):
        path = files[0]
        if self._save(path):
            if not self.winTitleFile:
                self.winTitleFile = path
                self.winTitleChange = ''
                self.title_change()
                self.versionLabel.setText(f'(ver:{SAVE_VERSION})')
                self.closeButton.setEnabled(True)
                self.saveSuccess = True
                self.saveButton.setDisabled(True)

    def close_project(self, *, reset_recent: bool = True):
        if self.winTitleChange:
            answer = QMessageBox.question(
                self,
                LANG_UI_TXT.info.not_saved,
                LANG_UI_TXT.info.save_ask,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Yes)
            if answer == QMessageBox.StandardButton.Yes:
                self.saveButton.click()
                if not self.saveSuccess:
                    return None
            elif answer == QMessageBox.StandardButton.Cancel:
                return None

        self.reset()
        self.closeButton.setDisabled(True)
        self.winTitleChange = ''
        self.winTitleFile = ''
        self.title_change()
        self.versionLabel.clear()
        self.saveButton.setDisabled(True)
        self.saveAsButton.setDisabled(True)
        self.commandPlainTextEdit.textChanged.connect(self.save_state_change)
        if reset_recent:
            SETTINGS.recentSavFile = ''

    def copy_code(self):
        self.mainWidget.app.clipboard().setText(str(COMMANDS))
        QMessageBox.information(
            self,
            LANG_UI_TXT.info.success,
            LANG_UI_TXT.info.success,
            QMessageBox.StandardButton.Ok,
            QMessageBox.StandardButton.Ok)

    def title_change(self):
        self.titleLine.setText(f'{self.winTitleChange}{self.winTitleFile}')

    def find_item(self, text: str):
        if text:
            for obj_name, item in self.allItems.items():
                if obj_name == text:
                    parent = item.parent()
                    while parent not in self.widgets:
                        parent = parent.parent()
                    self.tab.setCurrentWidget(parent)
                    if item.isEnabled():
                        if type(item) == CommandComboBox:
                            item.showPopup()
                        elif type(item) in (QLineEdit, QPlainTextEdit):
                            item.selectAll()
                        elif type(item) in (QSpinBox, QDoubleSpinBox):
                            item.selectAll()
                        elif type(item) == QCheckBox:
                            item.setDown(True)
                        item.setFocus()
                    break
            if text == 'lossless':
                self.tab.setCurrentWidget(self.profileWidget)
                self.encodeModeComboBox.showPopup()
                self.encodeModeComboBox.setFocus()
            else:
                print(f'找不到{text}')

    def keyReleaseEvent(self, a0) -> None:
        if a0.modifiers() == Qt.KeyboardModifier.ControlModifier and a0.key() == Qt.Key.Key_S:
            if self.saveButton.isEnabled():
                self.saveButton.click()
        elif a0.modifiers() == Qt.KeyboardModifier.ControlModifier and a0.key() == Qt.Key.Key_Q:
            if self.closeButton.isEnabled():
                self.close_project()
        elif a0.modifiers() == Qt.KeyboardModifier.ControlModifier and a0.key() == Qt.Key.Key_C:
            self.copy_code()
        elif a0.modifiers() == Qt.KeyboardModifier.ControlModifier and a0.key() == Qt.Key.Key_O:
            self.openButton.click()
