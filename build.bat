py -m nuitka --mingw64 --standalone --show-progress --show-memory --plugin-enable=pyside6 --include-qt-plugins=sensible,styles --windows-icon-from-ico=src\icon.ico --windows-disable-console --plugin-enable=pkg-resources --plugin-enable=pylint-warnings --output-dir=out src\main.py

pause