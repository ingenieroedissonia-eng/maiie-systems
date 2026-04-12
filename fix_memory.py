path = 'core/mission_memory.py'
c = open(path, encoding='utf-8').read()

# Reemplazar __init__ para no llamar _init_gcs en startup
old = '''        if self.backend == "gcs":
            self._init_gcs()
        else:
            if not os.path.exists(self.missions_path):
                logger.warning(f"Directorio de misiones no encontrado: {self.missions_path}")'''

new = '''        self._gcs_client = None
        self._gcs_bucket = None

        if self.backend != "gcs":
            if not os.path.exists(self.missions_path):
                logger.warning(f"Directorio de misiones no encontrado: {self.missions_path}")
        else:
            logger.info(f"GCS Memory configurado (lazy): gs://{self.bucket_name}")'''

if old in c:
    open(path, 'w', encoding='utf-8').write(c.replace(old, new, 1))
    print('OK __init__')
else:
    print('NO ENCONTRADO __init__')

# Reemplazar _init_gcs para que sea lazy
c = open(path, encoding='utf-8').read()
old2 = '''    def _init_gcs(self):
        try:
            from google.cloud import storage as gcs
            self._gcs_client = gcs.Client()
            self._gcs_bucket = self._gcs_client.bucket(self.bucket_name)
            logger.info(f"🧠 MissionMemory conectada a GCS: gs://{self.bucket_name}")
        except ImportError:
            raise RuntimeError(
                "google-cloud-storage no está instalado. "
                "Ejecuta: pip install google-cloud-storage"
            )
        except Exception as e:
            raise RuntimeError(f"Error inicializando MissionMemory GCS: {e}")'''

new2 = '''    def _init_gcs(self):
        if self._gcs_client is None:
            try:
                from google.cloud import storage as gcs
                self._gcs_client = gcs.Client()
                self._gcs_bucket = self._gcs_client.bucket(self.bucket_name)
                logger.info(f"GCS Memory conectado: gs://{self.bucket_name}")
            except Exception as e:
                raise RuntimeError(f"Error conectando GCS Memory: {e}") from e'''

if old2 in c:
    open(path, 'w', encoding='utf-8').write(c.replace(old2, new2, 1))
    print('OK _init_gcs')
else:
    print('NO ENCONTRADO _init_gcs')
