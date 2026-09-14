import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    print("OpenAI key have been loaded")
else:
    print("\nOpenAI key hasn't loaded\n\n")

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Write me rhyme that Ice cube would say"
)

print(f"\n\nWhole Response: {response}")
print(f"R\n\nesponse from LLM: {response.output_text}")
print(type(response))