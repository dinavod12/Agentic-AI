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
        description="Major category of the Expense Type are (e.g., Airfare, Hotel, Individual MealsMeals, e.t.c). "
    )

    SubExpenseType: Optional[str] = Field(
        default=None,
        description="Sub-category under Expensetype mentioned explicitly in BRD "
                    "(e.g., Baggage, Seat Upgrade, Lodging, Meals, Equipment Purchase). "
                    "Write 'No Sub-Type' if unspecified."
    )

    Country: Optional[str] = Field(
        default=None,
        description="Geography where the rule applies. Use country codes like USA, Canada.If Not specified use USA or Canada"
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
        description="Who is eligible as per BRD (e.g., Manager and above, All Employees,Chiefs / Presidents). Use explicit BRD criteria."
    )

    Input: Optional[str] = Field(
        default=None,
        description="Primary input source for rule validation per BRD, e.g., Concur Itemized hotel Receipt Payment of proof (For personal Amex or Cash OOP) if payment mode is not available.."
    )

    ConditionsforValidations: Optional[str] = Field(
        default=None,
        description="Checklist of validations derived from BRD (e.g., receipt checks, date, eligibility, currency). For example Expense Type - Hotel. Subexpense - Individual Meal. " \
                    "Report Header Validation Country/Employee Group : US or Canada Policy Type :  Business Expense-US or Business Expense-Canada " \
                    "Business purpose :  Business travel (This can be checked by validating the previous reports of the associate or through PTA code.) Employee Grade : Any" \
                    "Expense Receipt Validation: Name of the associate (optional) Date Amount & Currency (Per day Meal- upto 50 USD OR 50 CAD )" \
                    "No. of Guests Validate Entered detail in Concur Matches Receipt or Payment proof (if payment mode is not available)" \
                    "Name of associate (if available) Transaction date =  Receipt and Concur Amount & Currency = Receipt and Concur (Tax can be combined with individual  meals)" \
                    "Audit Rule/Warning : Validated Check if PTA code is available. (From T&E app)"
    )

    Claimsubmissionperiod: Optional[str] = Field(
        default=None,
        description="Time window allowed for claim submission (e.g.,<180 days) as specified in BRD."
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
        description="List of approval codes applicable as per BRD. For an example -  A-APE-BUSI, A-APR-SLFA, A-APR-TRIN e.t.c"
    )
    
    Rejectioncode: Optional[str] = Field(
        default=None,
        description="List of rejection codes applicable as per BRD. For an example - REJ-WALLET - AMEX , REJ-OTPLCY, REJ-LOUNGE e.t.c"
    )

    Sendbackcode: Optional[str] = Field(
        default=None,
        description="List of send-back codes applicable as per BRD. For an example SBR-ADDSUP, SBR-WRNPOL, SBR-ITEMZD  e.t.c"
    )

    Exceptionsapprovalrequired: Optional[bool] = Field(
        default=None,
        description="True if exceptions require additional approvals; False or None otherwise."
    )

    Approverdesignation: Optional[str] = Field(
        default=None,
        description="Designated approvers for exceptions as specified in BRD. For an example Global Travel Services Team, D+, Email from HR e.t.c"
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

"""class RuleRow(BaseModel):

    Expensetype: Optional[str] = Field(
        default=None,
        description="Category for the ExpenseType are (e.g., Airfare, Hotel, Individual Meals). It Must be explicitly mentioned ."
    )

    SubExpenseType: Optional[str] = Field(
        default=None,
        description="Specific sub-category under Expensetype, as mentioned in the BRD (e.g., Baggage, Seat Upgrade, Lodging, Airfare Cancellation, Seat/Cabin Upgrade). "
                    "This may appear in formats like 'Sub expenses for Airfare' or 'Hotel – Sub Expense'. "
                    "Use 'No' if no sub-category is explicitly mentioned."

    )

    Country: Optional[str] = Field(
        default=None,
        description="Country where the rule applies. Allowed values: 'USA' or 'Canada'. If not specified, default is USA OR Canda."
    )

    PaymentMethod: Optional[str] = Field(
        default=None,
        description="Method of payment used (e.g., Corporate Amex, Cash OOP). Must be explicitly stated or logically inferred from BRD."
    )

    BookingChannel: Optional[str] = Field(
        default=None,
        description="Channel used for booking (e.g., CWT, Self Booking). Use terminology from BRD only."
    )

    Eligibility: Optional[str] = Field(
        default=None,
        description="Eligibility criteria as per BRD (e.g., All Employees, Manager and above). Must be explicitly stated or logically derived."
    )

    Input: Optional[str] = Field(
        default=None,
        description="Source documents or triggers for rule validation (e.g., Receipt, Invoice, Booking Itinerary). Must be mentioned in BRD."
    )

    ConditionsforValidations: Optional[str] = Field(
        default=None,
        description="Checklist of validations derived from BRD (e.g., receipt checks, travel dates, eligibility, refund logic)."
    )

    Claimsubmissionperiod: Optional[str] = Field(
        default=None,
        description="Time window allowed for claim submission (e.g., '<180 days') as specified in BRD."
    )

    ClaimafterTravel: Optional[bool] = Field(
        default=None,
        description="True if claims are allowed only after travel; False if allowed before; None if not specified in BRD."
    )

    Action: Optional[str] = Field(
        default=None,
        description="Final decision for the rule: Approve, Reject, Send Back. Use only these values unless BRD specifies others."
    )

    APRorSBRorREJComments: Optional[str] = Field(
        default=None,
        description="Comments related to approval, send back, or rejection. Must be derived from BRD codes or remarks."
    )

    Approvalcode: Optional[str] = Field(
        default=None,
        description="Approval code(s) applicable as per BRD. Leave blank if not mentioned."
    )

    Rejectioncode: Optional[str] = Field(
        default=None,
        description="Rejection code(s) applicable as per BRD. Leave blank if not mentioned."
    )

    Sendbackcode: Optional[str] = Field(
        default=None,
        description="Send-back code(s) applicable as per BRD. Leave blank if not mentioned."
    )

    Exceptionsapprovalrequired: Optional[bool] = Field(
        default=None,
        description="True if exception approval is required; False or None otherwise. Must be explicitly stated in BRD."
    )

    Approverdesignation: Optional[str] = Field(
        default=None,
        description="Designation of approver for exceptions (e.g., Manager, Director). Use BRD terminology."
    )

    ApprovewithException: Optional[str] = Field(
        default=None,
        description="Context or justification when rule is approved with exception. Must be derived from BRD."
    )

    Comments: Optional[str] = Field(
        default=None,
        description="General notes or remarks explaining the rule logic or auditor observations."
    )

    TEcomments: Optional[str] = Field(
        default=None,
        description="Additional comments related to Travel & Expense policy or BRD context."
    )

    TERemarks: Optional[str] = Field(
        default=None,
        description="Final remarks relevant to Travel & Expense or other expense categories. Use BRD language."
    )"""


class ExtractionBatch(BaseModel):
    Expensetype: Optional[str] = Field(
        default=None,
        description="Primary category of the ExpenseType are (e.g., Airfare, Hotel, Individual Meals). It Must be explicitly mentioned ."
                    "If the 'Expense Type' field is not mentioned in the BRD, use the previously identified Expense Type field as the default."
    )
    rows: str = Field(
        description=(
            """ Extract all relevant text from the BRD document to form structured rules."""
        )
    )

#SYSTEM = (""" You are a knowledgeable financial compliance assistant.  
#            Your task is to analyze Business Requirements Document (BRD) content and extract important information relevant for constructing expense policy rules.  
#            For the given BRD data, generate up to 21 concise, single-topic questions that help to capture  										
#          Ensure each question is complete, directly related to the BRD, and avoids compound sentences.  
#          List each question on a separate line without numbering."""
#)

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

"""SYSTEM_RuleBook = (  You are an expert AI assistant tasked with transforming Business Requirements Documents (BRD) into a structured RuleBook.
                   Carefully read the BRD content and extract all applicable expense policy rules using the RuleRow schema.

                   ** Note : Before moving forward Please make sure to understand the context of the BRD (Business Requirements Document) as a human would. Consider how a person might use this context to develop a meaningful and practical RuleBook. **
                   ** Note : The column conditions for validation should be described in more detail. Think step-by-step, like an expert human assistant would—clearly outlining the logic and reasoning behind each condition.**

                   The RuleRow schema includes the following columns:

                   Expense Type
                   Sub Expense Type
                   Country
                   Payment Method
                   Booking Channel
                   Eligibility
                   Input Fields
                   Conditions for Validation
                   Claim Submission Period
                   Claim After Purchase Date
                   Action (Approve / Reject / Send Back)
                   APR / SBR / REJ Comments
                   Approval Code
                   Rejection Code
                   Send Back Code
                   Exceptions Approval Required (Yes/No)
                   Approver Designation
                   Approve with Exception Comments
                   T&E Comments
                   
                   **Instructions:

                   1) Extract accurate and concise rules from the BRD using only details explicitly mentioned in the document.
                   
                   2) If a field is not mentioned, but indirect hints are present, you may logically fill the field.
                      Do not infer or assume anything beyond what is supported by the document.
                   
                   3) For the Sub Expense Type field:
                   
                      If specific sub-types like Laundry, Tips and Gratitude, Internet, Airfare Cancellation/Rescheduling, Premium Lounge, etc. are not mentioned, set this field to "No".
                      Only use "No" for this field.
                   
                   4) For the Country field: 
                       If the Country field is not mentioned in BRD context. Then use USA or Canada.
                   
                   5) For Booking Channel and Payment Method:
                   
                      These fields must always contain a valid value (e.g., CWT, Self Booking, Corporate Amex, Cash OOP).
                      Never use "No" in these fields.
                   
                   6) Generate separate RuleRows for every unique combination of Booking Channel and Payment Method.
                   
                      Example:
                      If Booking Channel = CWT or Self Booking
                      and Payment Method = Corporate Amex or Cash OOP
                      → Create RuleRows for all combinations.
                   
                   7) ** Conditions for Validation
                         If the BRD says: “All attendees' details to be provided, follow validation rules in Section 5.2.” 
                                           → Go to Section 5.2, extract the actual validation logic, and do not repeat the reference.
                                            Always describe validation logic step-by-step, clearly outlining:
                                            Required fields
                                            Value checks
                                            Exceptions
                                            Dependencies **


                   Include rules for rejected cases as well. Rejected rules can also have multiple combinations.
                   
                   The output should be structured as multiple RuleRows, each containing all columns defined in the schema.**

                   ** For an Example your output should be look like this 
                   
                   "Expense Type": "Airfare",
                   "Sub Expense Type": "Airfare Cancellation",
                   "Country": "US or Canada",
                   "Payment Method": "Corporate Amex",
                   "Booking Channel": "CWT" or "Self Booking",
                   "Eligibility": "All",
                    "Input Fields": "Concur","Airline Invoice or booking receipt or CWT Receipt or Itinerary or EMD (based on booking)", "Cancellation receipt with amount highlighted",
                   "Conditions for Validation": "Associate claiming for cancellation charges, with charges highlighted in receipt.\n\n"
                                                "Note:\n"
                                                "- Validate reason for cancel in comments.\n"
                                                "- Check for any refund amount shown in negative, in payment transaction.",
                   "Claim Submission Period": "<180 days",
                   "Claim After Purchase Date": "Yes",
                   "Action (Approve / Reject / Send Back)": "Approve",
                   "APR / SBR / REJ Comments": "Refer to the Comments and Audit trail to understand the history of the report.",
                   "Approval Code": "A-APR-CANC - Cancellation / Rescheduled charges",
                   "Rejection Code": "",
                   "Send Back Code": "",
                   "Exceptions Approval Required (Yes/No)": "No",
                   "Approver Designation": "",
                   "Approve with Exception Comments": "",
                   "T&E Comments": "Create separate scenario for Amex and personal card for better clarity."
                   **
                   ) """
#4) **Combinations:** Generate separate RuleRows for every unique combination of **Booking Channel × Payment Method** mentioned or implied in BRD. If BRD lists multiple values (e.g., Booking Channel = CWT or Self Booking; Payment Method = Corporate Amex or Cash OOP), create RuleRows for **all combinations**.
SYSTEM_RuleBook = ("""  You are an expert AI assistant tasked with transforming Business Requirements Documents (BRD) into a structured RuleBook.

                        Carefully read the BRD and extract applicable expense policy rules using the RuleRow schema. Think step-by-step like an expert human analyst. Always return a  RuleRows (no extra text).

                        **Schema (canonical column names):**
                        - Expense Type
                        - Sub Expense Type
                        - Country
                        - Payment Method
                        - Booking Channel
                        - Eligibility
                        - Input Fields
                        - Conditions for Validation
                        - Claim Submission Period
                        - Claim After Purchase Date
                        - Action (Approve / Reject / Send Back)
                        - APR / SBR / REJ Comments
                        - Approval Code
                        - Rejection Code
                        - Send Back Code
                        - Exceptions Approval Required (Yes/No)
                        - Approver Designation
                        - Approve with Exception Comments
                        - T&E Comments
                        - T&E Remarks
                   
                       **Instructions:**
                     
                          1) Understand BRD context deeply before extracting rules. Use only explicit details; if indirect hints exist, logically fill fields without over-assumption.
                          2) If a field is not mentioned in the BRD, but indirect hints are present, you may logically fill the field using only what is supported by the document. Do not infer or assume anything beyond what is explicitly or implicitly supported by the BRD context.
                          3) **Field Defaults and Constraints:**
                              - Sub Expense Type: If not mentioned, set to **"No"**.
                              - Country: If not mentioned, set to **"US or Canada"**.
                              - Payment Method and Booking Channel: Must be valid values (e.g., **Corporate Amex**, **Cash OOP**; **CWT**, **Self Booking**). Never use "No".
                          4) ** Combinations: **
                                   - Do NOT create separate rows for each Booking Channel. Instead: * If the BRD specifies Booking Channels, use them exactly as mentioned (e.g., "CWT", "Self Booking", or combined as "CWT or Self Booking").* If the BRD does NOT mention any Booking Channel, set the default value to "CWT or Self Booking" "
                                   - Create separate RuleRows for each Action type: Approve, Reject, and Send Back.
                                   - For Approve rows: Include full Conditions for Validation as per BRD.
                                   - For Reject rows:
                                        * Include Conditions for Validation rewritten to reflect failure points that caused rejection.
                                        * Do NOT copy approval logic. Instead, highlight what was missing or invalid.
                                        * Example: "Step 1: Receipt missing or incomplete. Step 2: Payment proof not provided for Cash OOP. Step 3: Itemization does not match receipt."
                                        * These failure points MUST come from BRD or indirect hints (e.g., missing receipt, missing payment proof, exceeding rent cap without CFO approval).
                                   - For Send Back rows:
                                        * Include Conditions for Validation rewritten to reflect fixable issues that caused send back.
                                        * Example: "Step 1: Missing city of stay. Step 2: Incorrect room rent itemization. Step 3: Business purpose unclear."
                                        * These fixable issues MUST come from BRD or indirect hints (e.g., missing city of stay, incorrect itemization, unclear business purpose).
                                   - Use distinct codes for each Action type Only If the field is present in the BRD context.If the field is not present in BRD context use "" (empty string)
                                         * Approval Code for Approve rows (e.g., A-APR-ALCO	--- Alcohol expenses for individual and team meals	All Associates )
                                         * Rejection Code for Reject rows (e.g., REJ-NOSHOW	--- No Show Charges	Rejected as out-of-policy)
                                         * Send Back Code for Send Back rows (e.g., SBR-BUSEXP --- Business Expenses related restriction	Not allowed)
                          5) ** Input Fields: **
                               - Combine all required inputs from BRD into one field.
                               - Use clear separators (e.g., semicolons or line breaks).
                               - Include:
                                    * System name (e.g., Concur)
                                    * Receipt requirements (e.g., Itemized day-wise receipt with rent and tax separate)
                                    * Payment proof conditions (e.g., For Personal Amex or Cash OOP if payment mode is not available)
                                    * Any exceptional approval requirements (e.g., CFO approval if hotel rent exceeds $300 or $350 per day based on city)
                               - Example: "Concur; Itemized day-wise receipt (Rent and tax should be separate); Payment proof (mandatory for Personal Amex or Cash OOP if payment mode is not available); Exceptional approval from CFO team if Hotel rent > $300 or $350 per day (based on city)"
                          6) **Conditions for Validation (step-by-step, granular):**
                              - Clearly list required vs optional input fields.
                              - Define value checks and thresholds (e.g., **$300/day cap** or **$350/day for certain cities**).
                              - State dependencies (e.g., “If payment is personal Amex or Cash OOP, require payment proof.”).
                              - Validate itemization structure (e.g., rent and tax **separate line items per day**).
                              - Confirm Concur itemization **matches receipt**: dates, amounts, currency, vendor name (optional), transaction date equals **card swipe date**, **No. of guests = 1**, **Mode of payment** clearly indicated.
                              - Include conditional triggers/exceptions (e.g., **CFO team approval** if over cap).
                              - Include any audit rule/warning stated by BRD.
                              - If the BRD references another section (e.g., “Ensure compliance with validation rules in Section 5.2”), DO NOT copy the reference. Instead, extract the actual validation logic from that section and write it explicitly in step-by-step detail.
                          7) If the field **Claim Submission Period** is not mentioned in the BRD, set its value to  **<180 days** by default.
                          8) **Rejected / Send Back Rules:** If BRD specifies reject or send-back scenarios or codes, include those RuleRows and populate **Rejection Code** or **Send Back Code** accordingly. If not stated, leave code fields as **""** (empty string).
                          9) **Action Field:** Use exactly one of "Approve", "Reject", or "Send Back" as per BRD.
                          10) **Output Format:** A single **JSON array**. Each RuleRow must contain **all** schema fields (empty string "" if not specified). No extra commentary.
                          11) ** Fill the field ** Approver Designation ** from the data in BRD context" **
                          12) ** For any field not mentioned but indirect hints are present, you may logically fill the field using only what is supported by the document. Do not infer or assume anything beyond what is explicitly or implicitly supported by the BRD context.**"

                          **Example styling for Conditions for Validation (not content):**
                          "Conditions for Validation": "Step 1: Validate report header: Country/Employee Group must be US or Canada; Policy Type = Business Expense-US or Business Expense-Canada; Business purpose must relate to short business travel.\nStep 2: Validate receipt fields: Name of associate (fuzzy match), Guests = 1, Check-in and Check-out dates, City of stay, Mode of payment; Amount & Currency with itemization (Rent per day, Tax per day).\nStep 3: Room Rent Caps: <= $300/day (excluding 18 cities); <= $350/day (for 18 cities).\nStep 4: Concur itemization must match receipt exactly: dates, amounts, currency; Transaction date = card swipe date; Vendor name optional.\nStep 5: If payment is Personal Amex or Cash OOP, payment proof is mandatory.\nStep 6: If rent exceeds cap, CFO team exceptional approval required.\nAudit Rule/Warning: Validated."
                        
                         ** For an Example your output should be look like this 
                   
                         "Expense Type": "Airfare",
                         "Sub Expense Type": "Airfare Cancellation",
                         "Country": "US or Canada",
                         "Payment Method": "Corporate Amex",
                         "Booking Channel": "CWT" or "Self Booking",
                         "Eligibility": "All",
                         "Input Fields": "Concur","Airline Invoice or booking receipt or CWT Receipt or Itinerary or EMD (based on booking)", "Cancellation receipt with amount highlighted",
                         "Conditions for Validation": "Associate claiming for cancellation charges, with charges highlighted in receipt.\n\n"
                                                "Note:\n"
                                                "- Validate reason for cancel in comments.\n"
                                                "- Check for any refund amount shown in negative, in payment transaction.",
                         "Claim Submission Period": "<180 days",
                         "Claim After Purchase Date": "Yes",
                         "Action (Approve / Reject / Send Back)": "Approve",
                         "APR / SBR / REJ Comments": "Refer to the Comments and Audit trail to understand the history of the report.",
                         "Approval Code": "A-APR-CANC - Cancellation / Rescheduled charges",
                         "Rejection Code": "",
                         "Send Back Code": "",
                         "Exceptions Approval Required (Yes/No)": "No",
                         "Approver Designation": "",
                         "Approve with Exception Comments": "",
                         "T&E Comments": "Create separate scenario for Amex and personal card for better clarity." **

""")


"""SYSTEM_RuleBook = ( You are an expert AI assistant tasked with transforming Business Requirements Documents (BRDs) into a structured Expense Policy RuleBook.
                   Your ONLY task is to extract and generate RuleRows using the schema below. Each RuleRow must represent a unique, valid combination derived strictly from the BRD content.

                   RuleRow Schema
                   
                   Expense Type

                   Sub Expense Type 
                        Use specific sub-types only if explicitly mentioned (e.g., Laundry, Tips and Gratitude, Internet, Airfare Cancellation/Rescheduling, Premium Lounge).
                        If not mentioned, set this field to "No".
                   
                   Country

                   Payment Method
                      Must be a valid method (e.g., Corporate Amex, Cash OOP). Never use "No".
                   
                   Booking Channel
                       Must be a valid channel (e.g., CWT, Self Booking). Never use "No".
                   
                   Eligibility
                   
                   Input Fields
                        Include all source documents or triggers mentioned in the BRD (e.g., Concur, Airline Invoice, CWT Receipt, Supervisor Approval).
                   
                   Conditions for Validation
                   
                   Claim Submission Period

                   Claim After Purchase Date

                   Action
                      Must be one of: "Approve", "Send Back", "Reject".
                   
                   APR / SBR / REJ Comments
                   
                   Approval Code
                   
                   Rejection Code
                   
                   Send Back Code
                   
                   Exceptions Approval Required (Yes/No)
                   
                   Approver Designation

                   Approve with Exception Comments
                   
                   T&E Comments

                   **Instructions:

                   1) Extract accurate and concise rules from the BRD using only details explicitly mentioned in the document.
                   
                   2) If a field is not mentioned, but indirect hints are present, you may logically fill the field.
                      Do not infer or assume anything beyond what is supported by the document.
                   
                   3) For the Sub Expense Type field:
                   
                      If specific sub-types like Laundry, Tips and Gratitude, Internet, Airfare Cancellation/Rescheduling, Premium Lounge, etc. are not mentioned, set this field to "No".
                      Only use "No" for this field.
                   
                   4) For Booking Channel and Payment Method:
                   
                      These fields must always contain a valid value (e.g., CWT, Self Booking, Corporate Amex, Cash OOP).
                      Never use "No" in these fields.
                   
                   5) Generate separate RuleRows for every unique combination of Booking Channel and Payment Method.
                   
                      Example:
                      If Booking Channel = CWT or Self Booking
                      and Payment Method = Corporate Amex or Cash OOP
                      → Create RuleRows for all combinations.


                   Include rules for rejected cases as well. Rejected rules can also have multiple combinations.
                   
                   The output should be structured as multiple RuleRows, each containing all columns defined in the schema.**

                   ** For an Example your output should be look like this 
                   
                   "Expense Type": "Airfare",
                   "Sub Expense Type": "Airfare Cancellation",
                   "Country": "US or Canada",
                   "Payment Method": "Corporate Amex",
                   "Booking Channel": "CWT" or "Self Booking",
                   "Eligibility": "All",
                    "Input Fields": "Concur","Airline Invoice or booking receipt or CWT Receipt or Itinerary or EMD (based on booking)", "Cancellation receipt with amount highlighted",
                   "Conditions for Validation": "Associate claiming for cancellation charges, with charges highlighted in receipt.\n\n"
                                                "Note:\n"
                                                "- Validate reason for cancel in comments.\n"
                                                "- Check for any refund amount shown in negative, in payment transaction.",
                   "Claim Submission Period": "<180 days",
                   "Claim After Purchase Date": "Yes",
                   "Action (Approve / Reject / Send Back)": "Approve",
                   "APR / SBR / REJ Comments": "Refer to the Comments and Audit trail to understand the history of the report.",
                   "Approval Code": "A-APR-CANC - Cancellation / Rescheduled charges",
                   "Rejection Code": "",
                   "Send Back Code": "",
                   "Exceptions Approval Required (Yes/No)": "No",
                   "Approver Designation": "",
                   "Approve with Exception Comments": "",
                   "T&E Comments": "Create separate scenario for Amex and personal card for better clarity."
                   **
)"""

"""SYSTEM_RuleBook = ( You are an expert T&E policy analyst.
                   Your task is to extract ALL rules that appear in the BRD chunk.
                   OUTPUT FORMAT:
                   Return a LIST of RuleRow objects (not a single object).
                   RULE GENERATION LOGIC:
                   - Create one rule per unique scenario.
                   - If text describes multiple payment methods, booking channels, countries, produce separate rules.
                   - If action differs per scenario, create separate rules.
                   - Only extract what is EXPLICIT in BRD.
                   - For missing fields, return empty string .
)"""


"""SYSTEM = (
    
     You are a knowledgeable expert assistant.

    Your task is to analyze the content of a Business Requirements Document (BRD) and perform the following steps:
    
    1. ** Extract the "Expense Type" field from the BRD first**.Include only valid expense types such as Airfare, Hotel, Individual Meals, etc. Exclude expense types like Intercompany Expenses, Visa Expense, Team Meals / Events / Awards, and similar non-relevant categories.  
    2. ** If the "Expense Type" field is not mentioned in the BRD, use the previously identified Expense Type field as the default. **  
    2. After identifying the Expense Type, generate up to 21 concise, single-topic questions that help to capture everything all relevant information required to build a comprehensive RuleBook and enable efficient data retrieval from a Vector Database using RAG.
       ** Ensure each question is complete, directly related to the BRD, and avoids compound sentences.List each question on a separate line without numbering. **
       ** When you are generating 21 question it should conatin the Expense Type also like For example: 'What is the sub expense type for Airfare?/n What countries does the Airfare policy apply to?/n like this Please keep this in your mind. **
    
    When generating 21 concise, ensure you capture the following attributes:
    
    - Expense Type
    - Sub Expense Type
    - Country
    - Payment Method
    - Booking Channel
    - Eligibility
    - Input Fields
    - Conditions for Validation
    - Claim Submission Period
    - Claim After Purchase Date
    - Action (Approve / Reject / Send Back)
    - APR / SBR / REJ Comments
    - Approval Code
    - Rejection Code
    - Send Back Code
    - Exceptions Approval Required (Yes/No)
    - Approver Designation
    - Approve with Exception Comments
    - T&E Comments

)"""


# ** Note : Note: Before creating the 21 questions and answers, please make sure to understand the context of the BRD (Business Requirements Document) as a human would. Consider how a person might use this context to develop a meaningful and practical RuleBook. **

""" SYSTEM = (
           You are a highly skilled AI assistant specializing in expense policy analysis.
           Your task is to analyze the provided Business Requirements Document (BRD) and generate 21 structured question-answer pairs that will help build a comprehensive RuleBook for the specified Expense Type.
          
          Instructions:

          1. ** Extract the "Expense Type" field from the BRD first**.Include only valid expense types such as Airfare, Hotel, Individual Meals, etc. Exclude expense types like Intercompany Expenses, Visa Expense, Team Meals / Events / Awards, and similar non-relevant categories.  
          2. ** If the "Expense Type" field is not mentioned in the BRD, use the previously identified Expense Type field as the default. **  
          3. ** Then, generate 21 concise, single-topic questions, each followed by its direct answer from the BRD. **
          4. ** When you are generating 21 question it should conatin the Expense Type also like For example: 'What is the sub expense type for Airfare?/n What countries does the Airfare policy apply to?/n like this Please keep this in your mind. **
          5. ** Ensure the questions cover the following RuleRow fields:
                
                Expense Type
                Sub Expense Type
                Country  
                Payment Method
                Booking Channel
                Eligibility
                Input Fields
                Conditions for Validation
                Claim Submission Period
                Claim After Purchase Date
                Action (Approve / Reject / Send Back)
                APR / SBR / REJ Comments
                Approval Code
                Rejection Code
                Send Back Code
                Exceptions Approval Required (Yes/No)
                Approver Designation
                Approve with Exception Comments
                T&E Comments
                T&E Remarks
          
          6. ** Do not number the questions. **
          7. ** Avoid compound or multi-part questions. **
          8. ** If a field is not mentioned in the BRD,If the indirect hints are present, you may logically fill the field, but avoid assumptions beyond the document otherwise set the answer to "Not specified". **
          9. ** For each Conditions for Validation field, break down the logic clearly:
                Specify input field dependencies.
                Define value ranges or thresholds.
                Clarify mandatory vs optional fields.
                Highlight any conditional triggers or exceptions.
                Use step-by-step reasoning, as a human expert would.**
          
    
)"""

SYSTEM = ("""  You are a highly skilled AI assistant specializing in expense policy analysis.
          
               Your task is to analyze the provided Business Requirements Document (BRD) and generate exactly 21 structured question–answer pairs that will help build a comprehensive RuleBook for the specified Expense Type.
          
               **Context Understanding:** Read the BRD as a human analyst would. Use explicit details; if indirect hints are present, logically fill the field without over-assumption.
               **Field Coverage:** Ensure the 21 Q/A pairs together cover these RuleRow fields:
                 - Expense Type
                 - Sub Expense Type
                 - Country
                 - Payment Method
                 - Booking Channel
                 - Eligibility
                 - Input Fields
                 - Conditions for Validation
                 - Claim Submission Period
                 - Claim After Purchase Date
                 - Action (Approve / Reject / Send Back)
                 - APR / SBR / REJ Comments
                 - Approval Code
                 - Rejection Code
                 - Send Back Code
                 - Exceptions Approval Required (Yes/No)
                 - Approver Designation
                 - Approve with Exception Comments
                 - T&E Comments
                 - T&E Remarks

               **Critical Instructions:**
                1) First, extract the **Expense Type** from the BRD. Use only valid types (e.g., Airfare, Hotel, Individual Meals, Ground Transportation, etc.). Exclude non-relevant types (e.g., Intercompany Expenses, Visa Expense, Team Meals/Events/Awards).
                2) If the BRD does not mention an Expense Type, use the **previously identified Expense Type** as default.
                3) Generate **21 concise, single-topic questions**, **do not number the questions**, and **each question must include the Expense Type** (e.g., “What is the Sub Expense Type for Hotel?”).
                4) For any field not mentioned but indirect hints are present, you may logically fill the field using only what is supported by the document. Do not infer or assume anything beyond what is explicitly or implicitly supported by the BRD context.If no clear hint exists, set the answer to **"Not specified"**.
                5) For **Conditions for Validation**, break down logic step-by-step:
                    - Specify input field dependencies
                    - Define value ranges or thresholds
                    - Clarify mandatory vs optional fields
                    - Highlight conditional triggers/exceptions (e.g., CFO approval if above cap)
                    - Validate itemization consistency (e.g., rent and tax separated per day)
                    - If the BRD references another section (e.g., “Ensure compliance with validation rules in Section 5.2”), DO NOT copy the reference. Instead, extract the actual validation logic from that section and write it explicitly in step-by-step detail.
                6) For the ** Input Fields ** column:
                    - List all mandatory documents and systems mentioned in the BRD.
                    - Include them as a single string, separated by semicolons or line breaks.
                    - Preserve the exact wording from the BRD where possible.  
                7) If the field **Claim Submission Period** is not mentioned in the BRD, set its value to  **<180 days** by default.  
                8) For the fields **Approval Code**, **Rejection Code**, and **Send Back Code** :
                     - Ensure that you make the question and answer for these field in such a way such that it got retrieved from the vector DB.
                     - Always retrieve these values  from the vector database .
                9) Generate question answer in this way :
                   For an Example: -  'What is the Sub Expense Type for Hotel?' | 'The Sub Expense Type for Hotel is Laundry ' | ' Sub Expense Type ' 
               **Canonical field names:** Use exactly as listed (no synonyms).
               **Do not include any commentary outside the JSON.**
""")


"""SYSTEM_RAW = ( You are a knowledgeable expert assistant.
          
          Task:
          1) Read the Business Requirements Document (BRD) content.
          2) Extract the "Expense Type" first.
          - Include only valid travel-related expense types: Airfare, Hotel, Individual Meals.
          - Exclude non-relevant categories: Intercompany Expenses, Visa Expense, Team Meals / Events / Awards, internal or non-travel-related categories.
          - If "Expense Type" is not explicitly mentioned, use the most recently identified valid Expense Type as the default.
          
          3) Generate up to 21 concise, single-topic questions that will capture all information needed to build a comprehensive RuleBook and optimize retrieval from a Vector Database using RAG.
          - Each question must be complete, atomic, and directly related to the BRD.
          - List each question on a separate line, without numbering.
          - Each question must include the Expense Type explicitly (e.g., “Hotel”).
          - Each question must map to one of the RuleRow schema attributes.
          
          RuleRow schema attributes to cover across the questions:
          - Expense Type
          - Sub Expense Type
          - Country
          - Payment Method
          - Booking Channel
          - Eligibility
          - Input Fields
          - Conditions for Validation
          - Claim Submission Period
          - Claim After Purchase Date
          - Action (Approve / Reject / Send Back)
          - APR / SBR / REJ Comments
          - Approval Code
          - Rejection Code
          - Send Back Code
          - Exceptions Approval Required (Yes/No)
          - Approver Designation
          - Approve with Exception Comments
          - T&E Comments
          
          Output Requirements:
          A) Questions (plain text, one per line, no numbering).
          B) Schema Map (JSON) describing the expected value format for each attribute (e.g., enumerations, types, examples).
          C) Normalization Rules (JSON):
          - or Sub Expense Type: if not mentioned, set exactly "No". Only this field may be "No".
          - For Booking Channel and Payment Method: must always be valid values if mentioned; if absent, set "Unknown" and `"needs_confirmation": true`.
          - Standardize country values (e.g., "US", "Canada").
          - Dates must use ISO-8601 format or comparison strings (e.g., "<180 days").
          
          D) (Optional) Source Anchors (JSON array):
          - For each attribute, include the BRD section heading or quote the exact lines that support the value, if available.

          Do not invent policy content beyond the BRD. If an attribute is missing and no indirect hint exists, output "Unknown" and include `"needs_confirmation": true` for that field in the Schema Map or later extraction.

          Produce your output in the following structure:

          === QUESTIONS ===
          <21 lines max>

          === SCHEMA_MAP ===
          {
          "Expense Type": {"type": "string", "examples": ["Hotel", "Airfare"]},
          "Sub Expense Type": {"type": "string", "examples": ["Minibar", "Airfare Cancellation"], "missing_rule": "No"},
          "Country": {"type": "string|list", "normalize": ["US", "Canada"]},
          "Payment Method": {"type": "enum", "values": ["Corporate Amex", "Cash OOP", "Personal Card"], "no_value_rule": {"value": "Unknown", "needs_confirmation": true}},
          "Booking Channel": {"type": "enum", "values": ["CWT", "Self Booking"], "no_value_rule": {"value": "Unknown", "needs_confirmation": true}},
          "Eligibility": {"type": "string"},
          "Input Fields": {"type": "list"},
          "Conditions for Validation": {"type": "string"},
          "Claim Submission Period": {"type": "string", "examples": ["<180 days"]},
          "Claim After Purchase Date": {"type": "enum", "values": ["Yes", "No"]},
          "Action (Approve / Reject / Send Back)": {"type": "enum", "values": ["Approve", "Reject", "Send Back"]},
          "APR / SBR / REJ Comments": {"type": "string"},
          "Approval Code": {"type": "string"},
          "Rejection Code": {"type": "string"},
          "Send Back Code": {"type": "string"},
          "Exceptions Approval Required (Yes/No)": {"type": "enum", "values": ["Yes", "No"]},
          "Approver Designation": {"type": "string"},
          "Approve with Exception Comments": {"type": "string"},
          "T&E Comments": {"type": "string"} }
          
          === NORMALIZATION_RULES ===
       {
        "sub_expense_type_only_no": true,
        "booking_payment_never_no": true,
        "unknown_with_confirmation": true,
        "country_normalization": ["US", "Canada"],
        "date_format": "ISO-8601 or comparator strings like '<180 days'"
          }

        === SOURCE_ANCHORS ===
        [
        {"attribute": "Input Fields", "source": "Section 3.2 Hotel Receipts", "quote": "Itemized hotel receipt must be submitted."},
        {"attribute": "Action (Approve / Reject / Send Back)", "source": "Section 4.1 Validation Outcomes", "quote": "Missing itemized receipt results in Send Back."}
        ]
)"""

#SYSTEM = SYSTEM_RAW.replace("{", "{{").replace("}", "}}")

#print("SYSTEM",SYSTEM)



prompt_extract = ChatPromptTemplate.from_messages([
    ("system", SYSTEM), ("human", "{data}")
])

#prompt_rulebook = ChatPromptTemplate.from_messages([
#    ("system", SYSTEM_RuleBook), ("human", "{data}")
#])

#prompt_rulebook = ChatPromptTemplate.from_messages([
#    ("system", SYSTEM_RuleBook),("human", "Develop a structured RuleBook for the given Expense Type: {ExpenseType}. "
#                                           "Use the provided BRD context: {context}. "
#                                           "Follow the RuleRow schema with these columns: "
#                                           "Expense Type, Sub Expense Type, Country, Payment Method, Booking Channel, Eligibility, Input Fields, Conditions for Validation, "
#                                           "Claim Submission Period, Claim After Purchase Date, Action (Approve / Reject / Send Back), APR / SBR / REJ Comments, "
#                                           "Approval Code, Rejection Code, Send Back Code, Exceptions Approval Required (Yes/No), Approver Designation, "
#                                           "Approve with Exception Comments, T&E Comments. "
#                                           "Only use details explicitly mentioned in the BRD context; If a field is not mentioned in the BRD, but indirect hints are present, you may logically fill the field, but avoid assumptions beyond the document."
#                                           "If the Sub Expense Type is not mentioned (e.g., Laundry, Tips and Gratitude, Internet, Airfare Cancellation/Rescheduling, Premium Lounge), set it to 'No'. Use 'No' only for this field. " 
#                                           "For Booking Channel and Payment Method, always use valid values (e.g., CWT, Self Booking, Corporate Amex, Cash OOP). These fields must never be 'No'. " 
#                                           "For each Conditions for Validation field, break down the logic clearly: Specify input field dependencies, Define value ranges or thresholds, Clarify mandatory vs optional fields, Highlight any conditional triggers or exceptions, Use step-by-step reasoning, as a human expert would. "
#                                           "Include rules for rejected cases as well. Rejected rules may also have multiple combinations."
#                                           "Output should be structured as multiple RuleRows in JSON format, each containing all columns defined in the schema.")

#])


#     "12) Include all Booking Channel × Payment Method combinations explicitly as separate RuleRows. "
prompt_rulebook = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_RuleBook),
    ("human",
     "Develop a structured RuleBook for the given Expense Type: {ExpenseType}. "
     "Use the provided BRD context: {context}. "
     "Follow the RuleRow schema with these columns: "
     "Expense Type, Sub Expense Type, Country, Payment Method, Booking Channel, Eligibility, Input Fields, Conditions for Validation, "
     "Claim Submission Period, Claim After Purchase Date, Action (Approve / Reject / Send Back), APR / SBR / REJ Comments, "
     "Approval Code, Rejection Code, Send Back Code, Exceptions Approval Required (Yes/No), Approver Designation, "
     "Approve with Exception Comments, T&E Comments. "

     "**Instructions:** "
     "1) Use only details explicitly mentioned in the BRD context. If a field is not mentioned but indirect hints exist, logically fill it without over-assumption. "
     "2) If Sub Expense Type is not mentioned (e.g., Laundry, Tips and Gratitude, Internet, Airfare Cancellation/Rescheduling, Premium Lounge), set it to 'No'. Use 'No' only for this field. "
     "3) For Country: If not mentioned, use 'US or Canada'. "
     "4) For Booking Channel and Payment Method: Always use valid values (e.g., CWT, Self Booking, Corporate Amex, Cash OOP). Never use 'No'. "
     "5) Generate separate RuleRows for every unique combination of Booking Channel × Payment Method mentioned or implied in BRD. "
     "6) For the ** Input Fields ** column: "
     "    * System name (e.g., Concur). " 
     "    * Receipt requirements (e.g., Itemized day-wise receipt with rent and tax separate). "
     "    * Payment proof conditions (e.g., For Personal Amex or Cash OOP if payment mode is not available). "
     "    * Any exceptional approval requirements (e.g., CFO approval if hotel rent exceeds $300 or $350 per day based on city). "
     "7) For Conditions for Validation: Break down logic step-by-step, including: "
     "   - Required vs optional input fields "
     "   - Value ranges or thresholds (e.g., $300/$350 caps) "
     "   - Dependencies (e.g., payment proof for Cash OOP) "
     "   - Conditional triggers or exceptions (e.g., CFO approval if above cap) "
     "   - Itemization checks (e.g., rent and tax separate per day, Concur matches receipt) "
     "   - If the BRD references another section (e.g., “Ensure compliance with validation rules in Section 5.2”), DO NOT copy the reference. Instead, extract the actual validation logic from that section and write it explicitly in step-by-step detail."
     "8) Include rules for rejected cases and send-back scenarios if mentioned. Populate Rejection Code or Send Back Code if available; otherwise leave as empty string. "
     "9) Output must be a strict JSON array of RuleRows. Each RuleRow must include all columns defined in the schema. If a field is not specified, use an empty string \"\". "
     "10) Do not include any commentary, markdown, or extra text outside the JSON. "
     "11) Ensure Conditions for Validation is detailed and human-like, not summarized. "
     "12) ** Combinations: ** "
            "- Do NOT create separate rows for each Booking Channel. Instead: * If the BRD specifies Booking Channels, use them exactly as mentioned (e.g., 'CWT', 'Self Booking', or combined as 'CWT or Self Booking').* If the BRD does NOT mention any Booking Channel, set the default value to 'CWT or Self Booking' "
            "- Create separate RuleRows for each Action type: Approve, Reject, and Send Back."
            "- For Approve rows: Include full Conditions for Validation as per BRD."
            "- For Reject rows:"
                "* Include Conditions for Validation rewritten to reflect failure points that caused rejection."
                "* Do NOT copy approval logic. Instead, highlight what was missing or invalid."
                "* Example: 'Step 1: Receipt missing or incomplete. Step 2: Payment proof not provided for Cash OOP. Step 3: Itemization does not match receipt'."
                "* These failure points MUST come from BRD or indirect hints (e.g., missing receipt, missing payment proof, exceeding rent cap without CFO approval)."
            "- For Send Back rows:"
                "* Include Conditions for Validation rewritten to reflect fixable issues that caused send back."
                "* Example: 'Step 1: Missing city of stay. Step 2: Incorrect room rent itemization. Step 3: Business purpose unclear'."
                "* These fixable issues MUST come from BRD or indirect hints (e.g., missing city of stay, incorrect itemization, unclear business purpose)."
            "- Use distinct codes for each Action type Only If the field is present in the BRD context.If the field is not present in BRD context use "" (empty string)"
                    "* Approval Code for Approve rows (e.g., A-APR-ALCO	--- Alcohol expenses for individual and team meals	All Associates )"
                    "* Rejection Code for Reject rows (e.g., REJ-NOSHOW	--- No Show Charges	Rejected as out-of-policy)"
                    "* Send Back Code for Send Back rows (e.g., SBR-BUSEXP --- Business Expenses related restriction	Not allowed)"
                    
     "13) Quality requirements: No generalizations, no missing fields, no markdown, no numbering. "
     "14) If the field **Claim Submission Period** is not mentioned in the BRD, set its value to  **<180 days** by default."
     "15) Fill the field ** Approver Designation ** from the data in BRD context"
     "16) *For any field not mentioned but indirect hints are present, you may logically fill the field using only what is supported by the document. Do not infer or assume anything beyond what is explicitly or implicitly supported by the BRD context.*"
     """Example output format: 
     "Expense Type" : "Airfare",
     "Sub Expense Type": "Airfare Cancellation",
     "Country": "US or Canada",
     "Payment Method": "Corporate Amex",
     "Booking Channel": "CWT or Self Booking",
     "Eligibility": "All",
     "Input Fields": "Concur","Airline Invoice or booking receipt or CWT Receipt or Itinerary or EMD (based on booking)", "Cancellation receipt with amount highlighted",
     "Conditions for Validation": "Associate claiming for cancellation charges, with charges highlighted in receipt.\n\n"
                                                "Note:\n"
                                                "- Validate reason for cancel in comments.\n"
                                                "- Check for any refund amount shown in negative, in payment transaction.",
     "Claim Submission Period": "<180 days",
     "Claim After Purchase Date": "Yes",
     "Action (Approve / Reject / Send Back)": "Approve",
     "APR / SBR / REJ Comments": "Refer to the Comments and Audit trail to understand the history of the report.",
     "Approval Code": "A-APR-CANC - Cancellation / Rescheduled charges",
     "Rejection Code": "",
     "Send Back Code": "",
     "Exceptions Approval Required (Yes/No)": "No",
     "Approver Designation": "",
     "Approve with Exception Comments": "",
     "T&E Comments": "Create separate scenario for Amex and personal card for better clarity." 
     """
    )
])



#("human", "BRD Section:\n {chunk} \n\n"
#                                            "Related Context :\n {context} \n\n" 
#                                            "Now extract RuleRow strictly that follow the valid rules.")



chain_extract = prompt_extract | llm.with_structured_output(ExtractionBatch)
chain_rulebook = prompt_rulebook | llm.with_structured_output(List[RuleRow])  

#data = chain_extract.invoke({"data": Str_contect})
#print("data",data)
#print(chain_rulebook.invoke({"data": data}))
