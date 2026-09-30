import os
import time
import json

from datetime import datetime, date

from pydantic import BaseModel, Field, EmailStr, ValidationError


class invoicesPaid(BaseModel):

    """
    These are the invoices the compnay has made a payment for.
    """

    invoiceID: str = Field(description="A unique identifier for an invoice, often a number.")
    paymentAmount: float = Field(description="Payment amount associsted with invoice number. Payment amount will be on the same row associated with the invoice number")
    invoiceDate: date = Field(description="This is the date of when the invoice was issued to the client. This is different from paymentDatw")
    paymentDate: date = Field(description="Payment date of an invoice number. Payment date will be on the same rows as the associted invoice number")

# Define Schema for LLM to Return
class Remittance(BaseModel):

    """
    This is the shape of data I want returned when data is extracted from an invoice"
    """

    dataExtractedAt: datetime = Field(description="Date data was extracted from document")
    clientName: str = Field(description="Client name. It won't be our company name Dorvict")
    clientEmail: EmailStr = Field(description="Email Address of client. Email address should contain the {@} symbol with a domain. e.g. reens.org. Do not include the domain {@dorvict.com}. Leave blank if there is no email address")
    amountPayedInWords: str = Field(description="Sum of all paymentAmounts on all invoices in words")
    invoices: list[invoicesPaid] = Field(description="List of Invoice Numbers and amounts paid for each invoice.")

# Convert Pydantic object to Json schema to provide more context to LLM 
# and intrusct the LLM on the shape of how to to return data
remittance_schema_model = Remittance.model_json_schema()