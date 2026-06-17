import httpx

response = httpx.post(
    "http://localhost:11434/api/generate",
    json={
        "model": "qwen3:8b",
        "prompt": "hi",
        "stream": False
    },
    timeout=300
)

print(response.status_code)
print(response.text)