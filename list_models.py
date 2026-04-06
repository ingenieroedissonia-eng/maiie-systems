from google import genai
client = genai.Client(vertexai=True, project='triple-course-481522-e2', location='global')
for m in client.models.list():
    if 'gemini' in m.name.lower():
        print(m.name)