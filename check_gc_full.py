content = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read()
lines = content.split('\n')
for i, l in enumerate(lines, 1):
    print(f'{i}: {l}')
