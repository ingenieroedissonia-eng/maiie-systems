lines = open('api/main.py', 'r', encoding='utf-8').read().split('\n')
for i, l in enumerate(lines[147:170], start=148):
    print(f'{i}: {repr(l)}')
