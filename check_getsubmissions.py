content = open('maiie-web/src/services/apiService.js', 'r', encoding='utf-8').read()
idx = content.find('getSubmissions')
print(content[idx:idx+300])
