import os
import time
import asyncio
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.agent.workflow import FunctionAgent
from llama_index.llms.openai import OpenAI


from dotenv import load_dotenv

# Load environment variables into the python process
load_dotenv(override=True)

# Make the OpenAI PI key available to the script.
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    print(f"Open AI api key loaded")
else:
    print(f"Open AI api key no loaded")


# Create a RAG toll using LlamaIndex
documents = SimpleDirectoryReader(input_dir="data").load_data()

index = VectorStoreIndex.from_documents(documents)
print(f'Index: {index}')

query_engine = index.as_query_engine()
print(f'query_engine: {query_engine}')

# Define a simple calculator tool
def multiply(a: float, b : float) -> float:
    ''' Multply two numbers'''
    return a * b

async def search_documents(query: str) -> str:
    """Useful for answering natural language questions about an personal essay written by Paul Graham."""
    response = await query_engine.aquery(query)
    return str(response)

class HashableFunctionAgent(FunctionAgent):
    __hash__ = object.__hash__

# create an agent workflo with our calculator tool
agent = HashableFunctionAgent(
    tools=[multiply, search_documents],
    llm=OpenAI(model="gpt-4o-mini", api_key=OPENAI_API_KEY),
    system_prompt="You are a helpful assistant that can multiply two numbers and search through" \
    "documens to answer questions.",
)

async def main():
    # Run the agent
    response = await agent.run(user_msg='"What 3 grad schools fid the author apply to?')
    print(str(response))

# Run the agent
if __name__ == '__main__':
    asyncio.run(main())