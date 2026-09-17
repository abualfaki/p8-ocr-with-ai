import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from datetime import datetime, date
from pydantic import BaseModel, Field, EmailStr, ValidationError
from llama_cloud import LlamaCloud



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


# OpenAI Code
# 
'''
openai_client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Write me rhyme that Ice cube would say"
)

print(f"\n\nWhole Response: {response}")
print(f"\n\nResponse from LLM: {response.output_text}")
print(type(response))
'''

# Llama Index 

class invoicesPaid(BaseModel):
    invoiceNumber: int = Field(description="Invoice number associted with payment date and payment amount on the same row.")
    paymentAmount: float = Field(description="Payment amount associsted with invoice number. Payment amount will be on the same row associated with the invoice number")
    paymentDate: date = Field(description="Payment date of an invoice number. Payment date will be on the same rows as the associted invoice number")

# Define Schema using Pydantic
class Remittance(BaseModel):
    dataExtractedAt: datetime = Field(description="Date data was extracted from document")
    clientName: str = Field(description="Client name. It won't be our company name Dorvict")
    clientEmail: EmailStr = Field(description="Email Address of client. It won't contain the domain {@dorvict.com}")
    invoices: list[invoicesPaid] = Field(description="List of Invoice Numbers on Remittance")

client = LlamaCloud(api_key=LLAMA_INDEX_KEY)

# Upload Remittance to extract data
file_obj = client.files.create(file="example_pdfs/ESCS.pdf", purpose="extract")


# Extract data from documment
job = client.extract.create(
    file_input=file_obj.id,
    configuration={
        "data_schema": Remittance.model_json_schema(),
        "extraction_target": "per_doc",
        "tier": "cost_effective",
    },
)

start_time = time.monotonic()

while job.status not in ("COMPLETED", "FAILED", "CANCELLED"):
    elapsed_time = time.monotonic() - start_time

    print(
        f"\rStatus: {job.status} | Elapsed: {elapsed_time:.1f}s",
        end="",
        flush=True,
    )

    time.sleep(2)
    job = client.extract.get(job.id)

print()
elapsed = time.monotonic() - start_time

print(f"Job finished with status {job.status} in {elapsed:.1f}s\n\n")
print(job.extract_result)

print()
print()
print(job)