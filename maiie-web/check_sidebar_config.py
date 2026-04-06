content = open('src/components/Sidebar.jsx', 'r', encoding='utf-8').read()
idx = content.find('config')
print(content[idx-50:idx+200])
