from nt import cpu_count

import tools.vapoursynth.vapoursynth as vs

from PySide6.QtCharts import QLineSeries, QChartView, QValueAxis, QScatterSeries, QChart
from PySide6.QtCore import QThreadPool, QRunnable, QObject, Signal, QThread, Qt
from PySide6.QtWidgets import QLabel, QTreeWidget, QTreeWidgetItem, QLineEdit, \
    QVBoxLayout, QPushButton, QHBoxLayout, QComboBox, QGroupBox, QFormLayout, QTabWidget, QGridLayout, \
    QButtonGroup, QCheckBox, QSpinBox, QDoubleSpinBox, QRadioButton
from PySide6.QtGui import QPalette

from MyWidgets import PathLineEdit, ExtGroup, CodeEditor, FuncLineEdit
from data import *
from xml.etree.ElementTree import Element, parse, ParseError


class GetnativeWidget(QWidget):
    class Thread(QRunnable):
        def __init__(self, task, success_signal: Signal, error_signal: Signal):
            super().__init__()
            self.successSignal = success_signal
            self.errorSignal = error_signal
            self.task = task

        def run(self):
            try:
                self.successSignal.emit(self.task.run())
            except Exception as e:
                self.errorSignal.emit(f'{type(e)}: {e}')

    class Tasks(QObject):
        def __init__(self,
                     success_signal: Signal,
                     error_signal: Signal,
                     finish_signal: Signal):
            super().__init__()
            self.successSignal = success_signal
            self.errorSignal = error_signal
            self.finishSignal = finish_signal
            self.pool = QThreadPool()
            self.pool.globalInstance()
            self.pool.setMaxThreadCount(cpu_count() - 1)

        def start(self, tasks: list):
            for task in tasks:
                task_thread = GetnativeWidget.Thread(task, self.successSignal, self.errorSignal)
                task_thread.setAutoDelete(True)
                self.pool.start(task_thread)
            tasks.clear()
            self.pool.waitForDone()
            self.finishSignal.emit()

    class TaskThread(QThread):
        finishSignal = Signal()
        successSignal = Signal(tuple)
        errorSignal = Signal(str)

        def __init__(self):
            super().__init__()
            self.tasks = []
            self.task = GetnativeWidget.Tasks(self.successSignal,
                                              self.errorSignal,
                                              self.finishSignal)

        def run(self):
            self.task.start(self.tasks)

    class ChartView(QChartView):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.chart = QChart()
            self.axis_x = QValueAxis()
            self.axis_y = QValueAxis()
            self.line_series = QLineSeries()
            self.scatter_series = QScatterSeries()
            self.init_ui()

        def init_ui(self):
            self.setContentsMargins(0, 0, 0, 0)
            self.setChart(self.chart)

            self.axis_x.setLabelFormat('%.d')
            self.axis_y.setTickType(QValueAxis.TickType.TicksFixed)
            self.axis_y.setTickCount(5)
            self.axis_y.setLabelFormat('%.3f')
            self.chart.addSeries(self.line_series)
            self.chart.addSeries(self.scatter_series)
            self.chart.setContentsMargins(0, 0, 0, 0)
            self.chart.layout().setContentsMargins(0, 0, 0, 0)

            self.scatter_series.setPointLabelsVisible(True)
            self.scatter_series.setMarkerSize(8)
            self.chart.addAxis(self.axis_x, Qt.AlignmentFlag.AlignBottom)
            self.chart.addAxis(self.axis_y, Qt.AlignmentFlag.AlignLeft)
            self.init_language()

        def init_language(self):
            chart_text = LANG_UI_TXT.ToolsWidget.getnative.ChartView
            self.axis_x.setTitleText(chart_text.height)
            self.axis_y.setTitleText(chart_text.difference)
            self.scatter_series.setName(chart_text.best)

        def set_data(self, points: list, best_xs: list, filename: str):
            xs = [x for x, _ in points]
            ys = [y for _, y in points]

            self.line_series.setName(filename)
            if ys and xs:
                min_x = min(xs)
                max_x = max(xs)
                min_y = min(ys)
                max_y = max(ys)
                for x, y in points:
                    self.line_series.append(x, y)
                    if x in best_xs:
                        self.scatter_series.append(x, round(y, 2))

                left = (min_x - 1) // 50 * 50
                right = ((max_x + 1) // 50 + 1) * 50
                for d in range(9, 1, -1):
                    if 50 * d == right - left:
                        break
                else:
                    d = 5
                self.axis_x.setRange(left, right)
                self.axis_x.setTickCount(d + 1)
                diff = round((max_y - min_y) / 4, 3)

                self.axis_y.setRange(max(0, min_y - diff), max_y + diff)
                self.line_series.attachAxis(self.axis_x)
                self.line_series.attachAxis(self.axis_y)

                self.scatter_series.attachAxis(self.axis_x)
                self.scatter_series.attachAxis(self.axis_y)

    class DefineScaler:
        def __init__(self, kernel: str, b: float = 0, c: float = 0, taps: int = 0):
            """
            Get a scaler for getnative from descale

            :param kernel: kernel for descale
            :param b: b value for kernel "bicubic" (default 0)
            :param c: c value for kernel "bicubic" (default 0)
            :param taps: taps value for kernel "lanczos" (default 0)
            """

            self.kernel = kernel
            self.b = b
            self.c = c
            self.taps = taps

            self.descaler = getattr(CORE.descale, f'De{self.kernel}', None)
            self.upscaler = getattr(CORE.resize, self.kernel.title())

            self.check_input()
            self.check_for_extra_paras()

        def check_for_extra_paras(self):
            if self.kernel == 'bicubic':
                self.descaler = Partial(self.descaler, b=self.b, c=self.c)
                self.upscaler = Partial(self.upscaler, filter_param_a=self.b, filter_param_b=self.c)
            elif self.kernel == 'lanczos':
                self.descaler = Partial(self.descaler, taps=self.taps)
                self.upscaler = Partial(self.upscaler, filter_param_a=self.taps)

        def check_input(self):
            if self.descaler is None and self.kernel == "spline64":
                raise Exception(f'descale: spline64 support is missing, update descale (>r3).')
            elif self.descaler is None:
                raise Exception(f'descale: {self.kernel} is not a supported kernel.')

        def __str__(self):
            return (
                f"{self.kernel.capitalize()}"
                f"{'' if self.kernel != 'bicubic' else f' b {self.b:.2f} c {self.c:.2f}'}"
                f"{'' if self.kernel != 'lanczos' else f' taps {self.taps}'}"
            )

        def __repr__(self):
            return (
                f"ScalerObject: "
                f"{self.kernel.capitalize()}"
                f"{'' if self.kernel != 'bicubic' else f' b {self.b:.2f} c {self.c:.2f}'}"
                f"{'' if self.kernel != 'lanczos' else f' taps {self.taps}'}"
            )

    class GetNative:
        def __init__(self,
                     core,
                     input_path: str,
                     output_dir: str,
                     scaler,
                     frame: int,
                     kernel: str,
                     ar: float,
                     min_h: int,
                     max_h: int,
                     mask_out: bool,
                     no_save: bool,
                     steps: int,
                     use: callable):
            self.core = core
            self.frame = frame
            self.kernel = kernel
            self.ar = ar
            self.min_h = min_h
            self.max_h = max_h
            self.mask_out = mask_out
            self.no_save = no_save
            self.steps = steps
            self.output_dir = output_dir
            self.input_path = input_path
            self.use = use
            self.scaler = scaler
            self.resolutions = []
            self.filename = self.get_filename()

        def run(self):
            src = self.use(self.input_path)

            if self.frame > src.num_frames - 1:
                raise Exception(f"Last frame is {src.num_frames - 1}, but you want {self.frame}")

            if self.ar == 0:
                self.ar = src.width / src.height

            if self.min_h >= src.height:
                raise Exception(f"Input image {src.height} is smaller min_h {self.min_h}")
            elif self.min_h >= self.max_h:
                raise Exception(f"min_h {self.min_h} > max_h {self.max_h}? Not processable")
            elif self.max_h > src.height:
                print(f"The image height is {src.height}, going higher is stupid! New max_h {src.height}")
                self.max_h = src.height

            src = src[self.frame]
            matrix_s = '709' if src.format.color_family == vs.RGB else None
            src_luma32 = self.core.resize.Point(src, format=vs.YUV444PS, matrix_s=matrix_s)
            src_luma32 = self.core.std.ShufflePlanes(src_luma32, 0, vs.GRAY)
            src_luma32 = self.core.std.Cache(src_luma32)

            # descale each individual frame
            clip_list = [self.scaler.descaler(src_luma32, self.getw(h), h)
                         for h in range(self.min_h, self.max_h + 1, self.steps)]
            full_clip = self.core.std.Splice(clip_list, mismatch=True)
            full_clip = self.scaler.upscaler(full_clip, self.getw(src.height), src.height)
            if self.ar != src.width / src.height:
                src_luma32 = self.scaler.upscaler(src_luma32, self.getw(src.height), src.height)
            expr_full = self.core.std.Expr([src_luma32 * full_clip.num_frames, full_clip],
                                           'x y - abs dup 0.015 > swap 0 ?')
            full_clip = self.core.std.CropRel(expr_full, 5, 5, 5, 5)
            full_clip = self.core.std.PlaneStats(full_clip)
            full_clip = self.core.std.Cache(full_clip)

            vals = []
            for frame in full_clip.frames():
                vals.append(frame.props.PlaneStatsAverage)
            ratios = self.analyze_results(vals)

            best_values = (
                f"Native resolution(s) (best guess): "
                f"{'p, '.join([str(r * self.steps + self.min_h) for r in self.resolutions])}p"
            )
            txt_output = (
                f"Resize Kernel: {self.scaler}\n"
                f"{best_values}\n"
                f"Please check the graph manually for more accurate results\n\n"
            )
            txt_output += 'Raw data:\nResolution\t | Relative Error\t | Relative difference from last\n'
            txt_output += '\n'.join([
                f'{i * self.steps + self.min_h:4d}\t\t | {error:.10f}\t\t | {ratios[i]:.3f}'
                for i, error in enumerate(vals)
            ])

            if not self.no_save:
                if not QFileInfo(self.output_dir).isDir():
                    QDir().mkdir(self.output_dir)
                with open(f"{self.output_dir}/{self.filename}.txt", "w") as stream:
                    stream.writelines(txt_output)
                if self.mask_out:
                    self.save_images(src_luma32)

            dh_sequence = list(range(self.min_h, self.max_h + 1, self.steps))
            points = [(x, y) for x, y in zip(dh_sequence, ratios) if y != 0]
            best_xs = [r * self.steps + self.min_h for r in self.resolutions]

            return self.input_path, self.filename, points, best_xs

        def getw(self, h, only_even=True):
            w = h * self.ar
            w = int(round(w))
            if only_even:
                w = w // 2 << 1

            return w

        def analyze_results(self, vals: list) -> list:
            ratios = [0.0]
            for i in range(1, len(vals)):
                last = vals[i - 1]
                current = vals[i]
                if last == current == 0:
                    ratios.append(ratios[i - 1])
                else:
                    ratios.append((last or 0.0000000001) / (current or 0.0000000001))
            sorted_array = sorted(list(set(ratios)), reverse=True)
            max_difference = sorted_array[0]

            difference = {}
            for n, d in enumerate(ratios):
                left = max(0, n - 10)
                right = min(n + 10, len(ratios))
                if max(ratios[left:right]) == d \
                        and d - 1 > (max_difference - 1) * 0.33 \
                        and d in sorted_array[:5] \
                        and (ratios.index(d) == n or ratios.index(d) not in range(left, right)):
                    difference[n] = d

            self.resolutions.extend(difference.keys())

            return ratios

        def mask_detail(self, clip, final_width, final_height):
            temp = self.scaler.descaler(clip, final_width, final_height)
            temp = self.scaler.upscaler(temp, clip.width, clip.height)
            mask = self.core.std.Expr([clip, temp], 'x y - abs dup 0.015 > swap 16 * 0 ?').std.Inflate()
            mask = GetnativeWidget.DefineScaler(kernel="spline36").upscaler(mask, final_width, final_height)

            return mask

        def save_images(self, src_luma32: vs.VideoNode):
            src = src_luma32
            first_out = self.core.imwri.Write(src, 'png', f'{self.output_dir}/{self.filename}_source%d.png')
            first_out.get_frame(0)  # trick vapoursynth into rendering the frame
            for r in self.resolutions:
                r = r * self.steps + self.min_h
                image = self.mask_detail(src, self.getw(r), r)
                mask_out = self.core.imwri.Write(image, 'png', f'{self.output_dir}/{self.filename}_mask_{r:d}p%d.png')
                mask_out.get_frame(0)
                descale_out = self.scaler.descaler(src, self.getw(r), r)
                descale_out = self.core.imwri.Write(descale_out, 'png',
                                                    f'{self.output_dir}/{self.filename}_{r:d}p%d.png')
                descale_out.get_frame(0)

        def get_filename(self):
            return (
                f"f_{self.frame}"
                f"_{str(self.scaler).replace(' ', '_')}"
                f"_ar_{self.ar:.2f}"
                f"_steps_{self.steps}"
            )

    def __init__(self, descale: bool, avisource: bool, ffms: bool, lsmash: bool, imwri: bool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.common_scaler = {}
        self.home = QVBoxLayout(self)

        self.inputGroupBox = QGroupBox(self)
        self.modeGroupBox = QGroupBox(self)
        self.generalGroupBox = QGroupBox(self)
        self.kernelGroupBox = QGroupBox(self)
        self.outputGroupBox = QGroupBox(self)

        self.useLabel = QLabel(self)
        self.useButtonGroup = QButtonGroup()
        self.ffms2RadioButton = QRadioButton(self)
        self.LWLibavSourceRadioButton = QRadioButton(self)
        self.avisourceRadioButton = QRadioButton(self)
        self.imwriRadioButton = QRadioButton(self)
        self.modeButtonGroup = QButtonGroup()
        self.noneRadioButton = QRadioButton(self)
        self.bilinearRadioButton = QRadioButton(self)
        self.bicubicRadioButton = QRadioButton(self)
        self.lanczosRadioButton = QRadioButton(self)
        self.splineRadioButton = QRadioButton(self)
        self.allRadioButton = QRadioButton(self)
        self.frameLabel = QLabel(self)
        self.frameSpinBox = QSpinBox(self)
        self.kernelComboBox = QComboBox(self)
        self.bicubicBLabel = QLabel(self)
        self.bicubicBDoubleSpinBox = QDoubleSpinBox(self)
        self.bicubicCLabel = QLabel(self)
        self.bicubicCDoubleSpinBox = QDoubleSpinBox(self)
        self.lanczosTapsLabel = QLabel(self)
        self.lanczosTapsSpinBox = QSpinBox(self)
        self.aspectRatioLabel = QLabel(self)
        self.aspectRatioSpinBox = QDoubleSpinBox(self)
        self.minHeightLabel = QLabel(self)
        self.minHeightSpinBox = QSpinBox(self)
        self.maxHeightLabel = QLabel(self)
        self.maxHeightSpinBox = QSpinBox(self)
        self.outputMaskCheckBox = QCheckBox(self)
        self.steppingLabel = QLabel(self)
        self.steppingSpinBox = QSpinBox(self)
        self.inputFileLineEdit = PathLineEdit(QFileDialog.getOpenFileName, None, self)
        self.chartTabWidget = QTabWidget(self)
        self.outputLabel = QLabel(self)
        self.outputDirLineEdit = PathLineEdit(QFileDialog.getExistingDirectory, None, self)

        self.taskThread = GetnativeWidget.TaskThread()

        self.aboutWidget = QWidget(self)
        self.aboutLabels = [QLabel(self) for _ in range(5)]

        self.runningMsgLabel = QLabel(self)
        self.startButton = QPushButton(self)
        self.resetButton = QPushButton(self)
        self.clearButton = QPushButton(self)
        self.aboutButton = QPushButton(self)

        if descale:
            self.init_scaler()
        else:
            self.setDisabled(True)
        self.init_ui()

    def init_ui(self):
        self.inputFileLineEdit.textChanged.connect(self.enable_start)
        self.outputGroupBox.toggled.connect(self.is_save)
        self.outputDirLineEdit.textChanged.connect(self.enable_start)

        self.useButtonGroup.addButton(self.ffms2RadioButton, 0)
        self.useButtonGroup.addButton(self.LWLibavSourceRadioButton, 1)
        self.useButtonGroup.addButton(self.avisourceRadioButton, 2)
        self.useButtonGroup.addButton(self.imwriRadioButton, 3)
        self.ffms2RadioButton.setText('ffms2')
        self.LWLibavSourceRadioButton.setText('LWLibavSource')
        self.avisourceRadioButton.setText('avisource')
        self.imwriRadioButton.setText('ImageMagick Writer-Reader')

        self.modeButtonGroup.addButton(self.noneRadioButton, 0)
        self.modeButtonGroup.addButton(self.bilinearRadioButton, 1)
        self.modeButtonGroup.addButton(self.bicubicRadioButton, 2)
        self.modeButtonGroup.addButton(self.lanczosRadioButton, 3)
        self.modeButtonGroup.addButton(self.splineRadioButton, 4)
        self.modeButtonGroup.addButton(self.allRadioButton, 5)
        self.modeButtonGroup.buttonClicked.connect(self.change_mode)
        self.frameSpinBox.setRange(0, 9999999)
        self.kernelComboBox.addItems(('bicubic', 'lanczos', 'bilinear', 'spline16', 'spline36', 'spline64'))
        self.kernelComboBox.currentTextChanged.connect(self.change_kernel)
        self.bicubicBDoubleSpinBox.setRange(-10, 10)
        self.bicubicBDoubleSpinBox.setSingleStep(0.1)
        self.bicubicCDoubleSpinBox.setRange(-10, 10)
        self.bicubicCDoubleSpinBox.setSingleStep(0.1)
        self.lanczosTapsSpinBox.setRange(1, 100)
        self.aspectRatioSpinBox.setRange(0, 100)
        self.minHeightSpinBox.setRange(8, 9999)
        self.maxHeightSpinBox.setRange(9, 9999)
        self.steppingSpinBox.setRange(1, 999999)
        self.startButton.clicked.connect(self.run)
        self.resetButton.clicked.connect(self.reset)
        self.clearButton.clicked.connect(self.chartTabWidget.clear)
        self.outputGroupBox.setCheckable(True)
        self.chartTabWidget.setContentsMargins(0, 0, 0, 0)
        self.chartTabWidget.setTabsClosable(True)
        self.chartTabWidget.tabCloseRequested.connect(self.chartTabWidget.removeTab)
        self.taskThread.successSignal.connect(self.get_result)
        self.taskThread.errorSignal.connect(self.get_error)
        self.taskThread.finishSignal.connect(self.task_done)

        self.aboutButton.clicked.connect(self.aboutWidget.show)
        self.aboutWidget.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Popup)
        self.aboutWidget.setLayout(QVBoxLayout())
        self.aboutWidget.setFixedSize(600, 400)
        palette = QPalette()
        palette.setBrush(self.backgroundRole(), QColor('#FFFBFF'))
        self.aboutWidget.setPalette(palette)
        move_to_middle(self.aboutWidget)
        for widget in self.aboutLabels:
            widget.setWordWrap(True)
            self.aboutWidget.layout().addWidget(widget)

        layout1 = QGridLayout(self.inputGroupBox)
        layout1.setSpacing(5)
        layout1.addWidget(self.inputFileLineEdit, 0, 0, 1, 5)
        layout1.addWidget(self.useLabel, 1, 0, 1, 1)
        layout1.addWidget(self.ffms2RadioButton, 1, 1, 1, 1)
        layout1.addWidget(self.LWLibavSourceRadioButton, 1, 2, 1, 1)
        layout1.addWidget(self.avisourceRadioButton, 1, 3, 1, 1)
        layout1.addWidget(self.imwriRadioButton, 1, 4, 1, 1)
        layout1.setColumnStretch(0, 1)
        layout1.setColumnStretch(1, 100)
        layout1.setColumnStretch(2, 100)
        layout1.setColumnStretch(3, 100)
        layout1.setColumnStretch(4, 100)

        layout2 = QHBoxLayout(self.modeGroupBox)
        layout2.setSpacing(5)
        layout2.addWidget(self.noneRadioButton)
        layout2.addWidget(self.bilinearRadioButton)
        layout2.addWidget(self.bicubicRadioButton)
        layout2.addWidget(self.lanczosRadioButton)
        layout2.addWidget(self.splineRadioButton)
        layout2.addWidget(self.allRadioButton)

        layout3 = QHBoxLayout(self.kernelGroupBox)
        layout3.setSpacing(5)
        layout3.addWidget(self.kernelComboBox)
        layout3.addWidget(self.bicubicBLabel)
        layout3.addWidget(self.bicubicBDoubleSpinBox)
        layout3.addWidget(self.bicubicCLabel)
        layout3.addWidget(self.bicubicCDoubleSpinBox)
        layout3.addWidget(self.lanczosTapsLabel)
        layout3.addWidget(self.lanczosTapsSpinBox)
        for c in range(10):
            if c % 2:
                layout3.setStretch(c, 1)
            else:
                layout3.setStretch(c, 100)

        layout4 = QHBoxLayout(self.generalGroupBox)
        layout4.setSpacing(5)
        layout4.addWidget(self.frameLabel)
        layout4.addWidget(self.frameSpinBox)
        layout4.addWidget(self.aspectRatioLabel)
        layout4.addWidget(self.aspectRatioSpinBox)
        layout4.addWidget(self.minHeightLabel)
        layout4.addWidget(self.minHeightSpinBox)
        layout4.addWidget(self.maxHeightLabel)
        layout4.addWidget(self.maxHeightSpinBox)
        layout4.addWidget(self.steppingLabel)
        layout4.addWidget(self.steppingSpinBox)
        for c in range(10):
            if c % 2:
                layout4.setStretch(c, 100)
            else:
                layout4.setStretch(c, 1)

        layout5 = QFormLayout(self.outputGroupBox)
        layout5.setSpacing(5)
        layout5.addRow(self.outputMaskCheckBox)
        layout5.addRow(self.outputLabel, self.outputDirLineEdit)

        layout6 = QHBoxLayout()
        layout6.setSpacing(5)
        layout6.addStretch(1)
        layout6.addWidget(self.runningMsgLabel)
        layout6.addWidget(self.startButton)
        layout6.addWidget(self.resetButton)
        layout6.addWidget(self.clearButton)
        layout6.addWidget(self.aboutButton)

        self.home.addWidget(self.inputGroupBox)
        self.home.addWidget(self.modeGroupBox)
        self.home.addWidget(self.kernelGroupBox)
        self.home.addWidget(self.generalGroupBox)
        self.home.addWidget(self.outputGroupBox)
        self.home.addWidget(self.chartTabWidget)
        self.home.addLayout(layout6)

    def init_font(self, font: QFont):
        self.generalGroupBox.setFont(font)
        self.modeGroupBox.setFont(font)
        self.outputGroupBox.setFont(font)
        self.kernelGroupBox.setFont(font)
        self.inputGroupBox.setFont(font)
        self.ffms2RadioButton.setFont(font)
        self.LWLibavSourceRadioButton.setFont(font)
        self.avisourceRadioButton.setFont(font)
        self.imwriRadioButton.setFont(font)
        self.noneRadioButton.setFont(font)
        self.bilinearRadioButton.setFont(font)
        self.bicubicRadioButton.setFont(font)
        self.lanczosRadioButton.setFont(font)
        self.splineRadioButton.setFont(font)
        self.allRadioButton.setFont(font)
        self.frameSpinBox.setFont(font)
        self.kernelComboBox.setFont(font)
        self.bicubicBDoubleSpinBox.setFont(font)
        self.bicubicCDoubleSpinBox.setFont(font)
        self.lanczosTapsSpinBox.setFont(font)
        self.aspectRatioSpinBox.setFont(font)
        self.minHeightSpinBox.setFont(font)
        self.maxHeightSpinBox.setFont(font)
        self.outputMaskCheckBox.setFont(font)
        self.steppingSpinBox.setFont(font)
        self.inputFileLineEdit.setFont(font)
        self.outputDirLineEdit.setFont(font)
        self.bicubicBLabel.setFont(font)
        self.bicubicCLabel.setFont(font)
        self.lanczosTapsLabel.setFont(font)
        self.frameLabel.setFont(font)
        self.minHeightLabel.setFont(font)
        self.maxHeightLabel.setFont(font)
        self.aspectRatioLabel.setFont(font)
        self.steppingLabel.setFont(font)
        self.useLabel.setFont(font)
        self.outputLabel.setFont(font)
        self.runningMsgLabel.setFont(font)
        self.startButton.setFont(font)
        self.resetButton.setFont(font)
        self.clearButton.setFont(font)
        self.aboutWidget.setFont(font)

    def init_language(self):
        getnative_text = LANG_UI_TXT.ToolsWidget.getnative
        for title, groupbox in zip(getnative_text.groupboxes,
                                   (self.inputGroupBox,
                                    self.modeGroupBox,
                                    self.kernelGroupBox,
                                    self.generalGroupBox,
                                    self.outputGroupBox)):
            groupbox.setTitle(title)
        for mode, button in zip(getnative_text.modes,
                                (self.noneRadioButton,
                                 self.bilinearRadioButton,
                                 self.bicubicRadioButton,
                                 self.lanczosRadioButton,
                                 self.splineRadioButton,
                                 self.allRadioButton)):
            button.setText(mode)
        self.bicubicBLabel.setText(getnative_text.b)
        self.bicubicCLabel.setText(getnative_text.c)
        self.lanczosTapsLabel.setText(getnative_text.taps)
        self.frameLabel.setText(getnative_text.frame)
        self.minHeightLabel.setText(getnative_text.min_height)
        self.maxHeightLabel.setText(getnative_text.max_height)
        self.aspectRatioLabel.setText(getnative_text.ar)
        self.steppingLabel.setText(getnative_text.stepping)
        self.useLabel.setText(getnative_text.input_filter)
        self.outputLabel.setText(getnative_text.output_dir)
        self.outputMaskCheckBox.setText(getnative_text.output_mask)
        self.startButton.setText(LANG_UI_TXT.button.start)
        self.resetButton.setText(LANG_UI_TXT.button.reset)
        self.clearButton.setText(LANG_UI_TXT.button.clear)
        self.aboutButton.setText(LANG_UI_TXT.button.about)
        if self.runningMsgLabel.text():
            self.runningMsgLabel.setText(getnative_text.task_running)
        for index in range(self.chartTabWidget.count()):
            self.chartTabWidget.widget(index).init_language()

        self.aboutWidget.setWindowTitle(getnative_text.aboutWidget.title)
        for text, label in zip(getnative_text.aboutWidget.labels, self.aboutLabels):
            label.setText(text)

    def init_scaler(self):
        self.common_scaler.update({
            "bilinear": [self.DefineScaler("bilinear")],
            "bicubic": [
                self.DefineScaler("bicubic", b=1 / 3, c=1 / 3),
                self.DefineScaler("bicubic", b=.5, c=0),
                self.DefineScaler("bicubic", b=0, c=.5),
                self.DefineScaler("bicubic", b=1, c=0),
                self.DefineScaler("bicubic", b=0, c=1),
                self.DefineScaler("bicubic", b=.2, c=.5),
                self.DefineScaler("bicubic", b=.5, c=.5),
            ],
            "lanczos": [
                self.DefineScaler("lanczos", taps=2),
                self.DefineScaler("lanczos", taps=3),
                self.DefineScaler("lanczos", taps=4),
                self.DefineScaler("lanczos", taps=5),
            ],
            "spline": [
                self.DefineScaler("spline16"),
                self.DefineScaler("spline36"),
                self.DefineScaler("spline64"),
            ]
        })
        self.reset()

    def reset(self):
        self.frameSpinBox.setValue(500)
        self.kernelComboBox.setCurrentIndex(0)
        self.noneRadioButton.click()
        self.ffms2RadioButton.click()
        self.bicubicBDoubleSpinBox.setValue(1 / 3)
        self.bicubicCDoubleSpinBox.setValue(1 / 3)
        self.lanczosTapsSpinBox.setValue(3)
        self.lanczosTapsSpinBox.setDisabled(True)
        self.aspectRatioSpinBox.setValue(0)
        self.minHeightSpinBox.setValue(500)
        self.maxHeightSpinBox.setValue(1000)
        self.outputMaskCheckBox.setChecked(False)
        self.outputMaskCheckBox.setDisabled(True)
        self.steppingSpinBox.setValue(1)
        self.outputDirLineEdit.setDisabled(True)
        self.outputGroupBox.setChecked(False)
        if self.inputFileLineEdit.text():
            self.startButton.setEnabled(True)
        else:
            self.startButton.setDisabled(True)

    def is_save(self, checked: bool):
        if checked and IMWRI:
            self.outputMaskCheckBox.setEnabled(True)
            self.outputDirLineEdit.setEnabled(True)
        else:
            self.outputMaskCheckBox.setDisabled(True)
            self.outputDirLineEdit.setDisabled(True)
        self.enable_start()

    def enable_start(self):
        sender = self.sender()
        input_path = self.inputFileLineEdit.text()
        if sender == self.inputFileLineEdit and input_path and not self.outputDirLineEdit.text():
            self.outputDirLineEdit.setText(QFileInfo(input_path).dir().absolutePath())
        if not input_path:
            self.startButton.setDisabled(True)
        else:
            if self.outputGroupBox.isChecked() and not self.outputDirLineEdit.text():
                self.startButton.setDisabled(True)
            elif self.runningMsgLabel.text():
                self.startButton.setDisabled(True)
            else:
                self.startButton.setEnabled(True)

    def change_mode(self, button: QRadioButton):
        if button == self.noneRadioButton:
            self.change_kernel(self.kernelComboBox.currentText())
            self.kernelComboBox.setEnabled(True)
        else:
            self.kernelComboBox.setDisabled(True)
            self.lanczosTapsSpinBox.setDisabled(True)
            self.bicubicBDoubleSpinBox.setDisabled(True)
            self.bicubicCDoubleSpinBox.setDisabled(True)

    def change_kernel(self, kernel: str):
        if kernel == 'bicubic':
            self.bicubicBDoubleSpinBox.setEnabled(True)
            self.bicubicCDoubleSpinBox.setEnabled(True)
            self.lanczosTapsSpinBox.setDisabled(True)
        elif kernel == 'lanczos':
            self.lanczosTapsSpinBox.setEnabled(True)
            self.bicubicBDoubleSpinBox.setDisabled(True)
            self.bicubicCDoubleSpinBox.setDisabled(True)
        else:
            self.bicubicBDoubleSpinBox.setDisabled(True)
            self.bicubicCDoubleSpinBox.setDisabled(True)
            self.lanczosTapsSpinBox.setDisabled(True)

    def run(self):
        if (use := self.useButtonGroup.checkedId()) == 0:
            use = CORE.ffms2.Source if FFMS2 else 'ffms2'
        elif use == 1:
            use = CORE.lsmas.LWLibavSource if LSMASH else 'lsmash'
        elif use == 2:
            use = CORE.avisource.AVISource if AVISOURCE else 'avisource'
        else:
            use = CORE.imwri.Read if IMWRI else 'imwri'
        if type(use) == str:
            QMessageBox.warning(self,
                                LANG_UI_TXT.info.error,
                                f'{use} {LANG_UI_TXT.info.not_available}')
            return
        self.startButton.setDisabled(True)
        min_h = self.minHeightSpinBox.value()
        max_h = self.maxHeightSpinBox.value()
        if (mode := self.modeButtonGroup.checkedId()) == 0:
            b = self.bicubicBDoubleSpinBox.value()
            c = self.bicubicCDoubleSpinBox.value()
            taps = self.lanczosTapsSpinBox.value()
            mode = [self.DefineScaler(self.kernelComboBox.currentText(), b=b, c=c, taps=taps)]
        elif mode == 1:
            mode = self.common_scaler["bilinear"]
        elif mode == 2:
            mode = [scaler for scaler in self.common_scaler["bicubic"]]
        elif mode == 3:
            mode = [scaler for scaler in self.common_scaler["lanczos"]]
        elif mode == 4:
            mode = [scaler for scaler in self.common_scaler["spline"]]
        else:
            mode = [s for scaler in self.common_scaler.values() for s in scaler]
        for scaler in mode:
            commands = GetnativeWidget.GetNative(CORE,
                                                 self.inputFileLineEdit.text(),
                                                 self.outputDirLineEdit.text(),
                                                 scaler=scaler,
                                                 frame=self.frameSpinBox.value(),
                                                 kernel=self.kernelComboBox.currentText(),
                                                 ar=self.aspectRatioSpinBox.value(),
                                                 min_h=min_h,
                                                 max_h=max_h,
                                                 mask_out=self.outputMaskCheckBox.isChecked(),
                                                 no_save=not self.outputGroupBox.isChecked(),
                                                 steps=self.steppingSpinBox.value(),
                                                 use=use)

            self.taskThread.tasks.append(commands)
        self.taskThread.start()
        self.runningMsgLabel.setText(LANG_UI_TXT.ToolsWidget.getnative.task_running)

    def get_result(self, result: tuple):
        input_path, filename, points, best_xs = result
        base_name = QFileInfo(input_path).completeBaseName()
        ext = QFileInfo(input_path).suffix()
        if len(base_name) > 10:
            sum_file_name = f'{base_name[:5]}..{base_name[-3:]}.{ext}'
        else:
            sum_file_name = f'{base_name}.{ext}'
        chart = self.ChartView(self)

        chart.set_data(points, best_xs, filename)
        self.chartTabWidget.addTab(chart, sum_file_name)

    def get_error(self, msg: str):
        QMessageBox.warning(self,
                            LANG_UI_TXT.info.error,
                            msg,
                            QMessageBox.StandardButton.Ok,
                            QMessageBox.StandardButton.Ok)

    def task_done(self):
        self.runningMsgLabel.clear()
        self.enable_start()
        print('task all done')


class DelogoWidget(QWidget):
    class Thread(QRunnable):
        def __init__(self, task, success_signal: Signal, error_signal: Signal):
            super().__init__()
            self.successSignal = success_signal
            self.errorSignal = error_signal
            self.task = task

        def run(self):
            try:
                self.successSignal.emit(self.task.run())
            except Exception as e:
                self.errorSignal.emit(f'{type(e)}: {e}')

    class Tasks(QObject):
        def __init__(self,
                     success_signal: Signal,
                     error_signal: Signal,
                     finish_signal: Signal):
            super().__init__()
            self.successSignal = success_signal
            self.errorSignal = error_signal
            self.finishSignal = finish_signal
            self.pool = QThreadPool()
            self.pool.globalInstance()
            self.pool.setMaxThreadCount(cpu_count() - 1)

        def start(self, tasks: list):
            for task in tasks:
                task_thread = GetnativeWidget.Thread(task, self.successSignal, self.errorSignal)
                task_thread.setAutoDelete(True)
                self.pool.start(task_thread)
            tasks.clear()
            self.pool.waitForDone()
            self.finishSignal.emit()

    class TaskThread(QThread):
        finishSignal = Signal()
        successSignal = Signal(tuple)
        errorSignal = Signal(str)

        def __init__(self):
            super().__init__()
            self.tasks = []
            self.task = GetnativeWidget.Tasks(self.successSignal,
                                              self.errorSignal,
                                              self.finishSignal)

        def run(self):
            self.task.start(self.tasks)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class VapourSynthWidget(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.home = QGridLayout(self)
        self.pathLine = PathLineEdit(QFileDialog.getOpenFileName, ExtGroup('vpy'), self)
        self.codeEditor = CodeEditor(CodeEditor.CodeType.Vpy)
        self.funcTreeWidget = QTreeWidget(self)

        self.parGroupBox = QGroupBox(self)
        self.partPars = QFormLayout(self.parGroupBox)
        self.partCode = QHBoxLayout()
        self.codeLabel = QLabel(self)
        self.insertButton = QPushButton(self)
        self.saveButton = QPushButton(self)
        self.funcs: dict[Element] = {}
        self.parWidgets = []
        self.cur_funcs: Element = None
        self.init_ui()
        self.init_funcs()

    def init_ui(self):
        self.pathLine.textChanged.connect(self.load)
        self.codeEditor.setDisabled(True)
        self.funcTreeWidget.setDisabled(True)
        self.funcTreeWidget.setHeaderHidden(True)
        self.funcTreeWidget.setColumnCount(1)
        self.funcTreeWidget.currentItemChanged.connect(self.select_func)

        self.parGroupBox.setMinimumHeight(120)
        self.parGroupBox.setDisabled(True)
        self.insertButton.setDisabled(True)
        self.insertButton.clicked.connect(self.insert_code)
        self.saveButton.setDisabled(True)

        self.partCode.addWidget(self.codeLabel)
        self.partCode.addStretch(1)
        self.partCode.addWidget(self.insertButton)

        self.home.addWidget(self.pathLine, 0, 0, 1, 3)
        self.home.addWidget(self.codeEditor, 1, 0, 1, 1)
        self.home.addWidget(self.funcTreeWidget, 1, 1, 1, 1)
        self.home.addWidget(self.parGroupBox, 1, 2, 1, 1)
        self.home.addLayout(self.partCode, 2, 0, 1, 3)
        self.home.addWidget(self.saveButton, 3, 0, 1, 3)
        self.home.setColumnStretch(0, 2)
        self.home.setColumnStretch(1, 1)
        self.home.setColumnStretch(2, 1)

    def load(self, path: str):
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.codeEditor.setPlainText(f.read())
            except Exception as e:
                QMessageBox.warning(self,
                                    LANG_UI_TXT.info.error,
                                    str(e),
                                    QMessageBox.StandardButton.Ok,
                                    QMessageBox.StandardButton.Ok,)
            else:
                self.codeEditor.setEnabled(True)
                self.funcTreeWidget.setEnabled(True)
                self.parGroupBox.setEnabled(True)
                self.saveButton.setEnabled(True)
                self.insertButton.setEnabled(True)
        else:
            self.codeEditor.clear()
            self.codeEditor.setDisabled(True)
            self.funcTreeWidget.setDisabled(True)
            self.parGroupBox.setDisabled(True)
            self.saveButton.setDisabled(True)
            self.insertButton.setDisabled(True)

    def add_func(self, top_item: QTreeWidgetItem, tree: Element, base_name: str):
        def check_int(element: Element, num: int, _par_name: str):
            lacks = []
            error = False
            msg = ''
            _min = element.find('min')
            _max = element.find('max')
            if _min is None:
                lacks.append('min')
            if _max is None:
                lacks.append('max')
            if lacks:
                error = True
                msg = f'{base_name} -> {LANG_UI_TXT.info.function} "{func_name}" -> ' \
                      f'{LANG_UI_TXT.info.parameter} {num} "{_par_name}": 缺少元素{lacks}'
            else:
                m_m = {'min': _min, 'max': _max}
                for k, v in m_m.items():
                    if v.text is None or not (v.text.isdigit() or (v.text[0] == '-' and v.text[1:].isdigit())):
                        error = True
                        msg = f'{base_name} -> {LANG_UI_TXT.info.function} "{func_name}" -> ' \
                              f'{LANG_UI_TXT.info.parameter} {num} "{_par_name}": 元素{k}必须是数字'
                        break
                else:
                    _min = int(_min.text)
                    _max = int(_max.text)
                    if _min >= _max:
                        error = True
                        msg = f'{base_name} -> {LANG_UI_TXT.info.function} "{func_name}" -> ' \
                              f'{LANG_UI_TXT.info.parameter} {num} "{_par_name}": 元素min必须小于max'
                    else:
                        if element.find('default') is not None:
                            default = element.find('default').text
                            if default is not None and not default.isdigit() and (default[0] != '-' or default[1:].isdigit()):
                                error = True
                                msg = f'{base_name} -> {LANG_UI_TXT.info.function} "{func_name}" -> ' \
                                      f'{LANG_UI_TXT.info.parameter} {num} "{_par_name}": 元素"default"必须是数字或空元素'
                            elif default is not None and not _max >= int(default) >= _min:
                                error = True
                                msg = f'{base_name} -> {LANG_UI_TXT.info.function} "{func_name}" -> ' \
                                      f'{LANG_UI_TXT.info.parameter} {num} "{_par_name}": 元素"default"必须小于max且大于min'
            return error, msg

        for child in tree:
            if child.tag == 'Class':
                sub_item = QTreeWidgetItem()
                sub_item.setText(0, child.attrib.get('name', ''))
                top_item.addChild(sub_item)
                self.add_func(sub_item, child, base_name)
            elif child.tag == 'Func':
                item = QTreeWidgetItem()
                func_name = child.find('Name').text if child.find('Name') is not None else ''
                error = False
                msg = ''
                if child.find('Code') is None:
                    error = True
                    msg = f'{base_name} -> {LANG_UI_TXT.info.function} "{func_name}": 缺少元素"Code"'
                else:
                    if (func_type := child.attrib.get('type', '')) == 'code':
                        pass
                    elif func_type == 'call':
                        if (pars := child.find('Parameters')) is not None:
                            for n, par in enumerate(pars):
                                par_name = par.find('name')
                                par_name = '' if par_name is None or par_name.text is None else par_name.text
                                if par.find('force') is None:
                                    error = True
                                    msg = f'{base_name} -> {LANG_UI_TXT.info.function} "{func_name}" -> '\
                                          f'{LANG_UI_TXT.info.parameter} {n} "{par_name}" : 缺少元素"force"'
                                    break
                                else:
                                    if (par_type := par.attrib.get('type', '')) == 'int':
                                        error, msg = check_int(par, n, par_name)
                                        if error:
                                            break
                                    elif par_type == 'bool':
                                        if par.find('default') is not None:
                                            if par.find('default').text not in ('True', 'False'):
                                                error = True
                                                msg = f'{base_name} -> {LANG_UI_TXT.info.function} "{func_name}" -> '\
                                                      f'{LANG_UI_TXT.info.parameter} {n} "{par_name}": 元素"default"必须是True或False'
                                                break
                                    elif par_type == 'str':
                                        pass
                                    else:
                                        pass
                    elif func_type == 'assign':
                        if (value := child.find('Value')) is None:
                            error = True
                            msg = f'{base_name} -> {LANG_UI_TXT.info.function} "{func_name}": 缺少元素"Value"'
                        elif value.text is None:
                            error = True
                            msg = f'{base_name} -> {LANG_UI_TXT.info.function} "{func_name}": "Value"不能是空元素'
                        else:
                            if (value_type := value.attrib.get('type', '')) == 'int':
                                error, msg = check_int(value, 0, 'Value')
                            elif value_type == 'bool':
                                pass
                            elif value_type == 'str':
                                pass
                            else:
                                pass

                if error:
                    with open(VSFUNCS_DIR.absoluteFilePath('error.txt'), 'a+',
                              encoding='utf-8') as f:
                        f.write(f'\n{get_time()}\n{msg}\n')
                    QMessageBox.warning(self,
                                        LANG_UI_TXT.info.error,
                                        'VapourSynth工具错误，请查看./vsfunc/error.txt文件',
                                        QMessageBox.StandardButton.Ok,
                                        QMessageBox.StandardButton.Ok,)
                else:
                    item.setText(0, func_name)
                    top_item.addChild(item)

    def init_funcs(self):
        for file_info in VSFUNCS_DIR.entryInfoList(filters=QDir.Filter.Files | QDir.Filter.Readable):
            try:
                tree = parse(file_info.absoluteFilePath())
            except ParseError:
                print(f'{file_info.absoluteFilePath()}错误，无法识别')
            else:
                root = tree.getroot()
                base_name = file_info.completeBaseName()
                self.funcs[base_name] = root
                top_item = QTreeWidgetItem()
                top_item.setText(0, base_name)
                self.funcTreeWidget.addTopLevelItem(top_item)
                self.add_func(top_item, root, base_name)

    def select_func(self, item: QTreeWidgetItem):
        if not item.childCount():
            parents = []
            parent = item.parent()
            while parent and isinstance(parent, QTreeWidgetItem):
                parents.append(parent.text(0))
                parent = parent.parent()
            if parents and (funcs := self.funcs.get(parents.pop(-1))):
                funcs: Element
                for p in reversed(parents):
                    for _class in funcs.findall('Class'):
                        if _class.get('name') == p:
                            funcs = _class
                            break
                    else:
                        print('nonono')
                        return
                for func in funcs.findall('Func'):
                    if func.find('Name').text == item.text(0):
                        self.parGroupBox.setTitle(item.text(0))
                        self.init_parameters(func)
                        break

    def init_parameters(self, trees: Element):
        self.parWidgets.clear()
        for row in range(self.partPars.rowCount()-1, -1, -1):
            self.partPars.removeRow(row)
        self.cur_funcs = trees
        self.parGroupBox.setTitle(trees.find('Name').text)
        if (func_type := trees.attrib.get('type')) == 'code':
            pass
        elif func_type == 'call':
            if (pars := trees.find('Parameters')) is not None:
                for n, par in enumerate(pars):
                    name = str(n) if par.find("name") is None else par.find("name").text
                    default = par.find("default")
                    if (value_type := par.get('type')) == 'int':
                        _min = int(par.find("min").text)
                        _max = int(par.find("max").text)
                        widget = QSpinBox(self)
                        widget.valueChanged.connect(self.tweak)
                        widget.setRange(_min-1, _max)
                        widget.setSpecialValueText('None')
                        self.parWidgets.append(widget)
                        if default is None:
                            widget.setValue(_min)
                        elif default.text is None:
                            widget.setValue(_min-1)
                        else:
                            widget.setValue(int(default.text))

                    elif value_type == 'bool':
                        widget = QCheckBox(self)
                        widget.setTristate(True)
                        widget.stateChanged.connect(self.tweak)
                        self.parWidgets.append(widget)
                        if default is None:
                            widget.setChecked(True)
                        elif default.text is None:
                            widget.setCheckState(1)
                        else:
                            widget.setChecked(True if default.text == 'True' else False)
                    elif value_type == 'str':
                        widget = QLineEdit(self)
                        widget.textChanged.connect(self.tweak)
                        self.parWidgets.append(widget)
                        if default is None:
                            widget.setText('')
                        elif default.text is None:
                            widget.setText('None')
                        else:
                            widget.setText(default.text)
                    else:
                        widget = FuncLineEdit(self)
                        widget.textChanged.connect(self.tweak)
                        self.parWidgets.append(widget)
                        if default is None and value_type == 'VideoNode':
                            widget.setText('clip')
                        elif default is not None and default.text is not None:
                            widget.setText(default.text)
                        else:
                            widget.setText('None')
                    self.partPars.addRow(name, widget)
        elif func_type == 'assign':
            self.cur_funcs = trees
            value = trees.find('Value')
            if (value_type := value.get('type')) == 'int':
                _min = int(value.find("min").text)
                _max = int(value.find("max").text)
                widget = QSpinBox(self)
                widget.valueChanged.connect(self.tweak)
                widget.setRange(_min - 1, _max)
                widget.setSpecialValueText('None')
                self.parWidgets.append(widget)
                widget.setValue(_min)
            elif value_type == 'bool':
                widget = QCheckBox(self)
                widget.setTristate(True)
                widget.stateChanged.connect(self.tweak)
                self.parWidgets.append(widget)
                widget.setCheckState(True)
            elif value_type == 'str':
                widget = QLineEdit(self)
                widget.textChanged.connect(self.tweak)
                self.parWidgets.append(widget)
                widget.setText('')
            else:
                widget = FuncLineEdit(self)
                widget.textChanged.connect(self.tweak)
                self.parWidgets.append(widget)
                widget.setText('None')
            self.partPars.addRow('value', widget)
        self.tweak()

    def tweak(self):
        def get_value(widget) -> str | None:
            if type(widget) == QLineEdit:
                v = None if widget.text() == 'None' else "'" + widget.text().replace('\\', r'\\').replace("'", r'\'') + "'"
            elif type(widget) == FuncLineEdit:
                v = None if widget.text() in ('None', '') else widget.text()
            elif type(widget) == QSpinBox:
                v = None if widget.text() == 'None' else widget.text()
            elif type(widget) == QCheckBox:
                v = widget.checkState()
                if v == 0:
                    v = 'False'
                elif v == 1:
                    v = None
                else:
                    v = 'True'
            else:
                v = ''
                print(f'value错误：widget_type "{type(widget)}"')
            return v

        args = [self.cur_funcs.find('Code').text]
        if (func_type := self.cur_funcs.attrib.get('type')) == 'code':
            pass
        elif func_type == 'call':
            if (pars := self.cur_funcs.find('Parameters')) is not None:
                kwargs = []
                for n, widget in enumerate(self.parWidgets):
                    value = get_value(widget)
                    par_name = pars[n].find("name")
                    par_name = None if par_name is None else par_name.text
                    default = pars[n].find("default")
                    if default is None or (None if default.text is None else default.text) != value:
                        if par_name is None:  # 这里n不知道会不会出错，请注意
                            kwargs.append(value)
                        else:
                            kwargs.append(f'{par_name}={value}')

                args.append(f'({", ".join(kwargs)})')
            else:
                args.append('()')
        elif func_type == 'assign':
            value = get_value(self.parWidgets[0])
            args.append(value)
        self.codeLabel.setText(''.join(args))

    def insert_code(self):
        self.codeEditor.insertPlainText(self.codeLabel.text())


class ToolsWidget(QTabWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.getnativeWidget = GetnativeWidget(DESCALE, AVISOURCE, FFMS2, LSMASH, IMWRI, self)
        self.vapoursynthWidget = VapourSynthWidget(self)
        self.addTab(self.vapoursynthWidget, 'VS Codes')
        self.addTab(self.getnativeWidget, 'GetNative')

    def init_font(self, font):
        self.getnativeWidget.init_font(font)
        self.tabBar().setFont(font)

    def init_language(self):
        self.getnativeWidget.init_language()
