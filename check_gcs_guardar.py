content = open('api/main.py', 'r', encoding='utf-8').read()
idx = content.find('_gcs_guardar')
print(content[idx-50:idx+500])
