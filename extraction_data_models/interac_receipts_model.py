from pydantic import BaseModel, Field, EmailStr
from datetime import date
from typing import Annotated
import json


"This is the data model you will select when extracting date from invoices"


class interacReceiptsItems(BaseModel):

    """
    Extract data from invoices paid using Interac eTransfer
    """
    clientName: str = Field(description="The Person or company that sent the money")
    clientEmail: EmailStr = Field(description="Email Address of client. Email address should contain the {@} symbol with a domain. e.g. reens.org. Do not include the domain {@dorvict.com}. Leave blank if there is no email address")
    paymentDate: date = Field(description="This is the date the money was sent. Always under date")
    referenceNumber: str = Field(decription="A unique ID of the interac receipt. It is a mixture of numbers and letters")
    amountPayed: float = Field(description="Transferred or deposited amount as a numeric value.")
    amountPayedInWords: str = Field(description="amountPayed in words")
    invoicesPaid: list[str] = Field(description="List of invoices paid will be under the Message:")

interactData = interacReceiptsItems.model_json_schema()