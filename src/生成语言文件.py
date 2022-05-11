from pickle import dump

from English import *

with open(r'.\language\Eng.language', 'wb') as f:
    dump(All, f)
    with open('default_lang.py', 'w', encoding='utf-8') as f:
        f.write(f'data={repr(All)}')

from zh_CN import *

with open(r'.\language\zh_CN.language', 'wb') as f:
    dump(All, f)
