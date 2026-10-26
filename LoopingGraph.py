from typing import Dict,TypedDict,List
from langgraph.graph import StateGraph,START,END
import random

class AgentState(TypedDict):
    name : str
    counter : int
    Numb : List[int]

def Greet(state : AgentState) -> AgentState:
    """Greets the person"""
    # CHANGED: inner quotes switched to single quotes; reusing double quotes inside an f-string only works on Python 3.12+
    state["name"] = f"Hey {state['name']}"
    state["counter"] = 0
    return state

def Rand(state : AgentState) -> AgentState:
    """Generates Random Number"""
    myList = state["Numb"]
    myList.append(random.randint(1,10))
    state["counter"] += 1
    return state
# CHANGED: return type is str (a routing key), not AgentState
def Looper(state : AgentState) -> str:
    if state["counter"] < 5:
        return "loop"
    else:
        return "end"

graph = StateGraph(AgentState)
graph.add_node("Greet" , Greet)
graph.add_node("Random" , Rand)
# CHANGED: removed the "Looper" lambda node; Looper is a router function, not a node, and the orphan node fails compile
graph.add_edge(START,"Greet")
graph.add_edge("Greet","Random")
graph.add_conditional_edges(
    "Random",
    Looper,
    {
        "loop" : "Random",
        # CHANGED: "END" string -> END constant (the string is treated as an unknown node)
        "end" : END
    }
)

app = graph.compile()
# CHANGED: added "Numb": [] (Rand reads it -> KeyError otherwise); counter set to 0 since Greet resets it anyway
result = app.invoke({"name" : "Saksham", "counter" : 0, "Numb" : []})

print(result["name"], result["Numb"])

from IPython.display import Image, display

png = app.get_graph().draw_mermaid_png()
with open("graphLooping.png", "wb") as f:
    f.write(png)
