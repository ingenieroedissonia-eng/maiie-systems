import subprocess, json
result = subprocess.run(
    'gcloud storage cat gs://maiie-missions-prod/missions_store/e88a988bb3b0.json',
    shell=True, capture_output=True, text=True
)
print(result.stdout[:500])
print(result.stderr[:200])
