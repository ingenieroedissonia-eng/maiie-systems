content = open('api/main.py', 'r', encoding='utf-8').read()
idx = content.find('threading.Thread')
print(content[idx-800:idx+200])
