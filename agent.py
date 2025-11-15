from langgraph.graph import StateGraph, END, START
from chain_agent import chain_extract, chain_rulebook,read_brd_md,chunk_brd_by_langchain,RuleRow
from langchain_core.messages import BaseMessage,HumanMessage
from typing import List, Optional,TypedDict,Annotated,operator,Dict
from langgraph.graph.message import add_messages
from langchain_text_splitters import RecursiveCharacterTextSplitter 
import itertools
from vector_db import create_vector_store,load_vector_store,retrieve_similar_documents
from chain_agent import RuleRow,chain_rulebook,chain_extract
import os
from pathlib import Path
import pandas as pd
from sentence_transformers import CrossEncoder
import numpy as np
from langgraph.checkpoint.memory import MemorySaver
#from agent_vectordb import State

def func_ranking_rag(query:str,retrieved_documents:List[dict]):
    unique_documents = []
    lst_score = []
    for i in range(len(retrieved_documents)):
        unique_documents.append(retrieved_documents[i]["docs"])
        lst_score.append(retrieved_documents[i]["score"])
    scores_float = np.array([float(s) for s in lst_score])
    top_indices = np.argsort(scores_float)[::-1][:2]
    top_documents = [unique_documents[i] for i in top_indices]
    context = "\n\n".join(top_documents)
    return context
    

def chunk_brd(md_text: str, max_chars: int) -> List[str]:
    splitter = RecursiveCharacterTextSplitter(chunk_size=max_chars, chunk_overlap=200)
    docs = splitter.create_documents([md_text])
    return [d.page_content for d in docs]


def extractor_node(state: State) -> State:
    md_text = state["md_text"]
    state["chunks"] = chunk_brd(md_text, max_chars=2000)
    state["processed_idx"] = 0
    state["all_rules"] = []
    if not os.path.exists("./faiss_db_updated_All"):
        create_vector_store(md_text)
    return state


def rag_node(state: State) -> State:
    idx = state["processed_idx"]
    if idx >= len(state["chunks"]):
        state["current_context"] = ""
        return state
    #print("chunk_str",state["chunks"][idx])
    chunk = chain_extract.invoke({"data" : state["chunks"][idx]}).model_dump(exclude_none=True)
    print("chunck --------------------- ",chunk)
    
    Expensetype = chunk["Expensetype"]
    print("chunk ----------------- -------------- ",chunk)
    row = chunk["rows"]
    retrieved = retrieve_similar_documents(row, k=10)
    #retrieved = retrieve_similar_documents(state["chunks"][idx], k=3)
    #print("retrieved",retrieved)
    #retrieved = [doc.page_content for doc in retrieved]
    retrieved = func_ranking_rag(row,retrieved)
    print("retrieved --------",retrieved)
    print("retrieved ---------- ",len(retrieved))
    state["current_context"] = "\n\n".join(retrieved)+ "\n"  + state["chunks"][idx]
    state["Expensetype"] = Expensetype
    #print("retrived","\n\n".join(retrieved))
    return state
    


def rulebook_node(state: State) -> State:
    idx = state["processed_idx"]
    if idx >= len(state["chunks"]):
        return state

    ExpenseType = state.get("ExpenseType","")
    context = state.get("current_context", "")
    print("token lenght------------------ ",len(context))
    #print("context -------------- context ----",context)
    result: List[RuleRow] = chain_rulebook.invoke({
            "ExpenseType": ExpenseType,
            "context": context
        })
    #print("result -=------- result ",result)
    #print("model ---------- model ",result.model_dump(exclude_none=True))
    print("result ----------------- ------------ ",result)
    #new_rules = result.model_dump(exclude_none=True)
    new_rules = [r for r in result['args']]
    print("new rules -------------- -------------- ",new_rules)
    state["all_rules"].extend(new_rules)
    #print("result",result)
    #for r in result:
    #    state["all_rules"].append(r.model_dump(exclude_none=True))
    print("all_rules -------------- -------------- ",state["all_rules"])
    state["processed_idx"] += 1
    return state



def validator_node(state: State) -> State:
    print("rules",state["all_rules"])
    import re

    def normalize_text(v: str):
        if v is None:
            return None
        if not isinstance(v, str):
            return v
        v = v.strip()
        v = re.sub(r"\s+", " ", v)  
        v = v.replace(" ,", ",")
        v = v.replace(" .", ".")
        return v if v != "" else None

    def normalize_boolean(v):
        if isinstance(v, bool):
            return v
        if isinstance(v, str):
            v = v.strip().lower()
            if v in ["yes", "true", "y"]:
                return True
            if v in ["no", "false", "n"]:
                return False
        return None

    canon = []
    seen = set()

    for r in state["all_rules"]:
        r_norm = {}
        for k, v in r.items():
            if k in ["ClaimafterTravel", "Exceptionsapprovalrequired"]:
                v = normalize_boolean(v)
            else:
                v = normalize_text(v)

            r_norm[k] = v
        dedup_key_fields = [
            "Expensetype", "SubExpenseType", "Country",
            "PaymentMethod", "BookingChannel", "Eligibility",
            "ConditionsforValidations", "Action"
        ]

        key_tuple = tuple((f, r_norm.get(f)) for f in dedup_key_fields)

        if key_tuple not in seen:
            seen.add(key_tuple)
            canon.append(r_norm)
    state["all_rules"] = canon
    return state

def loop_condition_node(state: State):
    if state["processed_idx"] < len(state["chunks"]):
        return "rule_book"
    return END

from langgraph.graph import StateGraph,START,END
#from agent_vectordb_node import extractor_node,rag_node,rulebook_node,validator_node,loop_condition_node
from typing import TypedDict,List,Dict

class State(TypedDict):
    md_text: str
    chunks: List[str]
    processed_idx: int
    current_context: str
    Expensetype: str
    all_rules: List[Dict]   

 

builder = StateGraph(State)
builder.add_node("extractor", extractor_node)
builder.add_node("rag", rag_node)
builder.add_node("rulegen", rulebook_node)
#builder.add_node("validator", validator_node)

builder.set_entry_point("extractor")
builder.add_edge("extractor", "rag")
builder.add_conditional_edges("rag", loop_condition_node, {"rule_book": "rulegen", END: END})
builder.add_edge("rulegen","rag")
#builder.add_edge("validator", END)
#memory = MemorySaver()
graph = builder.compile()
graph.get_graph().print_ascii()


if __name__ == "__main__":
    def read_brd_md(md_path: str) -> str:
        return Path(md_path).read_text(encoding="utf-8")
    
    #md_text = " "
    #for i in range(2,5):
    #    md_text+=read_brd_md(fr"C:\Users\2436230\OneDrive - Cognizant\Desktop\python\brd_main_steps_nested\markdown\mainstep_{i}.md")
    #    md_text+="\n"
    md_text = read_brd_md(fr"C:\Users\2436230\OneDrive - Cognizant\Desktop\python\brd_main_steps_nested\markdown\mainstep_2.md")
    #thread = {"configurable": {"thread_id": "777"}}
    #value = chunk_brd(md_text, max_chars=3500)
    final = graph.invoke({"md_text": md_text},config={"recursion_limit":5000})
    rules = final.get("all_rules", [])
    stats = final.get("stats", {})

    ruleses = []

    for i in rules:
        if i not in ruleses:
            ruleses.append(i)

    print("Length ---- rules",len(rules))
    print("Length ----- ruleses",len(ruleses))
    df = pd.DataFrame(ruleses)
    print(df)
    excel_file = "rulebook_airfare_2_1_1_cond.xlsx"
    df.to_excel(excel_file, index=False)
