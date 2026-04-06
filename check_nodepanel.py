content = open('maiie-web/src/components/NodeDetailPanel.jsx', 'r', encoding='utf-8').read()
idx = content.find("tab === 'code'")
print(repr(content[idx:idx+400]))
