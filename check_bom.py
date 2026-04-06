import os
bom = b'\xef\xbb\xbf'
for root, dirs, files in os.walk('maiie-web/src'):
    dirs[:] = [d for d in dirs if d != 'node_modules']
    for f in files:
        path = os.path.join(root, f)
        with open(path, 'rb') as fh:
            if fh.read(3) == bom:
                print(path)
