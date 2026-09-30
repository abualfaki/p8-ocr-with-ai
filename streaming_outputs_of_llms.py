import os
from dotenv import load_dotenv
from llama_index.llms.openai import OpenAI

load_dotenv(override=True)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

handle = OpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY).stream_complete("William Shakespeare is ")


print(type(handle))

for token in handle:
    print(token.delta, end="", flush=True)
