from os import listdir, system
from os.path import splitext, join
import base64

exe = r'D:\ImageMagick-6.2.7-Q16\convert.exe'
with open('images.py', 'w', encoding='utf-8') as f:
    for i in listdir(r'.\images'):
        base, ext = splitext(i)
        if ext == '.png':
            image = open(join(r'.\images', i), 'rb')
            data = image.read()
            f.write(f'{base} = {str(data)}\n')
            image.close()
