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

    Expense_type: Optional[str] = Field(
        default=None,
        description=(
            "Parent expense type. For this BRD "
            "Leave blank only if the BRD chunk is unrelated."
        ),
    )

    Sub_Expense_Type: Optional[str] = Field(
        default=None,
        description=(
            "Sub-category under BRD when explicitly mentioned in BRD: e.g., 'Baggage', 'Seat/Cabin Upgrade', "
            "'Premium Lounge', 'Airfare Cancellation', 'Airfare Rescheduling', 'Agency Booking Fees', "
            "'In Flight WiFi', 'Baggage Wrapping'. Or write it No Sub-Type if unspecified in BRD."
        ),
    )

    Country: Optional[str] = Field(
        default=None,
        description=(
            "Geography the rule applies to. Use 'US', 'Canada', 'US or Canada', or 'All' (when the rule applies "
            "irrespective of country). BRD specifies different receipt rules for US (<= $75 for Amex) and "
            "Canada (>= $1 for any amount)."
        ),
    )

    Payment_Method: Optional[str] = Field(
        default=None,
        description=(
            "Payment method from BRD. Use 'Corporate Amex' for corporate card transactions and "
            "'Cash OOP (Personal Card)' for out-of-pocket/personal card. "
            "Personal card generally requires payment proof (bank statement) and approval after travel date; "
            "Corporate Amex may be approved before travel date subject to receipt rules."
        ),
    )

    Booking_Channel: Optional[str] = Field(
        default=None,
        description=(
            "Booking channel per BRD: 'CWT' (including MyCWT corporate channel) or 'Self Booking'. "
            "Self Booking requires Global Travel Services email approval; use APR A-APR-SLFA if instructed. "
            "CWT bookings can be validated via itinerary in Concur."
        ),
    )

    Eligibility: Optional[str] = Field(
        default=None,
        description=(
            "Who is eligible / band constraints per BRD (e.g., 'AVP & below', 'VP/SVP', 'Director and above', "
            "'Chiefs/Presidents'). Use BRD articulation; examples: "
            "AVP & below → Economy/main cabin; VP/SVP → Business only for >6hr international (<= $7000 round trip); "
            "Chiefs/Presidents → Business (no cap)."
        ),
    )

    Input: Optional[str] = Field(
        default=None,
        description=(
            "Primary input artifact/source for validation per BRD, typically: 'Concur', "
            "'CWT Receipt/Itinerary', 'Airline Invoice or booking receipt', or 'EMD' for sub-expenses."
        ),
    )

    Conditions_for_Validations: Optional[str] = Field(
        default=None,
        description=(
            "Checklist of validations derived from BRD: Report Header checks (Country/Policy Type/Business Purpose), "
            "Receipt checks (Associate name, Date of travel, Amount & currency, Duration, Class vs Eligibility), "
            "and specific notes (e.g., itinerary acceptable for MyCWT, boarding pass rules for OOP)."
        ),
    )

    Claim_submission_period: Optional[str] = Field(
        default=None,
        description=(
            "Window per BRD (e.g., '<180 days' or '>180 days'). Use '>180 days' to trigger EC exception "
            "approval requirements (APEC code) as noted in BRD."
        ),
    )

    Claim_after_Travel: Optional[bool] = Field(
        default=None,
        description=(
            "True if BRD states the claim must be submitted only after travel date (e.g., personal card/OOP airfare), "
            "False if approval can happen before travel date (e.g., Corporate Amex per BRD). Use None if unspecified."
        ),
    )

    Action: Optional[str] = Field(
        default=None,
        description=(
            "Outcome per BRD for the scenario: one of "
            "['Approve', 'Reject', 'Send Back', 'Partial Approve', 'Partial Reject', 'On hold']."
        ),
    )

    APR_or_SBR_or_REJ_Comments: Optional[str] = Field(
        default=None,
        description=(
            "Any BRD-specific notes to accompany applied codes (APR/SBR/REJ), e.g., ' Need exception approval', 'Missing supporting document', 'Incorrect expense type'."
        ),
    )

    
    Approval_code: Optional[str] = Field(
        default=None,
        description=(
            "List of APR codes per BRD (e.g., A-APR-TRIN, A-APR-SLFA, D-APR-SEGR, D-APR-LOUN, "
            "A-APR-CANC, A-APR-BORD, A-APR-BAGW). Use only codes present in BRD (Sub Step 2.7 & elsewhere)."
        ),
    )

    Rejection_code: Optional[str] = Field(
        default=None,
        description=(
            "List of REJ codes per BRD (e.g., REJ-SEATUP, REJ-LOUNGE, REJ-LOST, REJ-AIRFAR, REJ-OTPLCY, "
            "REJ-DUPLIC, REJ-FUTPYT, REJ-WALLET). Use only codes present in BRD (Sub Step 2.8 & scenarios)."
        ),
    )

    Send_back_code: Optional[str] = Field(
        default=None,
        description=(
            "List of SBR codes per BRD (e.g., SBR-SLFBKG, SBR-DEPBUS, SBR-WRNPOL, SBR-WRNEXP, SBR-RCTMTH, "
            "SBR-WRGDT, SBR-CURMIS, SBR-ITEMZD, SBR-ADDSUP, SBR-180DAY). Use only codes present in BRD."
        ),
    )

    Exceptions_approval_required: Optional[bool] = Field(
        default=None,
        description=(
            "True if BRD requires exception approval (e.g., EC for >180 days, CFO for room/class/amount exceptions, "
            "Global Travel Services for self-booking), otherwise False; None if not specified."
        ),
    )

    Approver_designation: Optional[str] = Field(
        default=None,
        description=(
            "Approver per BRD when exceptions apply (e.g., 'EC', 'D+', 'CFO', 'Global Travel Services Team'). "
            "For self-booked airfare, approver email is TravelMailbox@cognizant.com as per BRD."
        ),
    )

    Approve_with_Exception: Optional[str] = Field(
        default=None,
        description=(
            "If Action is 'Approve with Exception', capture the exception context per BRD (e.g., 'APE-BUSI'). "
            "Leave blank otherwise."
        ),
    )

    Comments: Optional[str] = Field(
        default=None,
        description=(
            "Free-form BRD notes that help the auditor (e.g., 'Use highest priority code in comments', "
            "'Write comments at item and report header level')."
        ),
    )

    TE_comments: Optional[str] = Field(
        default=None,
        description="Additional Travel & Expense remarks from BRD applicable to auditing behavior.",
    )

    TE_Remarks: Optional[str] = Field(
        default=None,
        description="Any final T&E remark not already covered.",
    )


class ExtractionBatch(BaseModel):
    rows: List[str] = Field(
        description=(
            """ Extract all relevant text from the BRD document to form structured rules."""
        )
    )

SYSTEM = """You are expert AI to Extract important data or text from Business Requirements Documents(BRD) .Please read the BRD data carefully and extract all relevant data that is used to form expense policy rules"""

SYSTEM_RuleBook = """You are expert AI to transform Business Requirements Documents(BRD) into a Structued Rule Book.Read the BRD data carefully and extract all relevant expense policy rules into structured format as per the RuleRow schema.And Also use different conditions based on the BRD content. Please ensure that the extracted rules are accurate and comprehensive. Provide all the rules one by one in the output that has formed using different conditions based on the BRD content.
Like we have different Payment Methods, Booking Channels, Expense Types, Sub Expense Types, Countries, Eligibility criteria etc. You can form combinations of these conditions to form different rules.For eg. In one Bookin Channel CWT and Payment Method Corporate Amex we have certain rules, similarly for Self Booking and Payment Method Cash OOP we have different rules.
You have to also provide the rule which are not going to be approved as per the BRD.
Use only BRD facts. If something is not in BRD, leave it blank..
"""

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
