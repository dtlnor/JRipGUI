import base64

with open('1.txt', 'w') as f:
    image = open('_.png', 'rb')
    data = image.read()
    b64 = base64.b64encode(data)
    f.write(str(b64))
    
