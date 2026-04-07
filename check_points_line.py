lines = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read().split('\n')
for i, l in enumerate(lines):
    if 'points=' in l:
        print(f'{i+1}: {repr(l)}')
