import subprocess
content = open('config/.env', 'r', encoding='utf-8').read()
pairs = []
for line in content.split('\n'):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        pairs.append(line)
env_str = ','.join(pairs)
cmd = 'gcloud run services update maiie-system --region=us-central1 --update-env-vars="' + env_str + '"'
result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print(result.stdout)
print(result.stderr)
