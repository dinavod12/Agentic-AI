from langgraph.graph import StateGraph, END
from chain_agent import (
    chainextract, chainrulebook, readbrdmd, chunkbrdbylangchain
)
from typing import List, Dict
import itertools

class State(Dict):
    extracteddata: List[dict]
    rulebookdata: List[dict]
    expected_combinations: int

def extractornode(state: State) -> State:
    print("Extracting data from BRD...")
    state["extracteddata"] = [chainextract.invoke(chunk.page_content) for chunk in state["extracteddata"]]
    return state

def rulebooknode(state: State) -> State:
    print("Generating rulebook from extracted data...")
    payment_methods, booking_channels, expense_types, sub_expense_types, countries = set(), set(), set(), set(), set()
    for chunk in state["extracteddata"]:
        payment_methods.update(chunk.get("PaymentMethods", []))
        booking_channels.update(chunk.get("BookingChannels", []))
        expense_types.update(chunk.get("ExpenseTypes", []))
        sub_expense_types.update(chunk.get("SubExpenseTypes", []))
        countries.update(chunk.get("Countries", []))
    combinations = list(itertools.product(
        payment_methods or [None], booking_channels or [None],
        expense_types or [None], sub_expense_types or [None], countries or [None]
    ))
    seen = set()
    rules = []
    for combo in combinations:
        key = tuple(combo)
        if key in seen:
            continue
        rule_data = dict(
            PaymentMethod=combo[0], BookingChannel=combo[1],
            ExpenseType=combo[2], SubExpenseType=combo[3], Country=combo[4]
        )
        rule = chainrulebook.invoke(rule_data)
        rules.append(rule)
        seen.add(key)
    state["rulebookdata"] = rules
    return state

def conditionnode(state: State):
    if len(state["rulebookdata"]) >= state.get("expected_combinations", 0):
        return END
    return "rulebook"

def main():
    mdtext = readbrdmd("your_BRD_document.md")  # Replace with the actual file
    chunks = chunkbrdbylangchain(mdtext, maxchars=5000)
    all_payment_methods, all_booking_channels, all_expense_types, all_sub_expense_types, all_countries = set(), set(), set(), set(), set()
    extracted_chunks = []
    for chunk in chunks:
        data = chainextract.invoke(chunk.page_content)
        all_payment_methods.update(data.get("PaymentMethods", []))
        all_booking_channels.update(data.get("BookingChannels", []))
        all_expense_types.update(data.get("ExpenseTypes", []))
        all_sub_expense_types.update(data.get("SubExpenseTypes", []))
        all_countries.update(data.get("Countries", []))
        extracted_chunks.append(data)
    expected_combinations = len(list(itertools.product(
        all_payment_methods or [None],
        all_booking_channels or [None],
        all_expense_types or [None],
        all_sub_expense_types or [None],
        all_countries or [None]
    )))
    initial_state = {
        "extracteddata": extracted_chunks,
        "rulebookdata": [],
        "expected_combinations": expected_combinations
    }
    builder = StateGraph(State)
    builder.add_node("extractor", extractornode)
    builder.add_node("rulebook", rulebooknode)
    builder.set_entry_point("extractor")
    builder.add_edge("rulebook", "extractor")
    builder.add_edge("rulebook", END)
    builder.add_conditional_edges("extractor", conditionnode, {"rulebook": "rulebook", "END": END})
    graph = builder.compile()
    final_answer = graph.invoke(initial_state)
    for idx, rule in enumerate(final_answer["rulebookdata"]):
        print(f"Rule {idx+1}:", rule)
        print("----------------")

if __name__ == "__main__":
    main()
