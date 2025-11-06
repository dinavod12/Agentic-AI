from langgraph.graph import StateGraph, END, START
from chain_agent import chain_extract, chain_rulebook,read_brd_md,chunk_brd_by_langchain,RuleRow
from langchain_core.messages import BaseMessage,HumanMessage
from typing import List, Optional,TypedDict,Annotated,operator
from langgraph.graph.message import add_messages
import itertools



md_text = read_brd_md(r"C:\Users\2436230\OneDrive - Cognizant\Desktop\python\brd_main_steps_nested\markdown\mainstep_2.md")
chunks = chunk_brd_by_langchain(md_text, max_chars=5000)


extracted_chunks = []
for chunk in chunks:
    data = chain_extract.invoke({"data": chunk.page_content})
    extracted_chunks.append(data)

            



"""Str_contect = ""
import time
for i in chunk_brd_by_langchain(md_text, max_chars=5000):
    Str_contect += i.page_content + "\n" """


Last = -1


class State(TypedDict):
    extracted_data: List[str]
    rulebook_data: Annotated[List[dict],operator.add] 

def extractor_node(state:State) -> State:
    print("Extracting data from BRD...")
    state["extracted_data"]  = [data for data in extracted_chunks]
    return state

def rulebook_node(state:State) -> State:
    print("Generating rulebook from extracted data...")
    return {"rulebook_data":[chain_rulebook.invoke({"data": state["extracted_data"]})]}


def condition_node(state:State) -> State:
    if len(state["rulebook_data"]) > 10:
        return END
    else:
        return "rulebook"

builder = StateGraph(State)

builder.add_node("extractor", extractor_node)       
builder.add_node("rulebook", rulebook_node)
builder.set_entry_point("extractor") 
builder.add_edge( "rulebook","extractor")     
#builder.add_edge("rulebook", END)
builder.add_conditional_edges("extractor", condition_node,{"rulebook": "rulebook", END: END})

graph = builder.compile()
graph.get_graph().print_ascii()

if __name__ == "__main__":
    final_answer = graph.invoke({"extracted_data": [extracted_chunks]})
    for i in final_answer["rulebook_data"]:
        print("Rules", i)
        print("\n")
        print("----------------")




# brd_to_rulebook_graph.py
from __future__ import annotations
import json, os, re
from typing import List, Dict, Optional, TypedDict

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from llm_model import llm
from vector_engine import build_vector_db, retrieve_similar_sections

# =========================
# Models
# =========================
class RuleRow(BaseModel):
    Expensetype: Optional[str] = None
    SubExpenseType: Optional[str] = None
    Country: Optional[str] = None
    PaymentMethod: Optional[str] = None
    BookingChannel: Optional[str] = None
    Eligibility: Optional[str] = None
    Input: Optional[str] = None
    ConditionsforValidations: Optional[str] = None
    Claimsubmissionperiod: Optional[str] = None
    ClaimafterTravel: Optional[bool] = None
    Action: Optional[str] = None
    APRorSBRorREJComments: Optional[str] = None
    Approvalcode: Optional[str] = None
    Rejectioncode: Optional[str] = None
    Sendbackcode: Optional[str] = None
    Exceptionsapprovalrequired: Optional[bool] = None
    Approverdesignation: Optional[str] = None
    ApprovewithException: Optional[str] = None
    Comments: Optional[str] = None
    TEcomments: Optional[str] = None
    TERemarks: Optional[str] = None

class State(TypedDict, total=False):
    md_text: str
    chunks: List[str]
    processed_idx: int
    current_context: str
    all_rules: List[Dict]         # list[RuleRow as dict]
    stats: Dict[str, int]

# =========================
# Chunking
# =========================
def chunk_brd(md_text: str, max_chars: int = 2500) -> List[str]:
    """
    Conservative chunking to keep semantic coherence.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=max_chars, chunk_overlap=200)
    docs = splitter.create_documents([md_text])
    return [d.page_content for d in docs]

# =========================
# Prompts / Chains
# =========================
SYSTEM_MULTI_RULES = """
You are an expert policy extraction agent. Your job is to extract **ALL** distinct business rules
from the given BRD section + related context. Do NOT miss any rule. If a field is not given,
leave it blank (null/empty). If there are many combinations (e.g., PaymentMethod x Country),
expand them into multiple rules, one per combination, when explicitly stated or implied.

Return a **JSON array** only. Each element must be an object matching this schema exactly:
{
 "Expensetype": "",
 "SubExpenseType": "",
 "Country": "",
 "PaymentMethod": "",
 "BookingChannel": "",
 "Eligibility": "",
 "Input": "",
 "ConditionsforValidations": "",
 "Claimsubmissionperiod": "",
 "ClaimafterTravel": null,
 "Action": "",
 "APRorSBRorREJComments": "",
 "Approvalcode": "",
 "Rejectioncode": "",
 "Sendbackcode": "",
 "Exceptionsapprovalrequired": null,
 "Approverdesignation": "",
 "ApprovewithException": "",
 "Comments": "",
 "TEcomments": "",
 "TERemarks": ""
}

If no rule exists, return [].
Ensure the output is STRICT JSON: no comments, no trailing commas, no prose before/after.
"""

prompt_multi = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_MULTI_RULES),
    ("human",
     "MAIN BRD SECTION:\n{chunk}\n\n"
     "RETRIEVED RELATED CONTEXT (RAG):\n{context}\n\n"
     "Now extract ALL rules as a JSON array (strict JSON).")
])

chain_extract_rules = prompt_multi | llm

# =========================
# Graph Nodes
# =========================
def extractor_node(state: State) -> State:
    md_text = state["md_text"]
    state["chunks"] = chunk_brd(md_text, max_chars=2500)
    state["processed_idx"] = 0
    state["all_rules"] = []
    state["stats"] = {"chunks": len(state["chunks"]), "fail_json": 0, "empty_chunks": 0}
    print(f"📄 Split BRD into {len(state['chunks'])} chunks.")
    # Build VectorDB once (idempotent)
    if not os.path.exists("./brd_vector_db"):
        print("📚 Building VectorDB (RAG) from full BRD ...")
        build_vector_db(md_text)
    return state

def rag_node(state: State) -> State:
    idx = state["processed_idx"]
    if idx >= len(state["chunks"]):
        state["current_context"] = ""
        return state
    chunk = state["chunks"][idx]
    # Retrieve top-4 similar sections across entire BRD
    retrieved = retrieve_similar_sections(chunk, k=4)
    state["current_context"] = "\n\n".join(retrieved)
    print(f"🔍 RAG retrieved {len(retrieved)} related sections for chunk {idx+1}.")
    return state

def rulegen_node(state: State) -> State:
    idx = state["processed_idx"]
    if idx >= len(state["chunks"]):
        return state

    chunk = state["chunks"][idx]
    context = state.get("current_context", "")

    print(f"🧠 Generating rules for chunk {idx+1}/{len(state['chunks'])} ...")
    try:
        resp = chain_extract_rules.invoke({"chunk": chunk, "context": context})
        raw = (resp.content or "").strip()
        # JSON hygiene
        raw = re.sub(r",\s*}", "}", raw)
        raw = re.sub(r",\s*]", "]", raw)
        # Some models wrap code fences: ```json ... ```
        raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)

        data = json.loads(raw)
        if not isinstance(data, list):
            data = [data]
    except Exception as e:
        print(f"⚠️ JSON parse failed for chunk {idx+1}: {e}")
        state["stats"]["fail_json"] += 1
        data = []

    # Validate against schema; drop malformed
    valid = []
    for d in data:
        try:
            r = RuleRow(**d).model_dump(exclude_none=True)
            if any(v not in (None, "", []) for v in r.values()):
                valid.append(r)
        except Exception:
            # skip malformed row
            pass

    if not valid:
        state["stats"]["empty_chunks"] += 1

    print(f"✅ Chunk {idx+1}: {len(valid)} valid rules.")
    state["all_rules"].extend(valid)
    state["processed_idx"] += 1
    return state

def validator_node(state: State) -> State:
    """
    Deduplicate and standardize. You can enhance this with canonicalization
    (uppercasing country, trimming spaces, normalizing booleans, etc.)
    """
    canon = []
    seen = set()

    def norm_val(v):
        if isinstance(v, str):
            return re.sub(r"\s+", " ", v.strip())
        return v

    for r in state["all_rules"]:
        # Canonicalize values
        r_norm = {k: norm_val(v) for k, v in r.items()}
        # Build a stable dedup key across the most discriminative fields + all content
        key = tuple(sorted(r_norm.items()))
        if key not in seen:
            seen.add(key)
            canon.append(r_norm)

    print(f"🧩 After validation/dedup: {len(canon)} unique rules (from {len(state['all_rules'])}).")
    state["all_rules"] = canon
    return state

def loop_condition(state: State):
    """
    Continue until all chunks are processed; then go to validator.
    """
    if state["processed_idx"] < len(state["chunks"]):
        return "rag"
    return "validator"

# =========================
# Build Graph
# =========================
builder = StateGraph(State)
builder.add_node("extractor", extractor_node)
builder.add_node("rag", rag_node)
builder.add_node("rulegen", rulegen_node)
builder.add_node("validator", validator_node)

builder.set_entry_point("extractor")
builder.add_edge("extractor", "rag")
builder.add_edge("rag", "rulegen")
builder.add_conditional_edges("rulegen", loop_condition, {"rag": "rag", "validator": "validator"})
builder.add_edge("validator", END)

graph = builder.compile()

# =========================
# CLI run
# =========================
if __name__ == "__main__":
    # Replace with your BRD path
    BRD_PATH = os.getenv("BRD_MD_PATH", r"C:\path\to\your\brd.md")
    with open(BRD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    final = graph.invoke({"md_text": md_text})
    rules = final.get("all_rules", [])
    stats = final.get("stats", {})

    print("\n============================")
    print(f"📘 FINAL RULEBOOK: {len(rules)} rules total")
    print(f"📊 Stats: {stats}")
    print("============================\n")

    # Preview first 10 rules
    for i, r in enumerate(rules[:10], 1):
        print(f"Rule #{i}")
        for k, v in r.items():
            print(f"  {k}: {v}")
        print("----")

    # Optional: write to JSON file
    out_path = os.getenv("RULEBOOK_OUT", "./rulebook.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(rules, f, ensure_ascii=False, indent=2)
    print(f"💾 Saved rulebook to {out_path}")



def rulegen_node(state: State) -> State:
    idx = state["processed_idx"]
    if idx >= len(state["chunks"]):
        return state

    chunk = state["chunks"][idx]
    context = state.get("current_context", "")

    print(f"🧠 Generating rules for chunk {idx+1}/{len(state['chunks'])} ...")

    # Direct Pydantic output (no parsing required)
    try:
        result: RuleBookOutput = chain_extract_rules.invoke({
            "chunk": chunk,
            "context": context
        })

        new_rules = [r.model_dump(exclude_none=True) for r in result.rules]
        print(f"✅ Chunk {idx+1}: {len(new_rules)} rules extracted.")
    except Exception as e:
        print(f"⚠️ LLM structured output failed at chunk {idx+1}: {e}")
        state["stats"]["fail_json"] += 1
        new_rules = []

    state["all_rules"].extend(new_rules)
    state["processed_idx"] += 1
    return state



