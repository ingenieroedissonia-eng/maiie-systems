
content = open('orchestrator/pipeline.py', encoding='utf-8').read()
old = '        import re as _re'
new = '        import re as _re'
print('lineas con TODO:', [l for l in content.split(chr(10)) if 'chr(34)chr(39)' in l])
