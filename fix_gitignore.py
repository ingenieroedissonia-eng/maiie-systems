content = open('.gitignore', encoding='utf-8').read()
if 'maiie-web/dist/' not in content:
    content += '\nmaiie-web/dist/\n'
    open('.gitignore', 'w', encoding='utf-8').write(content)
    print('OK - dist agregado')
else:
    print('YA EXISTE')
