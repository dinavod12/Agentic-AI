from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel,Field
from typing import Optional,List
from llm_model import llm
from langchain_core.prompts import ChatPromptTemplate,PromptTemplate

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

SYSTEM = (""" You are a knowledgeable financial compliance assistant.  
            Your task is to analyze Business Requirements Document (BRD) content and extract important information relevant for constructing expense policy rules.  
            For the given BRD data, generate up to 21 concise, single-topic questions that help to capture the following aspects
          - Expense type, Sub Expense Type, Country, Payment Method, Booking Channel, Eligibility, Input, Conditions for Validations, Claim submission period, Claim after Purchase date	
          - Action(Approve/Reject/Send back), APR or SBR or REJ Comments, Approval code	Rejection code, Send back code, Exceptions approval required(Yes/No), Approver designation, Approve with Exception	
          - Comments,T&E Comments										
          Ensure each question is complete, directly related to the BRD, and avoids compound sentences.  
          List each question on a separate line without numbering."""
)

#Focus only on details explicitly stated in the BRD. 
#For the given BRD chunk, generate up to five concise, single-topic questions that help capture the following aspects:  

"""SYSTEM_RuleBook = (
    "You are expert AI to transform Business Requirements Documents(BRD) into a Structued Rule Book."
    "Read the BRD data carefully and extract all appicable expense policy rules using the RuleRow schema."
    "For the given BRD Chunk and related context, extract **one accurate and concise rule**. "
    "Only use details explicitly mentioned in the BRD text. Do not infer unrelated points. "
    "If a field is not mentioned, leave it blank. "
    "Your goal is precision - produce a RuleRow represting that include all the RuleRow in this section"
)"""
"Generate rules for every unique combination stated or implied. If a scenario is not approved or is restricted,"
"For each ryule, consider all possible combinations of Payment Method, Booking Channel, Eligibility criteria, Country, Expense Type,"
"Sub Expense Type and other relevant fields presented in the BRD."

"include a rule indicating the proper action. ONLY use explicit facts in the BRD; leave fields blank if unspecified."
""

"""SYSTEM_RuleBook = (
    "You are expert AI to transform Business Requirements Documents(BRD) into a Structured Rule Book. "
    "Read the BRD data carefully and extract all applicable expense policy rules using the RuleRow schema. "
    "For the given BRD  and related context, extract the accurate and concise rule. "
    "Only use details explicitly mentioned in the BRD text. Do not infer unrelated points. "
    "If a field is not mentioned, leave it blank. "
    "Your goal is precision. Generate rules for every unique combination stated or implied. "
    "If a scenario is not approved or is restricted, indicate the proper action. "
    "For each rule, generate at least 20 rule like  RuleRow Structured But It should contains all the column that is define in RuleRow .Please Take care of it. "
    
)"""

SYSTEM_RuleBook = ( """
    You are an expert Travel & Expense (T&E) policy analyst. 
    Your task is to read the provided source text (a chunk from a BRD/policy) and extract important ** text that is used in making the RuleBook**.

    ### One rule object must include ALL of the following string fields (use empty string "" if not explicitly present in the text):

    - expense_type: Specify the expense type whether it is airfare/meals/hotel etc
    - sub_expense_type: Specify the sub expense ex: baggage, seat, cabin etc
    - country: Specify the country where the rule is applicable
    - payment_method: Specify the payment method whether it is Amex or Cash OOP (cash out of pocket) or both
    - booking_channel: Specify the booking channel ex: CWT or Self booking
    - eligibility_input: Specify the eligibility based on designation ex: VP & mention "ALL" if it is applicable to all designations
    - conditions_for_validations: Extract the condition for validations and elaborate it
    - claim_submission_period: Specify the claim submission period if any
    - claim_after_travel: Specify "YES" if the claim is after travel and "NO" for before travel
    - action: Specify the action whether it is Approve or Send Back or Reject
    - apr_sbr_reg_comments: Specify the detailed comments on approve/reject/send back
    - approval_code: Specify the approval code if any
    - rejection_code: Specify the rejection code if any
    - send_back_code: Specify the send back code if any
    - exceptions_approval_required: Specify whether the exceptions approval required
    - approver_designation: Specify the approver designation
    - approve_with_Exception: Specify if there is any approval with exception condition
    - comments: Specify the detailed comments about the rule
    - TEcomments: Specify the detailed comments about the rule


    ### Extraction principles
    - **Grounded**: Extract only what is explicitly supported by the text. Do not invent values.
    - **Most specific rule**: If a general rule and a more specific rule both apply, create separate objects; the specific one must reflect its stricter condition(s).
    - **Multiple rules**: If the text describes distinct scenarios (e.g., domestic vs international), output **one object per scenario**.
    - **Missing info**: Use "" (empty string) rather than null, N/A, or omitting the fie
    """)


prompt_extract = ChatPromptTemplate.from_messages([
    ("system", SYSTEM), ("human", "{data}")
])

#prompt_rulebook = ChatPromptTemplate.from_messages([
#    ("system", SYSTEM_RuleBook), ("human", "{data}")
#])

prompt_rulebook = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_RuleBook), ("human", "BRD Section:\n {chunk} \n\n"
                                            "Related Context :\n {context} \n\n" 
                                            "Now extract RuleRow strictly that follow the valid rules.")
])



chain_extract = prompt_extract | llm
chain_rulebook = prompt_rulebook | llm.with_structured_output(RuleRow)  

#data = chain_extract.invoke({"data": Str_contect})
#print("data",data)
#print(chain_rulebook.invoke({"data": data}))
