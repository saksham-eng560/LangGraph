"""
CONDITIONAL GRAPH II - Support Ticket Router (practice)

QUESTION
    Build a graph that triages a support ticket:
      1. Classify the ticket as billing / technical / general / unknown
         (keywords: billing -> refund, charge, invoice | technical -> error, crash,
          bug, login | general -> hello, hours, info | anything else -> unknown).
      2. billing   -> refund automatically if amount <= 100, otherwise escalate.
      3. technical -> try to fix it (simulate with random.random() < 0.4);
                      retry up to 3 times, then escalate.
      4. general   -> send a canned answer.
      5. unknown   -> escalate.
      6. Every path ends by sending a response, then END.

STATE
    text      : str          ticket text
    amount    : float        money involved (0 if none)
    category  : str          set by classify
    attempts  : int          fix attempts so far
    fixed     : bool         did the last fix work?
    response  : str          final message to the customer
    log       : list[str]    every node appends one line describing what it did
                             (hint: Annotated[list[str], operator.add])

FLOW
    START -> classify -+- billing   -> billing_check -+- amount <= 100 -> auto_refund --+
                       |                              +- amount  > 100 -> escalate -----+
                       +- technical -> attempt_fix -+- fixed         -> respond         |
                       |                 ^  retry  -+  attempts < 3                     |
                       |                 +--------- else -> escalate -------------------+
                       +- general   -> general_answer ---------------------------------+
                       +- unknown   -> escalate ---------------------------------------+-> respond -> END

TEST TICKETS (expected result in brackets)
    "I need a refund for a wrong charge", amount=40    [auto refund]
    "I need a refund for a wrong charge", amount=500   [escalated]
    "App crash on login"                               [retry loop, fixed or escalated]
    "What are your opening hours?"                     [canned answer]
    "My cat is purple"                                 [escalated]

BONUS
    1. Add a `priority` field and send "high" priority tickets straight to escalate.
    2. Add a "needs_approval" branch for amounts between 100 and 250.
    3. Replace classify with an LLM call.
    4. Draw the graph to a PNG with app.get_graph().draw_mermaid_png().
"""

from typing import Sequence, Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_ollama import ChatOllama
import random

# write your solution below

class AgentState(TypedDict):
    text      : str
    amount    : float        
    category  : str         
    attempts  : int        
    fixed     : bool       
    response  : str         


def Classifier(state : AgentState) -> AgentState: #lambda
    """This is a ticket classifier function"""
    # FIX: strip punctuation + lowercase so "hours?" / "Crash" match their keywords
    parsedList = [w.strip("?.,!").lower() for w in state["text"].split()]
    # FIX: no state["category"] writes here - a routing function's state changes are discarded
    for words in parsedList:
        if words in ("refund", "charge", "invoice"):
            return "billing"
        elif words in ("error", "crash", "bug", "login"):
            return "technical"
        elif words in ("hello", "hours", "info"):
            return "general"
    # FIX: "unknown" was returned inside the loop (on the first non-matching word);
    # now it is returned only after every word has been checked
    return "unknown"

def billing_ticket(state : AgentState) -> AgentState: #lambda
    """Checks the Amount"""
    if state["amount"] <= 100:
        return "amount<=100"
    else:
        return "amount>100"

def auto_refund(state : AgentState) -> AgentState:
        """Initiates the Refund"""
        state["fixed"] = True
        state["response"] = "Refunded Your Amount Thank for Visiting"
        return state

def escalate(state : AgentState) -> AgentState:
    """Escalates the Issue"""
    state["response"] = "We Need to escalate we will look further"
    return state

def general_answer(state : AgentState) -> AgentState:
    """Gives the general Answer"""
    state["response"] = "This is a general ticket, Tysm"
    return state

def attempt_fix(state : AgentState) -> AgentState:
    """Attempts the fix"""
    # FIX: random(0,1) -> random.random(); always count the attempt,
    # and a roll < 0.4 means the fix succeeded (was always False before)
    state["attempts"] += 1
    state["fixed"] = random.random() < 0.4
    return state

def tech_router(state : AgentState) -> AgentState:
    """Routes the technical ticket accordingly"""
    if state["fixed"] is True:
        return "fixed"
    elif state["fixed"] is False and state["attempts"] >= 3:
        return "attempts>=3"
    elif state["fixed"] is False and state["attempts"] < 3:
        return "retry"

def Respond(state : AgentState) -> AgentState:
    return state

graph = StateGraph(AgentState)

graph.add_node("classify",lambda state : state)
graph.add_node("billing_check",lambda state : state)
graph.add_node("auto_refund",auto_refund)
graph.add_node("escalate",escalate)
graph.add_node("respond",Respond)
graph.add_node("general_answer",general_answer)
graph.add_node("attemp_fix",attempt_fix)
graph.add_node("fixed_or_attempt_router",lambda state : state)

graph.add_edge("attemp_fix","fixed_or_attempt_router")

#conditional classifier
graph.add_conditional_edges(
    "classify",
    Classifier,
    {
        "billing" : "billing_check",
        "technical" : "attemp_fix",
        "general" : "general_answer",
        "unknown" : "escalate"
    }
)
#billing_check
graph.add_conditional_edges(
    "billing_check",
    billing_ticket,
    {
        "amount<=100" : "auto_refund",
        "amount>100" : "escalate"
    }
)
#tech looper + conditional
graph.add_conditional_edges(
    "fixed_or_attempt_router",
    tech_router,
    {
        "fixed" : "respond",
        "attempts>=3" : "escalate",
        "retry" : "attemp_fix"
    }
)

graph.add_edge("auto_refund","respond")
graph.add_edge("escalate","respond")
graph.add_edge("general_answer","respond")
graph.add_edge(START,"classify")
graph.add_edge("respond",END)

app = graph.compile()

#     text      : str
#     amount    : float        
#     category  : str          
#     attempts  : int          
#     fixed     : bool         
#     response  : str 

# FIX: nodes read amount/attempts/fixed directly, so every key must be supplied up front
tickets = [
    {"text": "I need a refund for a wrong charge", "amount": 40},
    {"text": "I need a refund for a wrong charge", "amount": 500},
    {"text": "App crash on login", "amount": 0},
    {"text": "What are your opening hours?", "amount": 0},
    {"text": "My cat is purple", "amount": 0},
]
for t in tickets:
    result = app.invoke({**t, "attempts": 0, "fixed": False, "category": "", "response": ""})
    print(result["response"])