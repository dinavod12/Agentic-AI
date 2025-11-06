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

