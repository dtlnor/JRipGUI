from os import listdir, system
from os.path import splitext, join
import base64

with open('svgs.py', 'w', encoding='utf-8') as f:
    for i in listdir(r'.\svg'):
        base, ext = splitext(i)
        if ext == '.svg':
            image = open(join(r'.\svg', i), 'rb')
            data = image.read()
            f.write(f'{base} = {bytes(data)}\n')
            image.close()
