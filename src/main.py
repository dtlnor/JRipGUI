import sys

# from PyQt5 import QWinTaskbarButton
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtCore import QFileInfo, QSharedMemory
from PySide6.QtWidgets import QApplication, QSplashScreen, QMessageBox
from data import load_languages, check_task_dir, DEFAULT_UI_TXT, DEFAULT_CMD_TXT, TASK_DIR,\
    WORK_DIR, FONT_SIZE, FONT, SETTINGS, load_css
import svgs
import default_lang
from x265 import MainWidget


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(load_css())

    splash = QSplashScreen(QPixmap.fromImage(QImage.fromData(svgs.icon)))
    splash.show()

    share = QSharedMemory()
    share.setKey(WORK_DIR.absoluteFilePath('x265EncoderGui'))
    share.attach()

    for key, value in default_lang.data.get('ui_language').items():
        setattr(DEFAULT_UI_TXT, key, value)

    for key, value in default_lang.data.get('cmd_language').items():
        setattr(DEFAULT_CMD_TXT, key, value)
    if share.create(1):

        TASK_DIR.setNameFilters(('job[0-9][0-9][0-9].task',
                                 'job[0-9][0-9][0-9][0-9].task',
                                 'job[0-9][0-9][0-9][0-9][0-9].task'))
        if check_task_dir(splash):
            WORK_DIR.mkpath('css')

            mainWidget = MainWidget(app)
            mainWidget.load_language(load_languages())
            mainWidget.settingWidget.init_programs()
            FONT.setPixelSize(FONT_SIZE)
            mainWidget.settingWidget.apply()
            mainWidget.set_font(FONT)
            mainWidget.encodeWidget.taskOperationWidget.taskTableWidget.init_tasks()

            if SETTINGS.autoLoadSav != 0 and (recent := QFileInfo(SETTINGS.recentSavFile)).exists():
                mainWidget.commandWidget.open_file(recent.absoluteFilePath())
            else:
                SETTINGS.recentSavFile = ''

            mainWidget.show()

            splash.finish(mainWidget)
            sys.exit(app.exec())
        else:
            QMessageBox.critical(splash,
                                 DEFAULT_UI_TXT.info.error,
                                 DEFAULT_UI_TXT.info.task_dir_disable,
                                 QMessageBox.StandardButton.Ok,
                                 QMessageBox.StandardButton.Ok)
            exit()
    else:
        QMessageBox.critical(splash,
                             DEFAULT_UI_TXT.info.error,
                             DEFAULT_UI_TXT.info.repeat_open,
                             QMessageBox.StandardButton.Ok,
                             QMessageBox.StandardButton.Ok)
        exit()
