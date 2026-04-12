path = 'utils/artifact_manager.py'
c = open(path, encoding='utf-8').read()

# Encontrar el __init__ de GCSStorage y reemplazarlo completo
start = c.find('    def __init__(self, bucket_name: str):')
end = c.find('    def _get_bucket(self):')

if start == -1 or end == -1:
    print(f'NO ENCONTRADO start={start} end={end}')
else:
    old_init = c[start:end]
    print('INIT ACTUAL:')
    print(repr(old_init))
    
    new_init = '''    def __init__(self, bucket_name: str):
        self._bucket_name = bucket_name
        self._client = None
        self._bucket = None
        logger.info(f"GCS Storage configurado (lazy): gs://{bucket_name}")

'''
    new_content = c[:start] + new_init + c[end:]
    open(path, 'w', encoding='utf-8').write(new_content)
    print('OK')
