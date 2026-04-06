import os
bom = b'\xef\xbb\xbf'
fixed = []
for root, dirs, files in os.walk('maiie-web/src'):
    dirs[:] = [d for d in dirs if d != 'node_modules']
    for f in files:
        path = os.path.join(root, f)
        with open(path, 'rb') as fh:
            content = fh.read()
        if content.startswith(bom):
            with open(path, 'wb') as fh:
                fh.write(content[3:])
            fixed.append(path)
for p in fixed:
    print('Fixed:', p)
print('Total:', len(fixed))
