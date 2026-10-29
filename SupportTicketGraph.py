import operator
import random
from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, START, END

# Practice: Support-ticket router
#
#   START -> classify --(category)--> billing | technical | general | escalate
#   billing   --(amount <= 100)--> auto_refund -> respond
#             --(amount  > 100)--> escalate
#   technical -> attempt_fix --(fixed)--------> respond
#                            --(attempts < 3)-> attempt_fix   (LOOP)
#                            --(else)---------> escalate
#   general   -> respond
#   escalate  -> respond
#   respond   -> END


class TicketState(TypedDict):
    text: str
    amount: float
    category: str
    attempts: int
    fixed: bool
    response: str
    # Annotated + operator.add => each node's returned list is APPENDED, not overwritten
    log: Annotated[list[str], operator.add]


# ---------- nodes ----------
def classify(state: TicketState) -> dict:
    text = state["text"].lower()
    if any(w in text for w in ("refund", "charge", "invoice")):
        category = "billing"
    elif any(w in text for w in ("error", "crash", "bug", "login")):
        category = "technical"
    elif any(w in text for w in ("hello", "hours", "info")):
        category = "general"
    else:
        category = "unknown"
    return {"category": category, "attempts": 0, "fixed": False,
            "log": [f"classified as '{category}'"]}


def auto_refund(state: TicketState) -> dict:
    return {"response": f"Refund of ${state['amount']:.2f} issued automatically.",
            "log": ["auto refund issued"]}


def attempt_fix(state: TicketState) -> dict:
    attempt = state["attempts"] + 1
    fixed = random.random() < 0.4  # simulate a flaky fix
    return {"attempts": attempt, "fixed": fixed,
            "log": [f"fix attempt {attempt}: {'success' if fixed else 'failed'}"]}


def general_answer(state: TicketState) -> dict:
    return {"response": "We are open 9-5, Mon-Fri.", "log": ["general answer"]}


def escalate(state: TicketState) -> dict:
    return {"response": "Escalated to a human agent.", "log": ["escalated"]}


def respond(state: TicketState) -> dict:
    # technical tickets that were fixed have no response yet
    response = state.get("response") or "Issue fixed. Please try again."
    return {"response": response, "log": ["response sent"]}


# ---------- routers (return the name of the next edge/node, they do NOT change state) ----------
def route_category(state: TicketState) -> str:
    return state["category"]


def route_billing(state: TicketState) -> str:
    return "auto_refund" if state["amount"] <= 100 else "escalate"


def route_after_fix(state: TicketState) -> str:
    if state["fixed"]:
        return "done"
    if state["attempts"] < 3:
        return "retry"
    return "give_up"


# ---------- graph ----------
graph = StateGraph(TicketState)
graph.add_node("classify", classify)
graph.add_node("billing_check", lambda state: {})  # pass-through, only a decision point
graph.add_node("auto_refund", auto_refund)
graph.add_node("attempt_fix", attempt_fix)
graph.add_node("general_answer", general_answer)
graph.add_node("escalate", escalate)
graph.add_node("respond", respond)

graph.add_edge(START, "classify")

graph.add_conditional_edges("classify", route_category, {
    "billing": "billing_check",
    "technical": "attempt_fix",
    "general": "general_answer",
    "unknown": "escalate",
})

graph.add_conditional_edges("billing_check", route_billing, {
    "auto_refund": "auto_refund",
    "escalate": "escalate",
})

graph.add_conditional_edges("attempt_fix", route_after_fix, {
    "done": "respond",
    "retry": "attempt_fix",   # loop back to itself
    "give_up": "escalate",
})

for node in ("auto_refund", "general_answer", "escalate"):
    graph.add_edge(node, "respond")
graph.add_edge("respond", END)

app = graph.compile()


def run(text: str, amount: float = 0.0):
    result = app.invoke({"text": text, "amount": amount, "log": []})
    print(f"\nTicket: {text!r} (amount={amount})")
    print("  path    :", " -> ".join(result["log"]))
    print("  response:", result["response"])


if __name__ == "__main__":
    run("I need a refund for a wrong charge", amount=40)    # billing, auto
    run("I need a refund for a wrong charge", amount=500)   # billing, escalate
    run("App crash on login")                               # technical, retry loop
    run("What are your opening hours?")                     # general
    run("My cat is purple")                                 # unknown -> escalate
