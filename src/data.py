import pickle
import json
from PySide6.QtCore import QSettings, QDir, QFileInfo, QDateTime, QFile
from PySide6.QtWidgets import QApplication, QWidget, QGraphicsDropShadowEffect, QMessageBox, QFileDialog, QSplashScreen
from PySide6.QtGui import QIcon, QPixmap, QImage, QColor, QFont
from enum import IntEnum
import tools.vapoursynth.vapoursynth as vs
from locale import getdefaultlocale
# import vapoursynth as vs


class Default:
    __default_values = {
        'csv': '',
        'analysis-save': '',
        'frame-dup': False,
        'dup-threshold': 70,
        'stats': '',
        'pools': '',
        'numa-pools': '',
        'dolby-vision-rpu': '',
        'zones': '',
        'refine-mv-type': '',
        'analysis-load': '',
        'analysis-reuse-file': 'x265_analysis.dat',
        'dhdr10-info': '',
        'lambda-file': '',
        'zonefile': '',
        'qpfile': '',
        'scaling-list': '',
        'master-display': '',
        'max-cll': '',
        'cll': True,
        'nalu-file': '',
        'custom': '',
        'log-level': 3,
        'csv-log-level': 0,
        'input-depth': 0,
        'input-csp': 1,
        'fps': '',
        'interlace': 0,
        'tune': 0,
        'profile': 0,
        'level-idc': 0,
        'output-depth': 0,
        'encoding mode': 0,
        'ctu': 0,
        'min-cu-size': 2,
        'max-tu-size': 0,
        'me': 1,
        'ctu-info': 0,
        'asm': 0,
        'qg-size': 0,
        'sar': '',
        'overscan': 0,
        'videoformat': 0,
        'range': 0,
        'colorprim': 0,
        'transfer': 0,
        'colormatrix': 0,
        'dolby-vision-profile': 0,
        'hash': 0,
        'progress': True,
        'dither': False,
        'ssim': False,
        'psnr': False,
        'high-tier': True,
        'allow-non-conformance': False,
        'uhd-bd': False,
        'const-vbv': False,
        'slow-firstpass': True,
        'multi-pass-opt-analysis': False,
        'multi-pass-opt-distortion': False,
        'strict-cbr': False,
        'rc-grain': False,
        'limit-modes': False,
        'rect': False,
        'amp': False,
        'early-skip': True,
        'rskip': 1,
        'rskip-edge-threshold': 5,
        'splitrd-skip': False,
        'fast-intra': False,
        'b-intra': False,
        'cu-lossless': False,
        'tskip-fast': False,
        'rd-refine': False,
        'refine-ctu-distortion': 0,
        'dynamic-refine': False,
        'refine-mv': False,
        'tskip': False,
        'ssim-rd': False,
        'temporal-mvp': True,
        'weightp': True,
        'weightb': False,
        'analyze-src-pics': False,
        'hme': False,
        'hme-search1': 0,
        'hme-search2': 1,
        'hme-search3': 2,
        'hme-range1': 16,
        'hme-range2': 32,
        'hme-range3': 48,
        'hist-scenecut': True,
        'hist-threshold': 0.01,
        'strong-intra-smoothing': True,
        'constrained-intra': False,
        'open-gop': True,
        'intra-refresh': False,
        'b-pyramid': True,
        'fades': False,
        'wpp': True,
        'pmode': False,
        'pme': False,
        'copy-pic': True,
        'aq-motion': False,
        'cutree': True,
        'signhide': True,
        'deblock': True,
        'sao': True,
        'sao-non-deblock': False,
        'limit-sao': False,
        'selective-sao': 0,
        'hdr10': False,
        'hdr10-opt': False,
        'dhdr10-opt': False,
        'annexb': True,
        'repeat-headers': False,
        'aud': False,
        'hrd': False,
        'hrd-concat': False,
        'info': True,
        'temporal-layers': False,
        'vui-timing-info': True,
        'vui-hrd-info': True,
        'opt-qp-pps': False,
        'opt-ref-list-length-pps': False,
        'multi-pass-opt-rps': False,
        'opt-cu-delta-qp': False,
        'idr-recovery-sei': False,
        'single-sei': False,
        'width': 0,
        'height': 0,
        'seek': 0,
        'frames': 0,
        'chunk-start': 0,
        'chunk-end': 0,
        'field': False,
        'ref': 3,
        'bitrate': 1000,
        'vbv-bufsize': 0,
        'vbv-maxrate': 0,
        'min-vbv-fullness': 50,
        'max-vbv-fullness': 80,
        'qp': 16,
        'qpstep': 4,
        'qpmin': 0,
        'qpmax': 69,
        'pass': 0,
        'rd': 3,
        'limit-refs': 3,
        'analysis-save-reuse-level': 5,
        'analysis-load-reuse-level': 5,
        'scale-factor': 0,
        'refine-intra': 0,
        'refine-inter': 0,
        'rdoq-level': 0,
        'tu-intra-depth': 1,
        'tu-inter-depth': 1,
        'limit-tu': 0,
        'nr-intra': 0,
        'nr-inter': 0,
        'rdpenalty': 0,
        'dynamic-rd': 0,
        'max-merge': 2,
        'subme': 2,
        'merange': 57,
        'keyint': 250,
        'min-keyint': 0,
        'scenecut': 40,
        'radl': 0,
        'rc-lookahead': 20,
        'gop-lookahead': 0,
        'lookahead-slices': 8,
        'lookahead-threads': 0,
        'b-adapt': 2,
        'bframes': 4,
        'bframe-bias': 0,
        'force-flush': 0,
        'frame-threads': 0,
        'slices': 1,
        'aq-mode': 2,
        'cbqpoffs': 0,
        'crqpoffs': 0,
        'tC offset': 0,
        'Beta offset': 0,
        'displayWindowSpinL': 0,
        'displayWindowSpinT': 0,
        'displayWindowSpinR': 0,
        'displayWindowSpinB': 0,
        'chromaloc': -1,
        'min-luma': -1,
        'max-luma': -1,
        'atc-sei': -1,
        'pic-struct': -1,
        'log2-max-poc-lsb': 8,
        'crf': 28.0,
        'crf-max': -0.1,
        'crf-min': -0.1,
        'vbv-init': 0.9,
        'vbv-end': 0.0,
        'vbv-end-fr-adj': 0.0,
        'psy-rd': 2.0,
        'psy-rdoq': 0.0,
        'scenecut-bias': 5.0,
        'aq-strength': 1.0,
        'hevc-aq': False,
        'qp-adaptation-range': 1.0,
        'scenecut-aware-qp': 0,
        'masking-strength': '',
        'vbv-live-multi-pass': False,
        'ipratio': 1.4,
        'pbratio': 1.3,
        'qcomp': 0.6,
        'qblur': 0.5,
        'cplxblur': 20.0,
        'max-ausize-factor': 1.0,
        'lowpass-dct': False,
        'recon': '',
        'recon-depth': 7,
        'recon-y4m-exec': '',
        'svt': False,
        'svt-hme': True,
        'svt-search-width': 0,
        'svt-search-height': 0,
        'svt-compressed-ten-bit-format': False,
        'svt-speed-control': False,
        'svt-preset-tuner': -1,
        'svt-hierarchical-level': 3,
        'svt-base-layer-switch-mode': 0,
        'svt-pred-struct': 2,
        'svt-fps-in-vps': False
        }

    def copy(self):
        return self.__default_values.copy()

    def __getitem__(self, item: str) -> ...:
        return self.__default_values[item]

    def keys(self):
        return self.__default_values.keys()


class Partial:
    __slots__ = "func", "args", "keywords", "__dict__", "__weakref__"

    def __new__(cls, func, /, *args, **keywords):
        if not callable(func):
            raise TypeError("the first argument must be callable")

        if isinstance(func, Partial):
            args = func.args + args
            keywords = {**func.keywords, **keywords}
            func = func.func

        self = super(Partial, cls).__new__(cls)

        self.func = func
        self.args = args
        self.keywords = keywords
        return self

    def __call__(self, /, *args, **keywords):
        keywords = {**self.keywords, **keywords}
        return self.func(*self.args, *args, **keywords)


class Settings:
    __language_code = {'zh_CN': '简体中文', 'eng': 'English'}

    def __init__(self):
        self.conf = QSettings('setting.ini', QSettings.Format.IniFormat)

        self.cmdLanguage = self.conf.value(self.key_section.get('cmdLanguage'), 'zh_CN')
        self.language = self.conf.value(self.key_section.get('language'), 'zh_CN')
        self.fontFamily = self.conf.value(self.key_section.get('fontFamily'), 'Arial')
        self.cacheMethod = self.conf.value(self.key_section.get('cacheMethod'), '')
        self.encodeCacheDir = self.conf.value(self.key_section.get('encodeCacheDir'), '')
        self.recentSavFile = self.conf.value(self.key_section.get('recentSavFile'), '')
        self.recentDir = self.conf.value(self.key_section.get('recentDir'), '')
        self.autoLoadSav = self.conf.value(self.key_section.get('autoLoadSav'), self.default['autoLoadSav'])
        self.loadVideoCmd = self.conf.value(self.key_section.get('loadVideoCmd'), self.default['loadVideoCmd'])
        self.svt = self.conf.value(self.key_section.get('svt'), self.default['autoLoadSav'])
        self.rememberRecentDir = self.conf.value(self.key_section.get('rememberRecentDir'),
                                                 self.default['rememberRecentDir'])
        self.recentDir = self.conf.value(self.key_section.get('recentDir'), QDir.currentPath())
        self.cacheMethod = self.conf.value(self.key_section.get('cacheMethod'), self.default['cacheMethod'])
        self.preload = self.conf.value(self.key_section.get('preload'), self.default['preload'])
        self.preloadTimeout = self.conf.value(self.key_section.get('preloadTimeout'), self.default['preloadTimeout'])
        self.encodeTimeout = self.conf.value(self.key_section.get('encodeTimeout'), self.default['encodeTimeout'])
        self.rawHevcExt = self.conf.value(self.key_section.get('rawHevcExt'), self.default['rawHevcExt'])
        self.parseSpeed = self.conf.value(self.key_section.get('parseSpeed'), self.default['parseSpeed'])

        with open('template.vpy', 'a+', encoding='utf-8', errors='replace') as f:
            f.seek(0, 0)
            if not (vpy := f.read()):
                vpy = 'import vapoursynth as vs\n' \
                      'core = vs.core\n' \
                      'core.max_cache_size = 2048\n' \
                      'core.num_threads = 8\n\n' \
                      'clip = core.ffms2.Source(r"<path>")\n' \
                      'clip.set_output()\n'
            self.vpyTemplate = vpy
        with open('template.avs', 'a+', encoding='utf-8', errors='replace') as f:
            f.seek(0, 0)
            if not (avs := f.read()):
                avs = 'AddAutoloadDir("PROGRAMDIR") \n' \
                      'FFVideoSource("<path>", colorspace="YUV420P8")\n'
            self.avsTemplate = avs

    def __setattr__(self, key: str, value: str):
        if key in (key_file := {'avsTemplate': 'template.avs', 'vpyTemplate': 'template.vpy'}):
            with open(key_file.get(key), 'w', encoding='utf-8') as f:
                f.write(value)
            self.__dict__[key] = value
        elif key in ('conf', 'language', 'cmdLanguage', 'fontFamily', 'recentSavFile', 'encodeCacheDir',
                     'recentDir', 'rawHevcExt'):
            self.__dict__[key] = value
            self.conf.setValue(self.key_section.get(key), value)
        elif key == 'parseSpeed':
            try:
                if 1 >= float(value) >= 0:
                    value = float(value)
                else:
                    value = self.default[key]
            except ValueError:
                value = self.default[key]
            self.__dict__[key] = value
            self.conf.setValue(self.key_section.get(key), value)
        elif key in ('svt', 'autoLoadSav', 'loadVideoCmd', 'rememberRecentDir', 'cacheMethod', 'preload'):
            try:
                if int(value) == 0:
                    value = 0
                else:
                    value = 1
            except ValueError:
                value = self.default[key]
            value = min(max(0, value), 99999)
            self.__dict__[key] = value
            self.conf.setValue(self.key_section.get(key), value)
        elif key in ('preloadTimeout', 'encodeTimeout'):
            try:
                value = int(value)
            except ValueError:
                value = self.default[key]
            self.__dict__[key] = value
            self.conf.setValue(self.key_section.get(key), value)
        else:
            print(f'{key=}错误')

    @property
    def default(self) -> dict:
        return {'svt': 0, 'autoLoadSav': 1, 'loadVideoCmd': 0, 'rememberRecentDir': 1, 'cacheMethod': 0,
                'preload': 1, 'preloadTimeout': 500, 'encodeTimeout': 500, 'parseSpeed': 0.5,
                'rawHevcExt': 'h265'}

    @property
    def language_codes(self) -> dict[str, str]:
        return self.__language_code

    @property
    def key_section(self) -> dict[str, str]:
        return {'language': 'Display/language',
                'cmdLanguage': 'Display/cmdLanguage',
                'fontFamily': 'Display/fontFamily',
                'recentSavFile': 'Recent/cmdSaveFile',
                'encodeCacheDir': 'Encode/encodeCacheDir',
                'recentDir': 'Recent/recentDir',
                'svt': 'Commands/svt',
                'autoLoadSav': 'Commands/autoLoadSav',
                'loadVideoCmd': 'Commands/loadVideoCmd',
                'rememberRecentDir': 'Recent/rememberRecentDir',
                'cacheMethod': 'Encode/cacheMethod',
                'preload': 'Encode/preload',
                'encodeTimeout': 'Encode/encodeTimeout',
                'preloadTimeout': 'Encode/preloadTimeout',
                'parseSpeed': 'MediaInfo/parseSpeed',
                'rawHevcExt': 'Encode/rawHevcExt'}


class LanguageItem:
    def __init__(self, key: str, parent=None):
        self.__parent: Language = parent
        self.__key = key

    def __setattr__(self, key: str, value):
        if type(value) in (str, tuple):
            self.__dict__[key] = value
        elif type(value) == dict:
            language = LanguageItem(key, self)
            for sub_key, sub_value in value.items():
                setattr(language, sub_key, sub_value)
            self.__dict__[key] = language
        elif key in ('_LanguageItem__key', '_LanguageItem__parent'):
            super().__setattr__(key, value)
        else:
            raise TypeError('value必须是str, tuple或dict')

    def __getattr__(self, item: str):
        _dict = super().__getattribute__('__dict__')
        if item in _dict:
            return _dict[item]
        elif value := self.get_optional(item):
            return value
        else:
            print(f'Language error: 未找到{item}')
            return item

    def __sizeof__(self) -> int:
        size = super().__sizeof__()
        for key, value in self.__dict__.items():
            size += value.__sizeof__()
        return size

    @property
    def parent(self):
        return self.__parent

    @property
    def key(self):
        return self.__key

    def get_optional(self, item: str) -> str:
        parent = self.__parent
        keys = [item]
        while isinstance(parent, LanguageItem):
            keys.append(parent.key)
            parent = parent.parent
        for key in reversed(keys):
            parent = getattr(parent, key)
        return parent


class Language:
    def __init__(self, optional=None):
        self.__optional: Language = optional

    def __setattr__(self, key: str, value):
        if type(value) in (str, tuple):
            self.__dict__[key] = value
        elif type(value) == dict:
            language_item = LanguageItem(key, self)
            for sub_key, sub_value in value.items():
                setattr(language_item, sub_key, sub_value)
            self.__dict__[key] = language_item
        elif key == '_Language__optional':
            super().__setattr__(key, value)
        else:
            raise TypeError('value必须是str, tuple或dict')

    def __getattr__(self, item: str):
        _dict = self.__dict__
        if item in _dict:
            return _dict[item]
        elif self.__optional and (value := getattr(self.__optional, item)):
            return value
        else:
            print(f'Language error: 未找到{item}')
            return item

    def __sizeof__(self) -> int:
        size = super().__sizeof__()
        for key, value in self.__dict__.items():
            size += value.__sizeof__()
        return size

    def load(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    def reset(self):
        optional = self.__optional
        self.__dict__.clear()
        self.__optional = optional


class Track:
    __slots__ = 'codec_id', 'track_type', 'track_id', 'track_path'

    def __init__(self, codec_id: str, track_type: str, track_id: str, track_path: str):
        self.codec_id = codec_id
        self.track_type = track_type
        self.track_id = track_id
        self.track_path = track_path

    def to_dict(self) -> dict[str, str]:
        return {'codec_id': self.codec_id, 'track_type': self.track_type,
                'track_id': self.track_id, 'track_path': self.track_path}

    def from_dict(self, data: dict):
        self.codec_id = data['codec_id']
        self.track_type = data['track_type']
        self.track_id = data['track_id']
        self.track_path = data['track_path']


class Message:
    def __init__(self):
        self.__data: list[tuple[str, list[str]]] = []

    def __getitem__(self, index: int) -> tuple:
        return self.__data[index]

    def __bool__(self) -> bool:
        return True if self.__data else False

    def to_list(self) -> list:
        return self.__data

    def from_list(self, data: list[tuple[str, list[str]]]):
        self.__data.clear()
        self.__data.extend(data)

    def add_top(self, header: str, msgs: list = None):
        sub_msgs = msgs if msgs else []
        self.__data.append((header, sub_msgs))

    def add_msg(self, msg: str):
        if self.__data:
            self.__data[-1][1].append(msg)
        else:
            raise ValueError('Message 必须有header才允许add_msg')

    def flush_msg(self, msg: str):
        if self.__data:
            if sub_msgs := self.__data[-1][1]:
                sub_msgs[-1] = msg
            else:
                sub_msgs.append(msg)
        else:
            raise ValueError('Message 必须有header才允许flush_msg')

    def clear(self):
        self.__data.clear()


class Task:
    class States(IntEnum):
        WAITING = 0
        RUNNING = 1
        FINISH = 2
        ABORT = 3
        ERROR = 4
        RETRY = 5
        WARNING = 6

    def __init__(self,
                 input_path: str,
                 output_path: str,
                 input_type: str,
                 status: States,
                 start: str,
                 end: str,
                 command: str,
                 *,
                 file_name: str,
                 parent):
        self.parent: TaskList = parent
        self.parent.append(self)
        self.file_name = file_name
        self.__input = input_path
        self.__output = output_path
        self.__type = input_type
        status = self.States(status) if type(status) == int else status
        self.__status = status
        self.__start = start
        self.__end = end
        self.__command = command
        self.__message = Message()
        self.__tracks: list[Track] = []
        self.totalFrames: int = 0

    def to_tuple(self) -> tuple:
        return (self.__input, self.__output, self.type,
                self.status_code, self.__start, self.__end, self.__command)

    @property
    def input(self) -> str:
        return self.__input

    @input.setter
    def input(self, value: str) -> None:
        self.__input = value
        self.parent.set_value(self, 0, value)

    @property
    def output(self) -> str:
        return self.__output

    @output.setter
    def output(self, value: str) -> None:
        self.__output = value
        self.parent.set_value(self, 1, value)

    @property
    def type(self) -> str:
        return self.__type

    @type.setter
    def type(self, value: str) -> None:
        if value in ('vpy', 'avs', 'yuv', 'bat', 'raw'):
            self.__type = value
            self.parent.set_value(self, 2, value)
        else:
            raise ValueError('type 必须是vpy, avs, yuv, bat, raw中的一个')

    @property
    def status(self) -> States:
        return self.__status

    @status.setter
    def status(self, value) -> None:
        if value in range(len(self.States)):
            self.__status = self.States(value)
            self.parent.set_value(self, 3, LANG_UI_TXT.EncodeWidget.state[value])
        elif isinstance(value, self.States):
            self.__status = value
            self.parent.set_value(self, 3, LANG_UI_TXT.EncodeWidget.state[value.value])
        else:
            raise ValueError(f'value必须是0-{len(self.States) - 1}数字或Task.States符')

    @property
    def status_code(self) -> int:
        return int(self.__status)

    @property
    def start(self) -> str:
        return self.__start

    @start.setter
    def start(self, value: str) -> None:
        self.__start = value
        self.parent.set_value(self, 4, value)

    @property
    def end(self) -> str:
        return self.__end

    @end.setter
    def end(self, value: str) -> None:
        self.__end = value
        self.parent.set_value(self, 5, value)

    @property
    def command(self) -> str:
        return self.__command

    @command.setter
    def command(self, value: str) -> None:
        self.__command = value
        self.parent.set_value(self, 6, value)

    @property
    def message(self):
        return self.__message

    @property
    def tracks(self):
        return self.__tracks

    def save(self, file_name: str = None):
        if file_name:
            self.file_name = file_name

        data = {'input': self.__input,
                'output': self.__output,
                'type': self.__type,
                'status': self.status.value,
                'start': self.__start,
                'end': self.__end,
                'command': self.__command,
                'message': self.__message.to_list(),
                'tracks': [track.to_dict() for track in self.__tracks]}
        with open(TASK_DIR.absoluteFilePath(self.file_name), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)


class TaskList:
    __cur_task = None
    __data: list[Task] = []

    def __init__(self, parent):
        self.parent = parent

    def __getitem__(self, index: int) -> Task:
        return self.__data[index]

    def remove(self, index: int) -> bool:
        if index == self.cur_index:
            return False
        else:
            del self.__data[index]
            return True

    def __len__(self) -> int:
        return len(self.__data)

    def __iter__(self):
        return self.__data.__iter__()

    def append(self, task: Task) -> None:
        if not isinstance(task, Task):
            raise TypeError
        elif task in self:
            print(f'[warning]{task}已经在人物列表里了，忽略添加')
        else:
            self.__data.append(task)
            task.parent = self

    def clear(self):
        self.__data.clear()
        self.__cur_task = None

    def index(self, __value, __start: int = 0, __stop: int = None, /) -> int:
        if __value in self.__data:
            if __stop is None:
                return self.__data.index(__value, __start)
            else:
                return self.__data.index(__value, __start, __stop)
        else:
            return -1

    def pop(self, __index: int = -1) -> Task:
        item = self.__data.pop(__index)
        if __index == self.cur_index:
            print('删除了正在运行的任务')
        return item

    @property
    def cur_task(self) -> Task:
        return self.__cur_task

    @cur_task.setter
    def cur_task(self, task: Task):
        if isinstance(task, Task):
            if task in self:
                self.__cur_task = task
            else:
                raise ValueError
        elif task is None:
            self.__cur_task = task
        else:
            raise TypeError

    @property
    def cur_index(self) -> int:
        if self.__cur_task:
            return self.index(self.__cur_task)
        else:
            return -1

    def set_value(self, task: Task, column: int, value: str):
        if task := self.parent.taskTableWidget.item(self.index(task), column):
            task.setText(value)
            task.setToolTip(value)

    def save(self):
        TASK_DIR.refresh()
        for path in TASK_DIR.entryList():
            TASK_DIR.remove(path)
        for row, task in enumerate(self.__data, start=1):
            task.save(f'job{row:03}.task')


class Commands:
    __keys = ('input-depth', 'input-res', 'input-csp', 'fps', 'interlace', 'seek', 'frame-dup', 'dup-threshold',
              'frames', 'dither', 'output-depth', 'chunk-start', 'chunk-end', 'field', 'log-level', 'progress', 'csv',
              'csv-log-level', 'ssim', 'psnr', 'asm', 'frame-threads', 'pools', 'wpp', 'pmode', 'pme', 'preset',
              'tune', 'slices', 'copy-pic', 'profile', 'level-idc', 'high-tier', 'ref', 'allow-non-conformance',
              'uhd-bd', 'rd', 'ctu', 'min-cu-size', 'limit-refs', 'limit-modes', 'rect', 'amp', 'early-skip',
              'rskip', 'rskip-edge-threshold', 'splitrd-skip', 'fast-intra', 'b-intra', 'cu-lossless', 'tskip-fast',
              'rd-refine', 'analysis-save', 'analysis-load', 'analysis-reuse-file', 'analysis-save-reuse-level',
              'analysis-load-reuse-level', 'refine-ctu-distortion', 'refine-mv-type', 'scale-factor', 'refine-intra',
              'refine-inter', 'dynamic-refine', 'refine-mv', 'rdoq-level', 'tu-intra-depth', 'tu-inter-depth',
              'limit-tu', 'nr-intra', 'nr-inter', 'tskip', 'rdpenalty', 'max-tu-size', 'dynamic-rd', 'ssim-rd',
              'max-merge', 'me', 'subme', 'merange', 'temporal-mvp', 'weightp', 'weightb', 'analyze-src-pics',
              'hme', 'hme-search', 'hme-range', 'strong-intra-smoothing', 'constrained-intra', 'psy-rd', 'psy-rdoq',
              'open-gop', 'keyint', 'min-keyint', 'scenecut', 'scenecut-bias', 'hist-scenecut', 'hist-threshold',
              'radl', 'ctu-info', 'intra-refresh', 'rc-lookahead', 'gop-lookahead', 'lookahead-slices',
              'lookahead-threads', 'b-adapt', 'bframes', 'bframe-bias', 'b-pyramid', 'force-flush', 'fades',
              'bitrate', 'crf', 'crf-max', 'crf-min', 'vbv-bufsize', 'vbv-maxrate', 'vbv-init', 'vbv-end',
              'vbv-end-fr-adj', 'min-vbv-fullness', 'max-vbv-fullness', 'vbv-live-multi-pass', 'qp', 'lossless',
              'aq-mode', 'aq-strength', 'aq-motion', 'qg-size', 'cutree', 'pass', 'stats', 'slow-firstpass',
              'multi-pass-opt-analysis', 'multi-pass-opt-distortion', 'strict-cbr', 'cbqpoffs', 'crqpoffs',
              'ipratio', 'pbratio', 'qcomp', 'qpstep', 'qpmin', 'qpmax', 'rc-grain', 'const-vbv', 'qblur',
              'cplxblur', 'zones', 'zonefile', 'scenecut-aware-qp', 'masking-strength', 'signhide', 'qpfile',
              'scaling-list', 'lambda-file', 'max-ausize-factor', 'deblock', 'sao', 'sao-non-deblock', 'limit-sao',
              'selective-sao', 'sar', 'display-window', 'overscan', 'videoformat', 'range', 'colorprim', 'transfer',
              'colormatrix', 'chromaloc', 'master-display', 'max-cll', 'cll', 'hdr10', 'hdr10-opt', 'dhdr10-info',
              'dhdr10-opt', 'min-luma', 'max-luma', 'nalu-file', 'atc-sei', 'pic-struct', 'annexb', 'repeat-headers',
              'aud', 'hrd', 'hrd-concat', 'dolby-vision-profile', 'dolby-vision-rpu', 'info', 'hash',
              'temporal-layers', 'log2-max-poc-lsb', 'vui-timing-info', 'vui-hrd-info', 'opt-qp-pps',
              'opt-ref-list-length-pps', 'multi-pass-opt-rps', 'opt-cu-delta-qp', 'idr-recovery-sei', 'single-sei',
              'lowpass-dct', 'recon', 'recon-depth', 'recon-y4m-exec', 'custom', 'svt', 'svt-hme', 'svt-search-width',
              'svt-search-height', 'svt-compressed-ten-bit-format', 'svt-speed-control', 'svt-preset-tuner',
              'svt-hierarchical-level', 'svt-base-layer-switch-mode', 'svt-pred-struct', 'svt-fps-in-vps')
    __data = dict.fromkeys(__keys, '')

    def __getitem__(self, key: str) -> str:
        if key not in self.__keys:
            print(f'未找到{key}')
        else:
            return self.__data[key]

    def __setitem__(self, key: str, value: str):
        if key not in self.__keys:
            raise KeyError(f'未找到{key}')
        else:
            self.__data[key] = value

    def __iter__(self):
        return self.__keys.__iter__()

    def __str__(self) -> str:
        return ' '.join([value.strip() for value in self.values() if value])

    @property
    def data(self) -> dict:
        return self.__data

    def get(self, item: str, default=None) -> str:
        return self.__data.get(item, default)

    def reset(self):
        for key in self.__keys:
            self[key] = ''

    def keys(self) -> tuple:
        return self.__keys

    def values(self):
        return self.__data.values()

    def items(self):
        return self.__data.items()


def set_icon(data: bytes) -> QIcon:
    return QIcon(QPixmap.fromImage(QImage.fromData(data)))


def get_size(size) -> str:
    if size < 1024:
        value = f'{round(size, 3)} B'
    elif 1024 <= size < 1048576:
        value = f'{round(size / 1024, 3)} KB'
    elif 1048576 <= size < 1073741824:
        value = f'{round(size / 1048576, 3)} MB'
    else:
        value = f'{round(size / 1073741824, 3)} GB'
    return value


def get_time() -> str:
    return QDateTime.currentDateTime().toString('yyyy-MM-dd hh:mm:ss')


def shadow(widget: QWidget):
    effect = QGraphicsDropShadowEffect()
    effect.setBlurRadius(10)
    effect.setOffset(0, 0)
    effect.setColor(QColor(220, 220, 220))
    widget.setGraphicsEffect(effect)


def move_to_middle(widget: QWidget):
    screen = QApplication.primaryScreen().size()
    widget.move((screen.width() - widget.width()) // 2,
                (screen.height() - widget.height()) // 2)


def load_css() -> str:
    if CSS_DIR.exists():
        css_list = []
        for file_info in CSS_DIR.entryInfoList(filters=QDir.Filter.Files | QDir.Filter.Readable):
            with open(file_info.absoluteFilePath(), 'r', encoding='utf-8') as f:
                css_list.append(f.read())
        return ''.join(css_list)
    else:
        return ''


def check_language(data) -> bool:
    if isinstance(data, dict):
        for key, value in data.items():
            if not isinstance(key, str) or not check_language(value):
                return False
    elif isinstance(data, tuple):
        for value in data:
            if not check_language(value):
                return False
    elif not isinstance(data, str):
        return False
    return True


def load_languages() -> list[tuple[str, str, QFile]]:
    languages = []

    for file_name in LANGUAGE_DIR.entryList():
        file = QFile(LANGUAGE_DIR.absoluteFilePath(file_name))
        if file.open(QFile.OpenModeFlag.ReadOnly):
            try:
                data: dict = pickle.loads(file.readAll().data())
                file.seek(0)
                if isinstance(data, dict):
                    language_code: str = data.get('language_code')
                    if not isinstance(language_code, str):
                        raise TypeError
                    language_name = SETTINGS.language_codes.get(language_code, '')
                    ui_language = data.get('ui_language')
                    cmd_language = data.get('cmd_language')
                else:
                    raise TypeError
            except (pickle.UnpicklingError, TypeError):
                continue
            else:
                if language_code and language_name \
                        and check_language(ui_language) \
                        and check_language(cmd_language):
                    languages.append((language_name, language_code, file))
    return languages


def check_permission(path: str) -> int:
    status = 0b00
    if QFileInfo(path).isReadable():
        status |= 0b01
    if QFileInfo(path).isWritable():
        status |= 0b10
    return status


def check_task_dir(splash: QSplashScreen) -> bool:
    while True:
        msgs = []
        if TASK_DIR.exists() or WORK_DIR.mkpath(TASK_DIR.absolutePath()):
            if not (p := check_permission(TASK_DIR.absolutePath())) & 0b01:
                msgs.append('无法读取')
            if not p & 0b10:
                msgs.append('无法写入')
        else:
            msgs.append('不存在且无法创建')
        if msgs:
            r = QMessageBox.question(splash,
                                     'Error',
                                     '任务文件夹：{0}\n{1}\n是否重新选择路径'.format(TASK_DIR.absolutePath(), '\n'.join(msgs)),
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.Yes)
            if r == QMessageBox.StandardButton.Yes:
                if path := QFileDialog.getExistingDirectory(splash,
                                                            '选择',
                                                            SETTINGS.recentDir)[0]:
                    TASK_DIR.setPath(path)
            else:
                return False
        else:
            break
    return True


class Filter:
    __slots__ = '__name', '__default_paths', '__identifier'

    def __init__(self, name, identifier: str, default_paths: list[QFileInfo] = None):
        self.__name = name
        if default_paths is None:
            default_paths = []
        self.__default_paths = default_paths
        self.__identifier = identifier

    def __bool__(self) -> bool:
        return self.is_enable()

    def name(self) -> str:
        return self.__name

    def identifier(self) -> str:
        return self.__identifier

    def check(self, ex_paths: list[QFileInfo] = None) -> bool:
        if self.__identifier in CORE.get_plugins():
            return True
        else:
            if ex_paths is None:
                ex_paths = []
            for file_info in ex_paths + self.__default_paths:
                try:
                    CORE.std.LoadPlugin(file_info.absoluteFilePath())
                except vs.Error:
                    continue
                else:
                    if self.__identifier in CORE.get_plugins():
                        return True
            else:
                return False

    def is_enable(self) -> bool:
        return True if self.__identifier in CORE.get_plugins() else False


CORE = vs.core
CORE.max_cache_size = 512
CORE.num_threads = 1

DEFAULT = Default()
COMMANDS = Commands()

DEFAULT_UI_TXT = Language()
DEFAULT_CMD_TXT = Language()

LANG_UI_TXT = Language(DEFAULT_UI_TXT)
CMD_LANG_TXT = Language(DEFAULT_CMD_TXT)

WORK_DIR = QDir.current()
TASK_DIR = QDir(r'./tasks')
LANGUAGE_DIR = QDir(r'./language', '*.language')
CSS_DIR = QDir(r'./css')
VSFUNCS_DIR = QDir(r'./VSfuncs', '*.xml')
SETTINGS = Settings()

FONT = QFont(SETTINGS.fontFamily)
FONT_SIZE = 14

SYSTEM_CODEC = getdefaultlocale()[1]
VIDEO_EXTS = ('mp4', 'mkv')

SAVE_VERSION = '2.1.0'

ENCODE_CACHE_DIR = QDir()

X265_PATH = [QFileInfo(path) for path in ('./tools/x265/x265-AVX2.exe',
                                          './tools/x265/x265-AVX.exe',
                                          './tools/x265/x265.exe',)]
VSPIPE_PATH = [QFileInfo(path) for path in ('./tools/vapoursynth/vspipe.exe',)]
AVS4X26X_PATH = [QFileInfo(path) for path in ('./tools/avisynth+/avs4x26x.exe',)]
MKVMERGE_PATH = [QFileInfo(path) for path in ('./tools/mkvmerge/mkvmerge.exe',)]
MP4BOX_PATH = [QFileInfo(path) for path in ('./tools/mp4box/mp4box.exe',)]
MEDIAINFO_PATH = [QFileInfo(path) for path in ('./tools/MediaInfo/MediaInfo.dll',)]
LSMASH_PATH = [QFileInfo(path) for path in ('./tools/vapoursynth/vapoursynth64/plugins/vslsmashsource.dll',)]
FFMS2_PATH = [QFileInfo(path) for path in ('./tools/vapoursynth/vapoursynth64/plugins/ffms2.dll',)]
AVISOURCE_PATH = [QFileInfo(path) for path in ('./tools/vapoursynth/vapoursynth64/coreplugins/avisource.dll',)]
IMWRI_PATH = [QFileInfo(path) for path in ('./tools/vapoursynth/vapoursynth64/coreplugins/libimwri.dll',)]
DESCALE_PATH = [QFileInfo(path) for path in ('./tools/vapoursynth/vapoursynth64/plugins/libdescale.dll',)]

X265 = QFileInfo()
VSPIPE = QFileInfo()
AVS4X26X = QFileInfo()
MKVMERGE = QFileInfo()
MP4BOX = QFileInfo()
MEDIAINFO = QFileInfo()

LSMASH = Filter('lsmas', 'systems.innocent.lsmas', LSMASH_PATH)
FFMS2 = Filter('ffms2', 'com.vapoursynth.ffms2', FFMS2_PATH)
AVISOURCE = Filter('avisource', 'com.vapoursynth.avisource', AVISOURCE_PATH)
IMWRI = Filter('imwri', 'com.vapoursynth.imwri', IMWRI_PATH)
DESCALE = Filter('descale', 'tegaf.asi.xe', DESCALE_PATH)

BASENAME_CODE = '<base_name>'
SUFFIX_CODE = '<suffix_name>'
FILENAME_CODE = '<file_name>'
PATH_CODE = '<path>'
