import os
import time
import asyncio
import zipfile
import pymupdf
import logging
import pandas as pd

from typing import Type, List
from io import BytesIO
from pydantic import BaseModel
from pathlib import Path

# Models
from openai import OpenAI
from llama_cloud import AsyncLlamaCloud

# Word Document creation
from docx.shared import Mm, Inches
from docxtpl import DocxTemplate

# Load in API Keys
from config import OPENAI_API_KEY, LLAMA_INDEX_KEY

# Data Model for Llama Extraction Model to return
from extraction_data_models.interac_receipts_model import interacReceiptsItems
from extraction_data_models.remittance_data_model import Remittance


# Pandas Display setting
pd.set_option("display.max_columns", None)
pd.set_option("display.max_colwidth", None)
pd.set_option("display.width", None)


# Configure Logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s\n",
)

# Intialize Logger
logger = logging.getLogger(__name__)

# Limit Aynscronus tasks to 5 
semaphore = asyncio.Semaphore(5)

async def data_extractor(
        file_path: str, 
        LLAMA_CLOUD_API_KEY = LLAMA_INDEX_KEY, 
        data_model: Type[BaseModel] = Remittance):

    ''' Takes a File, Data model anad extracts data from the doc and returns the data'''
  
    logger.info("Initializing LLAMA Cloud Service")
    client = AsyncLlamaCloud(api_key=LLAMA_CLOUD_API_KEY)  # intialize LLama CLoud
    
    async with semaphore:

        # Upload File
        logger.info("Uploading file to Llama Cloud")
        file_obj = await client.files.create(file=file_path, purpose="extract")
        logger.info("File Uploaded")

        # Intialize timer
        start_time = time.monotonic()
        next_poll = 0

        # Extract data from document
        logger.info("EXtracting data from Document")
        job = await client.extract.create(
            file_input=file_obj.id,
            configuration={
                "data_schema": data_model.model_json_schema(),
                "extraction_target": "per_doc",
                "tier": "agentic",
            },
        )

        # Poll for completeion
        while job.status not in ("COMPLETED", "FAILED", "CANCELLED"):

            now = time.monotonic()

            # poll the API every 2 seconds
            if now >= next_poll:
                job = await client.extract.get(job.id)
                next_poll = now + 2

            elapsed_time = now - start_time

            print(
            f"\rStatus: {job.status} | Elapsed time: {elapsed_time:.1f}s",
            end="",
            flush=True,
            )

            # Refresh Console every 0.1 seconds
            await asyncio.sleep(0.1)
    
    end_time = time.monotonic()
    time_to_extract = end_time - start_time


    extraction_date = time.time() # get time of extraction was completed.
    logger.info("Job Complete")

    result = job.extract_result # store Extraction data

    # Append meta data
    result.update({
        "dataExtractedAt": extraction_date,
        'time_to_extract': time_to_extract,
        'file_path': file_path
        }
    )

    return result


def ensure_docx_template(template_path: str) -> str:
    template_file = Path(template_path)

    if template_file.suffix.lower() != ".dotx":
        return str(template_file)

    output_path = template_file.with_suffix(".docx")

    with zipfile.ZipFile(template_file, "r") as source_zip, zipfile.ZipFile(output_path, "w") as target_zip:
        for item in source_zip.infolist():
            file_bytes = source_zip.read(item.filename)

            if item.filename == "[Content_Types].xml":
                file_bytes = file_bytes.replace(
                    b"application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml",
                    b"application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml",
                )

            target_zip.writestr(item, file_bytes)

    return str(output_path)


def convert_to_dataframe(extracted_data: list[dict]):

    dataframes = [] #strore dataframes in a list

    for remittance_data in extracted_data:
        dataframes.append(pd.json_normalize(
            remittance_data, 
            record_path="invoices", 
            meta=[
            "clientName",
            "clientEmail",
            "dataExtractedAt",
            "time_to_extract",
            "amountPayedInWords",
            "file_path"
        ]))

    return dataframes


def fill_word_template(
        template_path: str, 
        extracted_data: list[pd.DataFrame]
    ):

    '''
    Fill word document with data and save as a word doc
    '''

    template_path = ensure_docx_template(template_path)

    for data in extracted_data:

        client_name = data["clientName"].iloc[0]
        total_amount = data["paymentAmount"].sum()

        context = {
            "payment_deposit_date": data["paymentDate"].iloc[0],
            "client_name": client_name,
            "total_amount": total_amount,
            "amount_in_words": data["amountPayedInWords"].iloc[0],
            "purpose": "Staffing Service",
            "payment_method": "EFT",
            "prepared_by": "Abubakar Al-faki",
        }

        # Create a New Doc
        doc = DocxTemplate(template_path)
        doc.render(context) # Fill in the Template

        document = getattr(doc, "docx", doc)
        document.add_page_break()

        append_remittance(doc, data["file_path"].iloc[0]) # Append Remittance to document

        # Save document
        output_path = f"output_files/{client_name} - Amount ${total_amount:,.2f}.docx"
        doc.save(output_path)

        logger.info(f"Saved {output_path}.docx")


def append_remittance(doc, remittance_path: str):
    """
    Append an image or PDF remittance to an existing Word document.

    Args:
        doc: A python-docx Document or DocxTemplate instance.
        remittance_path: Path to an image or PDF file.

    Returns:
        The modified document object.
    """
    path = Path(remittance_path)

    if not path.exists():
        raise FileNotFoundError(f"Remittance not found: {path}")

    # DocxTemplate stores the underlying python-docx document in .docx
    document = getattr(doc, "docx", doc)

    document.add_page_break()
    # document.add_heading("Original Remittance", level=1)

    if path.suffix.lower() == ".pdf":
        pdf = pymupdf.open(path)

        try:
            for page_number, page in enumerate(pdf):
                if page_number > 0:
                    document.add_page_break()

                pixmap = page.get_pixmap(
                    matrix=pymupdf.Matrix(2, 2),
                    alpha=False,
                )

                image_stream = BytesIO(pixmap.tobytes("png"))
                document.add_picture(
                    image_stream,
                    width=Inches(5.8),
                )
        finally:
            pdf.close()

    elif path.suffix.lower() in {
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff",
    }:
        document.add_page_break()
        document.add_picture(
            str(path),
            width=Inches(6.5),
        )

    else:
        raise ValueError(
            "Unsupported remittance format. Use an image or PDF."
        )

    return doc


async def main():
    file_paths = ["example_pdfs/sa.pdf", "example_pdfs/Renna_Remittance.pdf"]
    results = await asyncio.gather(*(data_extractor(path) for path in file_paths))
    return results

results = asyncio.run(main())

dataframes = convert_to_dataframe(results)

print(results)
print("")
print(type(results))

fill_word_template('voucher_templates/receipt_voucher template_copy.dotx', dataframes)
print("Docs created")