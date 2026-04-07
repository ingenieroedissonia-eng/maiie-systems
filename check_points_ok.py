lines = open('maiie-web/src/components/GraphConsole.jsx', 'r', encoding='utf-8').read().split('\n')
for i, l in enumerate(lines[154:165], start=155):
    print(f'{i}: {l}')
