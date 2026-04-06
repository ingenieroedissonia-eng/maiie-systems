lines = open('src/services/apiService.js', 'r', encoding='utf-8').read().split('\n')
lines[57] = "      throw new ApiError(errorData.message || 'API Error: ' + response.statusText, response.status);"
open('src/services/apiService.js', 'w', encoding='utf-8').write('\n'.join(lines))
print('OK')
