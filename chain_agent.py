from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel,Field
from typing import Optional,List
from llm_model import llm
from langchain_core.prompts import ChatPromptTemplate

def read_brd_md(md_path: str) -> str:
    return Path(md_path).read_text(encoding="utf-8")

md_text = read_brd_md(r"C:\Users\2436230\OneDrive - Cognizant\Desktop\python\brd_main_steps_nested\markdown\mainstep_2.md")




def chunk_brd_by_langchain(md_text: str, max_chars: int = 5000) -> list[Document]:
    raw_chunks = []
    current_chunk = []
    for line in md_text.splitlines():
        if line.strip().startswith("## Sub Step"):
            if current_chunk:
                raw_chunks.append("\n".join(current_chunk).strip())
                current_chunk = []
        current_chunk.append(line)
    if current_chunk:
        raw_chunks.append("\n".join(current_chunk).strip())


    splitter = RecursiveCharacterTextSplitter(chunk_size=max_chars, chunk_overlap=200)
    documents = []
    for i, chunk in enumerate(raw_chunks):
        sub_docs = splitter.create_documents([chunk])
        for j, doc in enumerate(sub_docs):
            doc.metadata = {"substep_index": i + 1, "chunk_index": j + 1}
            documents.append(doc)

    return documents


Str_contect = ""
import time
for i in chunk_brd_by_langchain(md_text, max_chars=5000):
    Str_contect += i.page_content + "\n"


class RuleRow(BaseModel):

    Expensetype: Optional[str] = Field(
        default=None,
        description="Major category of the expense (e.g., Travel, Accommodation, Meals, Office Supplies). "
                    "Leave blank only if the BRD chunk is unrelated."
    )

    SubExpenseType: Optional[str] = Field(
        default=None,
        description="Sub-category under Expensetype mentioned explicitly in BRD "
                    "(e.g., Baggage, Seat Upgrade, Lodging, Meals, Equipment Purchase). "
                    "Write 'No Sub-Type' if unspecified."
    )

    Country: Optional[str] = Field(
        default=None,
        description="Geography where the rule applies. Use country codes like US, Canada, All if applicable."
    )

    PaymentMethod: Optional[str] = Field(
        default=None,
        description="Payment method specified in BRD. Examples: Corporate Amex, Cash OOP, Personal Card."
    )

    BookingChannel: Optional[str] = Field(
        default=None,
        description="Channel used for booking (e.g., Corporate Booking, Self Booking). Use BRD terminology."
    )

    Eligibility: Optional[str] = Field(
        default=None,
        description="Who is eligible as per BRD (e.g., Manager and above, All Employees). Use explicit BRD criteria."
    )

    Input: Optional[str] = Field(
        default=None,
        description="Primary input source for rule validation per BRD, e.g., Receipt, Invoice, Booking Itinerary."
    )

    ConditionsforValidations: Optional[str] = Field(
        default=None,
        description="Checklist of validations derived from BRD (e.g., receipt checks, date, eligibility, currency)."
    )

    Claimsubmissionperiod: Optional[str] = Field(
        default=None,
        description="Time window allowed for claim submission (e.g., 90 days, 180 days) as specified in BRD."
    )

    ClaimafterTravel: Optional[bool] = Field(
        default=None,
        description="True if claims permitted only after travel date; False if allowed before; None if unspecified."
    )

    Action: Optional[str] = Field(
        default=None,
        description="Outcome for the rule: Approve, Reject, Send Back, Partial Approve, Partial Reject, On Hold."
    )

    APRorSBRorREJComments: Optional[str] = Field(
        default=None,
        description="Additional comments related to approval, send back, or rejection codes from BRD."
    )

    Approvalcode: Optional[str] = Field(
        default=None,
        description="List of approval codes applicable as per BRD."
    )
    
    Rejectioncode: Optional[str] = Field(
        default=None,
        description="List of rejection codes applicable as per BRD."
    )

    Sendbackcode: Optional[str] = Field(
        default=None,
        description="List of send-back codes applicable as per BRD."
    )

    Exceptionsapprovalrequired: Optional[bool] = Field(
        default=None,
        description="True if exceptions require additional approvals; False or None otherwise."
    )

    Approverdesignation: Optional[str] = Field(
        default=None,
        description="Designated approvers for exceptions as specified in BRD."
    )

    ApprovewithException: Optional[str] = Field(
        default=None,
        description="Exception context when action is 'Approve with Exception'."
    )

    Comments: Optional[str] = Field(
        default=None,
        description="Free-form notes to explain the rule context or auditor remarks."
    )

    TEcomments: Optional[str] = Field(
        default=None,
        description="Additional remarks related to Travel Expense (or similar contexts)."
    )

    TERemarks: Optional[str] = Field(
        default=None,
        description="Final remarks relevant to Travel Expense or other expense category."
    )


class ExtractionBatch(BaseModel):
    rows: str = Field(
        description=(
            """ Extract all relevant text from the BRD document to form structured rules."""
        )
    )

SYSTEM = (
    "You are an expert AI agent for extracting important data or text from Business Requirements Documnents(BRD). "
    "Carefully read the BRD content provided and extract all relevant information that used to construct expense policy rules. "
    "Only include details that are explicitly stated in the BRD. Leave fields blank if not mentioned. "
)


SYSTEM_RuleBook = (
    "You are expert AI to transform Business Requirements Documents(BRD) into a Structued Rule Book."
    "Read the BRD data carefully and extract all appicable expense policy rules using the RuleRow schema."
    "For each ryule, consider all possible combinations of Payment Method, Booking Channel, Eligibility criteria, Country, Expense Type,"
    "Sub Expense Type and other relevant fields presented in the BRD."
    "Generate rules for every unique combination stated or implied. If a scenario is not approved or is restricted,"
    "include a rule indicating the proper action. ONLY use explicit facts the BRD; leave fields blank if unspecified."
)

prompt_extract = ChatPromptTemplate.from_messages([
    ("system", SYSTEM), ("human", "{data}")
])

prompt_rulebook = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_RuleBook), ("human", "{data}")
])

chain_extract = prompt_extract | llm.with_structured_output(ExtractionBatch)
chain_rulebook = prompt_rulebook | llm.with_structured_output(RuleRow)  
#data = chain_extract.invoke({"data": Str_contect})
#print("data",data)
#print(chain_rulebook.invoke({"data": data}))
