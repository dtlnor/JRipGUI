from os import listdir, system
from os.path import splitext
import base64

exe = r'D:\ImageMagick-6.2.7-Q16\convert.exe'
with open('images.py', 'w', encoding='utf-8') as f:
    for i in listdir():
        if splitext(i)[1] == '.png':
            image = open(i, 'rb')
            data = image.read()
            b64 = base64.b64encode(data)
            f.write(f'{splitext(i)[0]} = {str(b64)}\n')
            image.close()

