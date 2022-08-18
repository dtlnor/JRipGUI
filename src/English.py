from helps import helps
import time
import ver

today = time.strftime("%Y%m%d", time.localtime())
print(today)
help = {}
for key in helps:
    help[key] = helps[key]['English']
print(help)
All = {
    'cmd_language': {
        'comboBoxes': {'csv-log-level': ('0.summary', '1.frame level logging', '2.with performance statistics'),
                       'input-depth': 'undefined', 'interlace': ('progressive', 'tff', 'bff'),
                       'level-idc': '0（auto）',
                       'log-level': ('-1.none', '0.error', '1.warning', '2.info', '3.debug', '4.full'),
                       'output-depth': ('undefined', '8', '10', '12'),
                       'tune': ('none', 'psnr', 'ssim', 'grain', 'zero-latency', 'fast-decode', 'animation', 'lp', 'vcbs', 'lp++', 'vcbs++')},
        'profileWidgetLabels': (
            'tune', 'encode mode', 'bitrate(kbps)', 'pass', 'CRF', 'QP', 'output depth', 'profile', 'level', 'ref',
            'limit-refs', 'input depth', 'width', 'height', 'input csp', 'fps', 'interlace', 'seek',
            'dup-threshold',
            'frames',
            'chunk-start', 'chunk-end'),
        'titles': (
            'Preset', 'Encode Mode', 'Quality reporting metrics', 'Profile', 'Refs', 'Allow None Conformance',
            'Ultra HD Blu_ray support', 'Input / Output Options', 'Pass', 'QP', 'CRF', 'VBV Buffer', 'Performance',
            'Parallel',
            'RDO', 'Quad_Tree Size and Depth', 'Motion Partitions', 'RDOQ', 'Skip', 'Refinement', 'Analysis',
            'Temporal/motion search', 'Look ahead', 'GOP', 'Insert', 'Spatial/intra', 'B frames', 'Others',
            'Adaptive Quantization', 'SAO', 'Deblocking', 'Offset', 'Zones', 'Blur', 'Quantization', 'Others',
            'Sample Size',
            'HDR', 'Color', 'Others', 'SVT-HEVC', 'HRD', 'Optimize', 'VUI', 'DCT Approximations', 'Dolby Vision',
            'Debug',
            'Logging', 'Others', 'Custom Command Line')},
    'ui_language': {
        'AboutWidget': {'Headers': ('Programs', 'Version', 'Bit'),
                        'Info': f'x265 command editor\n\nPowered by JasinChen\ne-mail: 402083306@qq.com\nVersion: {ver.ver}',
                        'Programs': (
                            ('x265', ver.x265, '64-bit'),
                            ('vspipe', ver.vspipe, '64-bit'),
                            ('avisynth+', ver.avisynth, '64-bit'),
                            ('mkvmerge', ver.mkvmerge, '64-bit'),
                            ('mp4box', ver.mp4box, '64-bit'),
                            ('MediaInfo', ver.MediaInfo, '64-bit'))},
        'BatchExportWidget': {'label': ('Input', 'Output video', 'Output file'),
                              'title': 'Batch Export'},
        'EncodeWidget': {
            'TaskAppendWidget': (
                'Input Files', 'Input File Preview', 'Output format', 'Output Files', 'Command Line'),
            'TaskOperationWidget': (
                'Task Filter', 'Current Task', 'Input', 'Output', 'Encode rate', 'Avg bitrate', 'Remaining time',
                'Frames',
                'Retry times:', 'Finished:'), 'abort': 'Abort', 'abort_all': 'Abort all', 'action': (
                'Waiting', 'Abort', 'Edit', 'Delete', 'Clear', 'Clear Message', 'Open Input File',
                'Open Input Folder',
                'Open Output File', 'Open Output Folder', 'Export BAT File'),
            'back_cur_task': 'Back to running task',
            'cancel_plan': 'Cancel Plan',
            'encoding': 'Encoding',
            'finish': 'Finished',
            'indexing': 'Building Index',
            'merging': 'Merging',
            'priority': (
                'IdlePriority', 'LowestPriority', 'LowPriority', 'NormalPriority', 'HighPriority', 'HighestPriority',
                'TimeCriticalPriority'),
            'retry': ('Do not retry', 'Retry 1 times', 'Retry 5 times', 'Retry 10 times', 'Infinite retry'),
            'shutdown': ('Do nothing', 'Shut down', 'Close program', 'Restart computer', 'Sleep'),
            'state': ('waiting', 'running', 'finish', 'abort', 'error', 'retry', 'warning'),
            'tab': ('Append Tasks', 'Manage / Encode'),
            'task': 'Task',
            'task_begin': 'Task begin',
            'task_finish': 'Task finished',
            'tasks': ('Input', 'Output', 'Type', 'Status', 'Start time', 'End time', 'Command'),
            'title': 'Encode video'},
        'MediaInfoWidget': {'buttons': ('Import', 'Export vpy', 'Export avs',
                                        'Batch Export vpy', 'Batch Export avs', 'Clear'),
                            'info': 'No information available',
                            'reload': 'Reload'},
        'SettingWidget': {'auto_load_sav': 'Auto loading sav file after program start', 'avs': 'avs template',
                          'cache': 'cache', 'cache_mode': 'Cache mode',
                          'cache_modes': ('Put cache file in certain folder', 'Put cache file in output folder'),
                          'clear_cache_files': 'Clear cache folder', 'cmd': 'command language',
                          'default_source_filter': 'Default source',
                          'default_source_filters': (
                              'Depend on source video', 'FFMS2', 'LWLibavSource', 'LibavSMASHSource', 'AVISource'),
                          'disable': 'Disabled',
                          'enable': 'Enabled', 'encode_timeout': 'Encode timeout (s)', 'font': 'Font',
                          'insert_text': 'Insert Text',
                          'file_name': 'FileName',
                          'base_name': 'BaseName',
                          'suffix': 'Suffix',
                          'path': 'AbsPath',
                          'entry': 'Entries',
                          'label': 'Language',
                          'full': 'Display additional tags, including computer-readable values for sizes and durations.',
                          'load_video_cmd': 'Enable load encode settings from hevc video',
                          'need_restart': 'Restart the program for the settings to take effect',
                          'raw_hevc_ext': 'raw-hevc extension',
                          'parse_speed': 'Parse speed',
                          'preload': 'preload next task when encoding to decrease spending time (support preloading vpy, avs)',
                          'preload_timeout': 'Preload timeout (s)',
                          'reload': 'Reload programs',
                          'remember_temp_dir': 'Remember folder last used',
                          'support_all': 'Support all video format as input',
                          'support_all_tip': 'Video files are only supported as input sources in the customized X265. Make sure that your X265 supports it.',
                          'svt': 'Enable svt-hevc (If your x265 program support)',
                          'tab': ('Display', 'Commands', 'MediaInfo', 'Encode', 'Programs'), 'title': 'Settings',
                          'vpy': 'vpy template'},
        'TaskEdit': {'header': ('Codec', 'Type', 'Track ID', 'Path'), 'label': ('Input', 'Output', 'Command'),
                     'task_type': {'Audio': 'Audio', 'Menu': 'Chapter', 'Text': 'Subtitle'}, 'title': 'Task Editor'},
        'ToolsWidget': {
            'getnative': {'ChartView': {'best': 'Best value', 'difference': 'Difference', 'height': 'Height'},
                          'aboutWidget': {'labels': ('GetNative 3.0.0',
                                                     'Find the native resolution(s) of upscaled material (mostly anime)',
                                                     "Warning: This script's success rate is far from perfect. If possible, do multiple tests on different frames from the same source. Bright scenes generally yield the most accurate results. Graphs tend to have multiple notches, so the script's assumed resolution may be incorrect. Also, due to the current implementation of the autoguess, it is not possible for the script to automatically recognize 1080p productions.",
                                                     'Author: Infiziert90',
                                                     'Website: https://github.com/Infiziert90/getnative'),
                                          'title': 'About GetNative'}, 'ar': 'Aspect ratio', 'b': 'Bicubic-b',
                          'c': 'Bicubic-c', 'frame': 'Frame',
                          'groupboxes': ('Input', 'Presets', 'Kernel', 'General', 'Output'),
                          'helps': {'ar': 'Force aspect ratio. Only useful for anamorphic input',
                                    'b': 'B parameter of bicubic resize', 'c': 'C parameter of bicubic resize',
                                    'frame': 'Specify a frame for the analysis', 'img': 'Force image input',
                                    'kernel': 'Resize kernel to be used', 'mask_out': 'Save detail mask as png',
                                    'max_h': 'Maximum height to consider',
                                    'min_h': 'Minimum height to consider',
                                    'plot_format': 'Format of the output image. Specify multiple formats separated by commas. Can be svg, png, pdf, rgba, jp(e)g, tif(f), and probably more',
                                    'steps': 'This changes the way getnative will handle resolutions. Example steps=3 [500p, 503p, 506p ...]',
                                    'taps': 'Taps parameter of lanczos resize',
                                    'use': 'Use specified source filter'}, 'input': 'Input',
                          'input_filter': 'Input filter', 'is_image': 'Input is image', 'kernel': 'Kernel',
                          'max_height': 'Maximum height', 'min_height': 'Minimum height',
                          'modes': ('None', 'bilinear', 'bicubic', 'lanczos', 'spline', 'all'),
                          'output_dir': 'Output folder', 'output_mask': 'Output mask', 'stepping': 'Stepping',
                          'taps': 'Lanczos-taps', 'task_running': 'Task running..'}},
        'button': {'Abort': 'Abort', 'Abort_all': 'Abort all', 'Always_on_top': 'Always on Top', 'Apply': 'Apply',
                   'Cancel': 'Cancel', 'Close': 'Close', 'Confirm': 'Confirm', 'Import_Audio': 'Import Audio',
                   'Import_Chapter': 'Import Chapter', 'Import_Subtitle': 'Import Subtitle', 'Load': 'Load',
                   'Merge': 'Merge', 'OK': 'OK', 'Run': 'Run', 'about': 'about', 'add': 'add',
                   'append_task': 'Append',
                   'bottom': 'bottom', 'clear': 'clear', 'down': 'down', 'one_click': 'One-Click',
                   'remove': 'remove',
                   'reset': 'Reset', 'save': 'Save', 'start': 'Start', 'top': 'top', 'up': 'up'},
        'commandWidget': {'SearchLineText': ('exact search', 'fuzzy search'), 'auto': 'Auto',
                          'buttons': ('Open Profile', 'Save Profile', 'Save as', 'Close'), 'disable': 'disable',
                          'tab': (
                              'Profile/IO', 'Quality/Performance', 'Mode/Analysis', 'Frames/Slice',
                              'Distortion/Quantization', 'VUI/SVT',
                              'Bitstream/Logging'), 'tools': ('Copy', 'Reset', 'Export BAT'),
                          'undefined': 'undefined'},
        'fileDialog': {'available': 'Available files', 'export': 'export', 'export_folder': 'Export Folder',
                       'file': 'file',
                       'open': 'open', 'output video': 'Output video', 'save': 'save', 'support': 'Supported files',
                       'video': 'Video files'},
        'fileType': {'264': 'AVC/h.264 elementary streams', '265': 'HEVC/h.265 elementary streams',
                     '3g2': '3GPP2 Video/Audio files', '3gp': '3GPP Video/Audio files', 'aac': 'AAC(高级音频编码)',
                     'ac3': 'A/52(亦称AC-3)', 'ass': 'SSA/ASS文本字幕', 'av1': '开放码流单元(OBU)流',
                     'avc': 'AVC/h.264 elementary streams', 'avi': 'AVI（Video interleaved）', 'avs': 'avs file',
                     'bat': 'Batch file', 'caf': '(Apple无损音频编码)', 'dat': 'Data file', 'dll': 'Dynamic Link Library',
                     'dts': 'DTS/DTS-HD (数字影院系统)', 'dts-hd': 'DTS/DTS-HD (数字影院系统)', 'dtshd': 'DTS/DTS-HD (数字影院系统)',
                     'dtsma': 'DTS/DTS-HD (数字影院系统)', 'eac3': 'A/52(亦称AC-3)', 'evo': 'MPEG节目流', 'evob': 'MPEG节目流',
                     'exe': 'executable file', 'flac': 'FLAC(自由无损音频编码)', 'flv': 'Flash video',
                     'h264': 'AVC/h.264 elementary streams', 'h265': 'HEVC/h.265 elementary streams',
                     'hevc': 'HEVC/h.265 elementary streams', 'idx': 'VobSub字幕', 'ivf': 'IVF (AV1, VP8, VP9)',
                     'json': 'Json file', 'log': 'Logging file', 'm1v': 'MPEG-1/2视频基本流',
                     'm2ts': 'MPEG transport streams',
                     'm2v': 'MPEG-1/2视频基本流', 'm4a': '(Apple无损音频编码)', 'm4v': 'MP4 Video/Audio Files',
                     'mk3d': 'Matroska Video/Audio Files', 'mka': 'Matroska Video/Audio Files',
                     'mks': 'Matroska Video/Audio Files', 'mkv': 'Matroska Video/Audio Files',
                     'mov': 'QuickTime Video/Audio files', 'mp2': 'MPEG-1/2音频层Ⅱ/Ⅲ基本流', 'mp3': 'MPEG-1/2音频层Ⅱ/Ⅲ基本流',
                     'mp4': 'MP4 Video/Audio Files', 'mpeg': 'MPEG program streams', 'mpg': 'MPEG program streams',
                     'mpv': 'MPEG-1/2视频基本流', 'mts': 'MPEG transport streams', 'obu': '开放码流单元(OBU)流',
                     'ogg': 'Opus(Ogg容器中)音频文件', 'ogm': 'Ogg/OGM音频/视频文件', 'ogv': 'Ogg/OGM音频/视频文件',
                     'opus': 'Opus(Ogg容器中)音频文件', 'ra': 'RealMedia音频/视频文件', 'ram': 'RealMedia音频/视频文件',
                     'rm': 'RealMedia Video/Audio files', 'rmvb': 'RealMedia Video/Audio files',
                     'rv': 'RealMedia音频/视频文件',
                     'sav': 'save file', 'srt': 'SRT字幕文件', 'ssa': 'SSA/ASS文本字幕', 'sup': 'PGS/SUP字幕',
                     'thd': 'Dolby TrueHD(数字影院系统)', 'thd+ac3': 'Dolby TrueHD(数字影院系统)',
                     'true-hd': 'Dolby TrueHD(数字影院系统)',
                     'truehd': 'Dolby TrueHD(数字影院系统)', 'ts': 'MPEG transport streams',
                     'tta': 'TTA(The True Audio无损音频编码)',
                     'txt': 'Text file', 'usf': 'USF文本字幕', 'vc1': 'VC-1基本流', 'vob': 'MPEG节目流', 'vpy': 'vpy file',
                     'vtt': 'WebVTT Subtitles', 'wav': '未压缩的PCM音频', 'webm': 'WebM音频/视频文件', 'webma': 'WebM音频/视频文件',
                     'webmv': 'WebM音频/视频文件', 'wm': 'Windows Media Video', 'wmv': 'Windows Media Video',
                     'wv': 'WAVPACK v4 Audio', 'x264': 'AVC/h.264 elementary streams',
                     'x265': 'HEVC/h.265 elementary streams', 'xml': 'USF文本字幕', 'y4m': 'YUV4MPEG2 streams',
                     'yuv': 'yuv file'},
        'info': {'cannot_be_recovered_after_clear': 'Cache files cannot be recovered after clear, continue anyway?',
                 'close_anyway': 'Close the program anyway？',
                 'close_encode': 'Close Encode Video Widget first.',
                 'check permission': 'check the permission',
                 'command_error': 'Command error: \n',
                 'command_redundant': 'The commands in save file can not be recognized: ',
                 'command_repeat': 'Command repeat: ',
                 'commands': 'Error type: The commands between save file and program are different\n'
                             'Possible result：Program version is different from save file\n'
                             'Solution：View "Error.txt"，查找不符的参数，在程序内修改后重新保存。如果该提示没有消失，请联系作者。\n',
                 'continue_anyway': 'Continue anyway?',
                 'convert_fail': 'MKVmerge failed, create the hevc file: ',
                 'encoding': 'Encoding',
                 'error': 'error',
                 'export_success': 'Export success',
                 'fail_to_open_file': 'Fail to open file(Possible causes: Opening mode of this file is not set)',
                 'failed_to_initialize_VapourSynth_environment': 'Failed to initialize VapourSynth environment',
                 'failed_to_load_avisynth': 'Failed to load AviSynth.dll',
                 'function': 'Function',
                 'file_below is not supported': 'File below is not supported',
                 'file_extension_error': 'File extension error',
                 'file_invalid': 'File is invalid',
                 'file_repeat': 'File name repeat',
                 'overwritten': 'Overwrite it?',
                 'input_file_can_not_be_empty': 'Input file can not be empty!',
                 'instruction_sets_not_fit': 'May the instruction sets ofyour computeris not adapt to this x265 program.',
                 'is_exist': 'is exist',
                 'is_invalid': 'this program is invalid',
                 'is_repeat': 'is repeat',
                 'lack_command': 'Save file lacks commands: ',
                 'language_text_not_found': 'Language not found.',
                 'mediainfo_is_busy': 'MediaInfo is used now, please try later',
                 'mediaInfo_not_found': 'MediaInfo.dll is not found',
                 'no_empty': 'Can not be empty',
                 'not_available': 'not available',
                 'not_equal': 'The number between input and output video must be equal, automatically matching missing filenames?',
                 'not_exist': 'not exist',
                 'not_found': 'is not found',
                 'not_mediainfo': 'not MediaInfo.dll，please re-download.',
                 'not_readable': 'cannot read',
                 'not_saved': 'Not saved yet',
                 'not_support': 'Only support ',
                 'not_writable': 'cannot write',
                 'parameter': 'parameter',
                 'permission': 'This file is occupied or permissions denied',

                 'repeat_open': 'Please don\'t repeat running this program!',
                 'save_ask': 'Should I save the profile?',
                 'save_success': 'Save success',
                 'set_programs': 'Please set the program（Ablsolute Path）',
                 'success': 'success',
                 'task_dir_disable': 'Task dir is disable, please check permission',
                 'too_many_files': 'Only can input one file',
                 'unknown': 'Commands mismatch on widgets',
                 'unknown_error': 'Unknown error，please re-download MediaInfo.dll',
                 'version_different': 'Version of Save file and software are different, check and save it again',
                 'video_track_not_found': 'Video track not found, check input file.',
                 'warning': 'Warning',
                 'win32': 'is not a valid Win32 program，please use x64 version'},
        'mainWidget': {'about': 'About', 'menu': ('Commands', 'Media Info', 'Tools', 'Encode Video', 'Settings')},
        'mediaInfo': {'Audio': 'Audio',
                      'CBR': 'Constant',
                      'CFR': 'Constant',
                      'Color space': 'Color space',
                      'Constant': 'Constant',
                      'Duration': 'Duration',
                      'General': 'General',
                      'Image': 'Image',
                      'Interlaced': 'Interlaced',
                      'Lossless': 'lossless',
                      'Lossy': 'lossy',
                      'Menu': 'Chapter',
                      'menu_id': 'menu_id',
                      'No': 'no',
                      'Other': 'Other',
                      'Progressive': 'Progressive',
                      'SeparatedFields': 'Separated Fields',
                      'Text': 'Subtitle',
                      'VBR': 'Variable',
                      'VFR': 'VFR',
                      'Video': 'Video',
                      'Yes': 'yes',
                      'bit_depth': 'Depth',
                      'bit_rate': 'Bit rate',
                      'bit_rate_mode': 'Bit rate mode',
                      'bits__pixel_frame': 'Bits/(Pixel×Frames)',
                      'channel_layout': 'Channel layout',
                      'channel_s': 'Channels',
                      'chroma_subsampling': 'Chroma subsampling',
                      'clean_aperture_height': 'Clean aperture height',
                      'codec_configuration_box': 'Codec configuration (box)',
                      'codec_id': 'Codec ID',
                      'codec_id_info': 'Codec ID / Info',
                      'color_primaries': 'Color primaries',
                      'color_range': 'Color range',
                      'color_space': 'Color space',
                      'comapplequicktimecontentidentifier': 'com.apple.quicktime.content.identifier',
                      'comapplequicktimecreationdate': 'com.apple.quicktime.creationdate',
                      'comapplequicktimelocationiso6709': 'com.apple.quicktime.location.ISO6709',
                      'comapplequicktimemake': 'com.apple.quicktime.make',
                      'comapplequicktimemodel': 'com.apple.quicktime.model',
                      'comapplequicktimesoftware': 'com.apple.quicktime.software',
                      'compression_mode': 'Compression mode',
                      'count_of_elements': 'Count of elements',
                      'default': 'default',
                      'delay': 'Delay', 'delay_relative_to_video': 'Delay relative to video',
                      'duration': 'Duration',
                      'encoded_date': 'Encoded data',
                      'encoded_library_version': 'Encoded library version',
                      'encoding_settings': 'Encoded setting',
                      'file_size': 'File size',
                      'forced': 'Force',
                      'format': 'Format',
                      'format_compression': 'Format compression',
                      'format_info': 'Format info',
                      'format_profile': 'Format profile',
                      'format_settings': 'Format settings',
                      'format_settings__bvop': 'Format settings, BVOP',
                      'format_settings__cabac': 'Format settings, CABAC',
                      'format_settings__gop': 'Format settings, GOP',
                      'format_settings__matrix': 'Format settings, Matrix',
                      'format_settings__picture_structure': 'Format settings, picture structure',
                      'format_settings__reference_frames': 'Format settings，Reference frames',
                      'format_version': 'Format version',
                      'frame_count': 'Frames',
                      'frame_rate_mode': 'Frame rate mode',
                      'height': 'Height',
                      'hour': 'h',
                      'language': 'Language',
                      'm_second': 'msec',
                      'mastering_display_color_primaries': 'Mastering display color primaries',
                      'mastering_display_luminance': 'Mastering display luminance',
                      'matrix_coefficients': 'Matrix coefficients',
                      'minute': 'min',
                      'movie_name': 'movie name',
                      'display_aspect_ratio': 'DAR',
                      'frame_rate': 'Frame rate',
                      'hdr_format': 'HDR format',
                      'maximum_bit_rate': 'Maximum bit rate',
                      'maximum_frame_rate': 'Maximum frame rate',
                      'minimum_frame_rate': 'Minimum frame rate',
                      'original_frame_rate': 'Original frame rate',
                      'rotation': 'Rotation',
                      'sampling_rate': 'Sampling rate',
                      'unique_id': 'Other Unique ID',
                      'overall_bit_rate': 'Overall bit rate',
                      'overall_bit_rate_mode': 'Overall bit rate mode',
                      'pixel_aspect_ratio': 'SAR',
                      'scan_order': 'Scan order',
                      'scan_type': 'Scan type',
                      'scan_type__store_method': 'Scan type, Store method', 'second': 's',
                      'source_duration': 'Source duration',
                      'source_stream_size': 'Source stream size',
                      'standard': 'Standard',
                      'stream_size': 'Stream size',
                      'tagged_date': 'Tagged date',
                      'title': 'Title',
                      'track_id': 'ID',
                      'transfer_characteristics': 'Transfer characteristics',
                      'type': 'Type',
                      'Variable': 'Variable',
                      'width': 'Width',
                      'writing_application': 'Writing application',
                      'writing_library': 'Writing library'},
        'windowsTitle': 'x265 encoder'},
    'language_code': 'eng'}

if __name__ == '__main__':
    write = 1


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
comboBoxes = 7
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
EncodeWidget = 22
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
mediaInfo = 100
"""
