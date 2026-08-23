from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

key = os.getenv("OPENROUTER_API_KEY")

print("KEY LOADED:", bool(key))
print("KEY LENGTH:", len(key) if key else 0)

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=key,
    timeout=30.0
)

print("Sending request...")

response = client.chat.completions.create(
    model="openai/gpt-5",
    max_completion_tokens=500,
    messages=[
        {
            "role": "user",
            "content": "Say only: Hello"
        }
    ]
)

print("Response received!")
print("FULL MESSAGE:")
print(response.choices[0].message)

print("CONTENT:")
print(response.choices[0].message.content)