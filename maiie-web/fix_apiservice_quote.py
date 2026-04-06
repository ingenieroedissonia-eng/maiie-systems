content = open('src/services/apiService.js', 'r', encoding='utf-8').read()
old = "throw new ApiError(errorData.message || API Error: , response.status);"
new = "throw new ApiError(errorData.message || API Error: , response.status);"
if old in content:
    open('src/services/apiService.js', 'w', encoding='utf-8').write(content.replace(old, new))
    print('OK')
else:
    print('NO MATCH')
