from helps import helps
import time
import ver

today = time.strftime("%Y%m%d", time.localtime())

All = {
    'cmd_language': {'comboBoxes': {'csv-log-level': ('0.摘要', '1.帧级日志记录', '2.含性能统计的帧级日志'), 'input-depth': '未指定',
                                    'interlace': ('逐行扫描', 'tff', 'bff'),
                                    'level-idc': '0（自动）',
                                    'log-level': ('-1.禁用', '0.错误', '1.警告', '2.信息', '3.调试', '4.完整'),
                                    'output-depth': ('未指定', '8', '10', '12'),
                                    'tune': ('无', 'psnr', 'ssim', 'grain', '零延迟', '快速解码', '动画')},
                     'profileWidgetLabels': (
                         'tune', '编码模式', '码率(kbps)', 'pass', 'CRF', 'QP', '输出位深', 'profile', 'level', 'ref',
                         'limit-refs',
                         '输入位深', '宽度', '高度', '色度采样', '帧率', '交错', '跳过(帧)', 'dup-threshold', '视频帧数', 'chunk-start',
                         'chunk-end'),
                     'titles': (
                         '预设', '编码模式', '质量报告度量', '配置', 'L0参考', '一致性检测', '蓝光格式支持', '输入/输出设置', 'Pass', '量化参数(QP)',
                         '恒定质量(CRF)',
                         'VBV缓冲',
                         '性能', '并行性', 'RDO', '四叉树的大小和深度', '运动分区', '速率-失真分析量化', '跳过(Skip)', '改善(Refine)', '分析(Analysis)',
                         '时间/动作搜索',
                         'Look ahead', 'GOP', '插入', '帧间/帧内', 'B帧', '其他', '自适应量化', 'SAO', '解块', '偏移量', '区域', '模糊', '量化',
                         '其他',
                         '图像大小相关',
                         '高动态范围图像', '颜色相关', '其他', 'SVT-HEVC', 'HRD', '最优化', '视频可用性信息', 'DCT近似值', '杜比视界', '调试', '日志',
                         '其他', '自定义参数')},
    'ui_language': {
        'AboutWidget': {
            'Headers': ('程序', '版本', '位数'),
            'Info': f'x265参数编辑器\n\n制作者：JasinChen\ne-mail: 402083306@qq.com\n版本：{ver.ver}',
            'Programs': (('x265', ver.x265, '64-bit'),
                         ('vspipe', ver.vspipe, '64-bit'),
                         ('avisynth+', ver.avisynth, '64-bit'),
                         ('mkvmerge', ver.mkvmerge, '64-bit'),
                         ('mp4box', ver.mp4box, '64-bit'),
                         ('MediaInfo', ver.MediaInfo, '64-bit'))},
        'BatchExportWidget': {'label': ('输入源', '输出视频', '批处理文件名'), 'title': '批量导出'},
        'EncodeWidget': {'TaskAppendWidget': ('输入文件', '输入文件预览', '输出格式', '输出文件', '命令行'),
                         'TaskOperationWidget': (
                             '任务过滤', '当前任务', '当前输入', '当前输出', '速率', '平均码率', '剩余时间', '当前帧', '错误后：', '完成后：'),
                         'abort': '中止',
                         'abort_all': '全部中止',
                         'action': (
                             '等待', '放弃', '编辑', '删除', '清空', '清空消息', '打开输入文件', '打开输入文件夹', '打开输出文件', '打开输出文件夹',
                             '导出批处理文件'),
                         'back_cur_task': '定位至正在运行的任务',
                         'cancel_plan': '取消计划', 'encoding': '编码',
                         'finish': '结束任务',
                         'indexing': '建立索引',
                         'merging': '混流',
                         'priority': (
                             'IdlePriority', 'LowestPriority', 'LowPriority', 'NormalPriority',
                             'HighPriority',
                             'HighestPriority', 'TimeCriticalPriority'),
                         'retry': ('不重试', '重试1次', '重试5次', '重试10次', '无限次重试'),
                         'shutdown': ('不采取任何操作', '关机', '关闭程序', '重启计算机', '睡眠'),
                         'state': ('等待', '运行', '完成', '放弃', '错误', '重试', '警告'),
                         'tab': ('添加任务', '管理/编码'),
                         'task': '任务',
                         'task_begin': '任务开始',
                         'task_finish': '任务完成',
                         'tasks': ('输入', '输出', '类型', '状态', '开始时间', '结束时间', '参数'),
                         'title': '编码视频'},
        'MediaInfoWidget': {
            'buttons': ('导入文件', '生成vpy', '生成avs', '批量生成vpy', '批量生成avs', '清空'),
            'info': '无可用信息',
            'reload': '重新加载'},
        'Messages': (

        ),
        'SettingWidget': {
            'auto_load_sav': '启动后自动加载sav文件',
            'avs': 'avs模板',
            'cache': '编码缓存路径',
            'cache_mode': '缓存模式',
            'cache_modes': ('将缓存文件置于固定文件夹', '将缓存文件置于输出文件夹'),
            'complete': ('将缓存文件置于固定文件夹', '将缓存文件置于输出文件夹'),
            'clear_cache_files': '清空缓存文件夹',
            'cmd': '命令行语言',
            'default_source_filter': '默认源滤镜',
            'default_source_filters': (
                '根据视频格式自动选择', 'FFMS2', 'LWLibavSource', 'LibavSMASHSource', 'AVISource'),
            'disable': '不可用',
            'enable': '可用',
            'encode_timeout': '编码超时（秒）',
            'font': '字体',
            'full': '显示额外的标签，包括电脑可识别的持续时间和大小',
            'file_name': '文件名+拓展名',
            'base_name': '文件名',
            'suffix': '文件拓展名',
            'path': '完整路径',
            'entry': '词条',
            'label': '语言',
            'load_video_cmd': '允许从hevc视频中加载编码信息',
            'need_restart': '重启程序以使设置生效',
            'raw_hevc_ext': 'raw-hevc扩展名',
            'parse_speed': '解析速度',
            'preload': '编码时预加载下一个任务以缩短任务用时（支持预加载vpy, avs）',
            'preload_timeout': '预加载超时（秒）',
            'reload': '重新载入程序',
            'remember_temp_dir': '记住上次访问的文件夹',
            'support_all': '强制支持所有视频格式输入',
            'support_all_tip': '只有自定义的x265才支持视频文件作为输入源，请确定你的x265是否支持',
            'svt': '允许使用svt-hevc（假如x265程序支持）',
            'tab': ('显示', '命令参数', '媒体信息', '编码', '程序'),
            'title': '设置', 'vpy': 'vpy模板'},
        'TaskEdit': {
            'header': ('编码格式', '类型', '轨道ID', '路径'),
            'label': ('输入', '输出', '参数'),
            'task_type': {'Audio': '音频', 'Menu': '章节', 'Text': '字幕'},
            'title': '任务编辑'},
        'ToolsWidget': {
            'getnative': {
                'ChartView': {'best': '最佳值', 'difference': '差值', 'height': '高度'},
                'aboutWidget': {
                    'labels': ('GetNative 3.0.0', '寻找被放大素材的原始大小（大部分为动画）',
                               '警告：本工具成功率离完美相距较远. 如果可以，请在同一个源中的不同帧进行测试。较亮的场景通常返回准确的结果。图像趋于有多组置信区间，所以结果也许可能错误。另外，由于目前实现的自动猜测，他不能自动识别1080p素材。',
                               'Author: Infiziert90',
                               'Website: https://github.com/Infiziert90/getnative'),
                    'title': '关于GetNative'},
                'ar': '纵横比',
                'b': '双立方-b',
                'c': '双立方-c',
                'frame': '帧',
                'groupboxes': ('输入', '预设', '核函数', '通用', '输出'),
                'helps': {'ar': '强制纵横比，仅用于变形的视频',
                          'b': 'bicubic缩放中的参数B',
                          'c': 'bicubic缩放中的参数C',
                          'frame': '指定一个帧进行分析（0为第一帧）',
                          'img': '强制指定输入文件为图像',
                          'kernel': '指定一个函数进行缩放',
                          'mask_out': '保存线条为png图像',
                          'max_h': '分析的最大高度',
                          'min_h': '分析的最小高度',
                          'plot_format': 'Format of the output image. Specify multiple formats separated by commas. Can be svg, png, pdf, rgba, jp(e)g, tif(f), and probably more',
                          'steps': 'This changes the way getnative will handle resolutions. Example steps=3 [500p, 503p, 506p ...]',
                          'taps': 'lanczos缩放中的参数taps', 'use': '指定源滤镜'},
                'input': '输入',
                'input_filter': '输入滤镜',
                'is_image': '输入文件为图片',
                'kernel': '核函数',
                'max_height': '最大高度',
                'min_height': '最小高度',
                'modes': ('无', '双线性(bilinear)', '双立方(bicubic)', 'lanczos', 'spline', '全部'),
                'output_dir': '输出文件夹',
                'output_mask': '输出线条',
                'stepping': '步进',
                'taps': 'Lanczos-taps',
                'task_running': '任务运行中'}},
        'button': {'Abort': '中止', 'Abort_all': '全部中止', 'Always_on_top': '置顶显示', 'Apply': '应用',
                   'Cancel': '取消',
                   'Close': '关闭', 'Confirm': '确定', 'Import_Audio': '导入音频', 'Import_Chapter': '导入章节',
                   'Import_Subtitle': '导入字幕', 'Load': '导入', 'Merge': '混流', 'OK': '确定', 'Run': '运行',
                   'about': '关于', 'add': '添加', 'append_task': '添加任务', 'bottom': '置底', 'clear': '清空',
                   'down': '下移', 'one_click': '一键添加任务', 'remove': '移除', 'reset': '重置', 'save': '保存',
                   'start': '开始', 'top': '置顶', 'up': '上移'},
        'commandWidget': {'SearchLineText': ('精确查找', '模糊查找'), 'auto': '自动',
                          'buttons': ('打开配置', '保存配置', '另存为', '关闭配置'), 'disable': '禁用', 'tab': (
                '配置/输入输出', '质量/性能', '模式决策/分析', '帧/切片', '失真/量化', '视频可用性信息/SVT-HEVC', '比特流/日志'),
                          'tools': ('复制代码', '重置', '导出批处理文件'), 'undefined': '未指定'},
        'fileDialog': {'available': '可识别的文件', 'export': '导出', 'export Folder': '导出文件夹', 'file': '文件',
                       'open': '打开', 'output_video': '输出视频', 'save': '保存', 'support': '支持的文件',
                       'video': '视频文件'},
        'fileType': {'264': 'AVC/H.264基本流', '265': 'HEVC/H.265基本流', '3g2': '3GPP2视频/音频文件',
                     '3gp': '3GPP视频/音频文件', 'aac': 'AAC(高级音频编码)', 'ac3': 'A/52(亦称AC-3)',
                     'ass': 'SSA/ASS文本字幕',
                     'av1': '开放码流单元(OBU)流', 'avc': 'AVC/H.264基本流', 'avi': 'AVI(音视频交错文件)', 'avs': 'avs文件',
                     'bat': '批处理文件', 'caf': '(Apple无损音频编码)', 'dat': '数据文件', 'dll': '动态链接库文件',
                     'dts': 'DTS/DTS-HD (数字影院系统)', 'dts-hd': 'DTS/DTS-HD (数字影院系统)',
                     'dtshd': 'DTS/DTS-HD (数字影院系统)', 'dtsma': 'DTS/DTS-HD (数字影院系统)', 'eac3': 'A/52(亦称AC-3)',
                     'evo': 'MPEG节目流', 'evob': 'MPEG节目流', 'exe': '可执行文件', 'flac': 'FLAC(自由无损音频编码)',
                     'flv': 'FLV(Flash视频)', 'h264': 'AVC/H.264基本流', 'h265': 'HEVC/H.265基本流',
                     'hevc': 'HEVC/H.265基本流', 'idx': 'VobSub字幕', 'ivf': 'IVF (AV1, VP8, VP9)',
                     'json': 'Json文件', 'log': '日志文件', 'm1v': 'MPEG-1/2视频基本流', 'm2ts': 'MPEG传输流',
                     'm2v': 'MPEG-1/2视频基本流', 'm4a': '(Apple无损音频编码)', 'm4v': 'MP4视频/音频文件',
                     'mk3d': 'Matroska视频/音频文件', 'mka': 'Matroska视频/音频文件', 'mks': 'Matroska视频/音频文件',
                     'mkv': 'Matroska视频/音频文件', 'mov': 'QuickTime视频/音频文件', 'mp2': 'MPEG-1/2音频层Ⅱ/Ⅲ基本流',
                     'mp3': 'MPEG-1/2音频层Ⅱ/Ⅲ基本流', 'mp4': 'MP4视频/音频文件', 'mpeg': 'MPEG节目流', 'mpg': 'MPEG节目流',
                     'mpv': 'MPEG-1/2视频基本流', 'mts': 'MPEG传输流', 'obu': '开放码流单元(OBU)流',
                     'ogg': 'Opus(Ogg容器中)音频文件', 'ogm': 'Ogg/OGM视频/音频文件', 'ogv': 'Ogg/OGM视频/音频文件',
                     'opus': 'Opus(Ogg容器中)音频文件', 'ra': 'RealMedia视频/音频文件', 'ram': 'RealMedia视频/音频文件',
                     'rm': 'RealMedia视频/音频文件', 'rmvb': 'RealMedia视频/音频文件', 'rv': 'RealMedia视频/音频文件',
                     'sav': '存档文件', 'srt': 'SRT字幕文件', 'ssa': 'SSA/ASS文本字幕', 'sup': 'PGS/SUP字幕',
                     'thd': 'Dolby TrueHD(数字影院系统)', 'thd+ac3': 'Dolby TrueHD(数字影院系统)',
                     'true-hd': 'Dolby TrueHD(数字影院系统)', 'truehd': 'Dolby TrueHD(数字影院系统)', 'ts': 'MPEG传输流',
                     'tta': 'TTA(The True Audio无损音频编码)', 'txt': '文本文件', 'usf': 'USF文本字幕', 'vc1': 'VC-1基本流',
                     'vob': 'MPEG节目流', 'vpy': 'vpy文件', 'vtt': 'WebVTT字幕', 'wav': '未压缩的PCM音频',
                     'webm': 'WebM视频/音频文件', 'webma': 'WebM视频/音频文件', 'webmv': 'WebM视频/音频文件',
                     'wm': 'Windows媒体视频文件', 'wmv': 'Windows媒体视频文件', 'wv': 'WAVPACK v4音频',
                     'x264': 'AVC/H.264基本流', 'x265': 'HEVC/H.265基本流', 'xml': 'USF文本字幕',
                     'y4m': 'YUV4MPEG2 流',
                     'yuv': 'yuv文件'},
        'info': {'MediaInfo_not_found': '未找到MediaInfo.dll',
                 'check permission': '检查权限设置',
                 'cannot_be_recovered_after_clear': '缓存文件删除后无法恢复，是否继续？',
                 'close_anyway': '仍然要关闭程序？',
                 'close_encode': '请先关闭视频编码窗口',
                 'command_error': '命令错误：',
                 'command_redundant': '存档内以下参数未被识别：',
                 'command_repeat': '命令重复：',
                 'commands': '错误类型：存档与程序下方生成的参数不符\n可能的原因：版本与存档不符\n'
                             '解决办法：查看Error.txt，查找不符的参数，在程序内修改后重新保存。\n'
                             '如果该提示没有消失，请联系作者。\n',
                 'continue_anyway': '是否继续?',
                 'convert_fail': '混流mkv失败，已生成hevc格式： ',
                 'encoding': '仍在编码中',
                 'error': '错误', 'export_success': '导出成功',
                 'fail_to_open_file': '打开文件失败（可能的原因：未设置该文件的打开方式）：',
                 'failed_to_initialize_VapourSynth_environment': '无法初始化vapoursynth环境，请确认已正确安装vapoursynth',
                 'failed_to_load_avisynth': '导入AviSynth.dll失败',
                 'file_below_is_not_supported': '不支持以下文件',
                 'file_extension_error': '拓展名错误',
                 'file_invalid': '文件不合法',
                 'file_repeat': '文件名重复',
                 'function': '函数',
                 'overwritten': '是否覆盖？',
                 'input_file_can_not_be_empty': '输入源不能为空',
                 'instruction_sets_not_fit': '你的电脑指令集可能不适配此x265程序',
                 'is_exist': '已存在',
                 'is_invalid': '程序不合法',
                 'is_repeat': '重复',
                 'lack_command': '存档缺少以下参数：',
                 'language_text_not_found': '语言未找到。',
                 'mediaInfo_not_found': '未找到MediaInfo.dll',
                 'mediainfo_is_busy': 'MediaInfo正在使用中，稍后再重试',
                 'no_empty': '不能为空',
                 'not_available': '不可用',
                 'not_equal': '输出视频数量必须和输入数量相等，是否自动匹配缺少的文件名？',
                 'not_exist': '不存在',
                 'not_found': '未找到',
                 'not_mediainfo': '非MediaInfo.dll，请重新下载',
                 'not_readable': '无法读取',
                 'not_saved': '未保存',
                 'not_support': '只允许拖入 ',
                 'not_writable': '无法写入',
                 'parameter': '参数',
                 'permission': '该文件正在被占用或权限不足',
                 'repeat_open': '请问重复运行本程序！',
                 'save_ask': '是否保存配置文件？',
                 'save_success': '保存成功',
                 'set_programs': '请设置外部程序（绝对路径）',
                 'success': '成功',
                 'task_dir_disable': '任务文件夹不可用，请确认权限设置',
                 'too_many_files': '只允许拖入一个文件',
                 'unknown': '存档命令与控件状态不相符',
                 'unknown_error': '未知错误，请重新下载MediaInfo.dll',
                 'version_different': '存档版本与软件版本不符，请检查并重新保存',
                 'video_track_not_found': '找不到视频轨，请检查输入文件',
                 'warning': '警告',
                 'win32': '不是有效的win32程序，请使用64位版本'},
        'mainWidget': {'about': '关于',
                       'menu': ('命令参数', '媒体信息', '工具', '视频编码', '设置')},
        'mediaInfo': {'Audio': '音频',
                      'CBR': '恒定码率',
                      'CFR': '恒定帧率',
                      'Color space': '色彩空间',
                      'Constant': '恒定模式',
                      'Duration': '时长',
                      'General': '通用',
                      'Image': '图像',
                      'Interlaced': '隔行扫描',
                      'Lossless': '无损模式',
                      'Lossy': '有损模式',
                      'Menu': '章节',
                      'menu_id': '菜单ID',
                      'No': '否',
                      'Other': '其他',
                      'Progressive': '逐行扫描',
                      'SeparatedFields': '单独场',
                      'Text': '字幕',
                      'VBR': '动态码率',
                      'VFR': '动态帧率',
                      'Video': '视频',
                      'Yes': '是',
                      'bit_depth': '位深',
                      'bit_rate': '比特率',
                      'bit_rate_mode': '码率模式',
                      'bits__pixel_frame': '数据密度【码率/（像素×帧率）】',
                      'channel_layout': '声道布局',
                      'channel_s': '声道',
                      'chroma_subsampling': '色度采样',
                      'clean_aperture_height': '干净光圈高度',
                      'codec_configuration_box': '编码配置区块 (box)',
                      'codec_id': '编解码器编号',
                      'codec_id_info': '编解码器ID/信息',
                      'color_primaries': '基色',
                      'color_range': '色彩范围',
                      'color_space': '色彩空间',
                      'comapplequicktimecontentidentifier': 'com.apple.quicktime.content.identifier',
                      'comapplequicktimecreationdate': 'com.apple.quicktime.creationdate',
                      'comapplequicktimelocationiso6709': 'com.apple.quicktime.location.ISO6709',
                      'comapplequicktimemake': 'com.apple.quicktime.make',
                      'comapplequicktimemodel': 'com.apple.quicktime.model',
                      'comapplequicktimesoftware': 'com.apple.quicktime.software',
                      'compression_mode': '压缩模式',
                      'count_of_elements': '元素总数',
                      'default': '默认',
                      'delay': '延迟',
                      'delay_relative_to_video': '音频延迟',
                      'duration': '时长',
                      'encoded_date': '编码日期',
                      'encoded_library_version': '编码函数库',
                      'encoding_settings': '编码设置',
                      'file_size': '文件大小',
                      'forced': '强制',
                      'format': '格式',
                      'format_compression': '压缩算法',
                      'format_info': '格式信息',
                      'format_profile': '格式配置',
                      'format_settings': '格式设置',
                      'format_settings__bvop': '格式设置, B 帧',
                      'format_settings__cabac': '格式设置,CABAC',
                      'format_settings__gop': '格式设置, GOP',
                      'format_settings__matrix': '格式设置, 矩阵',
                      'format_settings__picture_structure': '格式设置, 图像结构',
                      'format_settings__reference_frames': '格式设置，参考帧',
                      'format_version': '格式版本',
                      'frame_count': '帧数',
                      'frame_rate_mode': '帧率模式',
                      'height': '高度',
                      'hour': '小时',
                      'language': '语言',
                      'm_second': '毫秒',
                      'mastering_display_color_primaries': '制片显示器色彩原色',
                      'mastering_display_luminance': '制片显示器亮度',
                      'matrix_coefficients': '矩阵系数',
                      'minute': '分',
                      'movie_name': '名称',
                      'display_aspect_ratio': '画面比例',
                      'frame_rate': '帧率',
                      'hdr_format': 'HDR格式',
                      'maximum_bit_rate': '最大比特率',
                      'maximum_frame_rate': '最大帧率',
                      'minimum_frame_rate': '最小帧率',
                      'original_frame_rate': '原始帧率',
                      'rotation': '旋转',
                      'sampling_rate': '采样率',
                      'unique_id': '唯一ID',
                      'overall_bit_rate': '总比特率',
                      'overall_bit_rate_mode': '总比特率模式',
                      'pixel_aspect_ratio': '像素比例',
                      'scan_order': '扫描顺序',
                      'scan_type': '扫描方式',
                      'scan_type__store_method': '扫描类型储存方式',
                      'second': '秒',
                      'source_duration': '源, 时长',
                      'source_stream_size': '源，流大小',
                      'standard': '标准', 'stream_size': '流大小',
                      'tagged_date': '标记日期',
                      'title': '标题',
                      'track_id': '编号',
                      'transfer_characteristics': '传输特质',
                      'type': '类型',
                      'Variable': '可变模式',
                      'width': '宽度',
                      'writing_application': '编码程序',
                      'writing_library': '编码函数库'},
        'windowsTitle': 'x265 encoder'}, 'language_code': 'zh_CN'}

if __name__ == '__main__':
    write = 0


    def walk(c_dict):
        if isinstance(c_dict, dict):
            new = {}
            keys = sorted([i for i in c_dict.keys()])
            for key in keys:
                new[key] = c_dict.get(key)
            for key, value in new.items():
                new[key] = walk(value)
            return new
        elif isinstance(c_dict, (list, tuple)):
            new = list(c_dict)
            for n, i in enumerate(new):
                new[n] = walk(i)
            return tuple(new)
        else:
            return c_dict


    pyperclip.copy(str(walk(All)))


    def print_all(k, obj):
        if isinstance(obj, (list, tuple)):
            print(f'{k} = {len(obj)}')
            for n, i in enumerate(obj):
                print_all(f'{k}:{n}', i)
        elif isinstance(obj, dict):
            print(f'{k} = {len(obj)}')
            for k, i in obj.items():
                print_all(k, i)


    print('"""')
    print_all('data', All)
    print('"""')
"""
data = 3
cmd_language = 3
comboBoxes = 8
csv-log-level = 3
interlace = 3
log-level = 6
output-depth = 4
tune = 7
profileWidgetLabels = 22
titles = 50
language = 15
AboutWidget = 3
Headers = 3
Programs = 6
Programs:0 = 3
Programs:1 = 3
Programs:2 = 3
Programs:3 = 3
Programs:4 = 3
Programs:5 = 3
BatchExportWidget = 2
label = 3
EncodeWidget = 21
TaskAppendWidget = 5
TaskOperationWidget = 10
action = 11
priority = 7
retry = 5
shutdown = 5
state = 7
tab = 2
tasks = 7
MediaInfoWidget = 3
buttons = 4
SettingWidget = 26
cache_modes = 2
default_source_filters = 5
tab = 5
TaskEdit = 4
header = 4
label = 3
task_type = 3
ToolsWidget = 1
getnative = 20
ChartView = 3
aboutWidget = 2
labels = 5
groupboxes = 5
helps = 13
modes = 6
button = 27
commandWidget = 7
SearchLineText = 2
buttons = 4
tab = 7
tools = 3
fileDialog = 9
fileType = 87
info = 45
mainWidget = 2
menu = 5
mediaInfo = 101
"""
