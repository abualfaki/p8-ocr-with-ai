"""
This script loads environment variables into process so other modules can run

"""
import os
import time

from dotenv import load_dotenv

# Always replace exisiting env variables in process.
load_dotenv(override=True)


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLAMA_INDEX_KEY = os.getenv("LLAMA_INDEX_KEY")

if OPENAI_API_KEY:
    print("OpenAI key have been loaded")
else:
    print("\nOpenAI key hasn't loaded\n\n")

if LLAMA_INDEX_KEY:
    print("LLAMA_INDEX_KEY loaded")
else:
    print("LLAMA_INDEX_KEY not loaded")


