import os
bom = b'\xef\xbb\xbf'
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ['node_modules', 'venv', '.git', 'output']]
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'rb') as fh:
                if fh.read(3) == bom:
                    print(path)
