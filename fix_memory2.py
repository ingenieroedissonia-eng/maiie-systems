path = 'core/mission_memory.py'
c = open(path, encoding='utf-8').read()
n = '\n'

fixes = [
    (
        'def _listar_misiones_gcs(self) -> List[str]:' + n + '        try:' + n + '            prefix = f"{self.missions_path}/"' + n + '            blobs  = self._gcs_client.list_blobs(',
        'def _listar_misiones_gcs(self) -> List[str]:' + n + '        self._init_gcs()' + n + '        try:' + n + '            prefix = f"{self.missions_path}/"' + n + '            blobs  = self._gcs_client.list_blobs('
    ),
    (
        'def _cargar_manifest_gcs(self, mission_id: str) -> Optional[Dict]:' + n + '        try:' + n + '            blob = self._gcs_bucket.blob(',
        'def _cargar_manifest_gcs(self, mission_id: str) -> Optional[Dict]:' + n + '        self._init_gcs()' + n + '        try:' + n + '            blob = self._gcs_bucket.blob('
    ),
    (
        'def _cargar_arquitectura_gcs(self, mission_id: str) -> Optional[str]:' + n + '        try:' + n + '            blob = self._gcs_bucket.blob(',
        'def _cargar_arquitectura_gcs(self, mission_id: str) -> Optional[str]:' + n + '        self._init_gcs()' + n + '        try:' + n + '            blob = self._gcs_bucket.blob('
    ),
    (
        'def _cargar_embedding_gcs(self, mission_id: str) -> Optional[List[float]]:' + n + '        try:' + n + '            blob = self._gcs_bucket.blob(',
        'def _cargar_embedding_gcs(self, mission_id: str) -> Optional[List[float]]:' + n + '        self._init_gcs()' + n + '        try:' + n + '            blob = self._gcs_bucket.blob('
    ),
]

count = 0
for old, new in fixes:
    if old in c:
        c = c.replace(old, new, 1)
        count += 1
        print(f'OK: {old[:50]}')
    else:
        print(f'NO ENCONTRADO: {old[:50]}')

open(path, 'w', encoding='utf-8').write(c)
print(f'Total fixes: {count}/4')
