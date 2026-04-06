from google import genai

client = genai.Client(
    vertexai=True,
    project="triple-course-481522-e2",
    location="global"
)

response = client.models.generate_content(
    model="gemini-3.1-pro-preview",
    contents="M.A.I.I.E system check: confirm connection."
)

print(response.text)