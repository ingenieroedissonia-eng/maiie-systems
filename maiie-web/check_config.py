content = open('src/App.jsx', 'r', encoding='utf-8').read()
idx = content.find("activeView === 'config'")
print(content[idx-20:idx+300])
