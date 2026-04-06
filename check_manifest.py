import subprocess
result = subprocess.run(
    'gcloud storage cat gs://maiie-missions-prod/output/missions/mission_20260331_190633_f123148a/mission_manifest.json',
    shell=True, capture_output=True, text=True
)
print(result.stdout)
