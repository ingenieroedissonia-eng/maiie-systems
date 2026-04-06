import subprocess
result = subprocess.run(
    'gcloud storage ls gs://maiie-missions-prod/output/missions/ --recursive',
    shell=True, capture_output=True, text=True
)
print(result.stdout[:3000])
