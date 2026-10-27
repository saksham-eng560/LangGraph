from typing import TypedDict
from langgraph.graph import StateGraph,START,END

class AgentState(TypedDict):
    num1 : int
    num2 : int
    num3 : int
    num4 : int
    operation1 : str
    operation2 : str
    final : str

def Add_Node1(state : AgentState) -> AgentState:
    """Adds the num1 and num2"""
    state["final"] = state["final"] + f" This is you answer {state["num1"] + state["num2"]}"
    return state

def Add_Node2(state : AgentState) -> AgentState:
    """Adds the num3 and num4"""
    state["final"] = state["final"] + f" This is you answer {state["num3"] + state["num4"]}"
    return state

def Sub_Node1(state : AgentState) -> AgentState:
    """Subtracts the num1 and num2"""
    state["final"] = state["final"] + f" This is you answer {state["num1"] - state["num2"]}"
    return state

def Sub_Node2(state : AgentState) -> AgentState:
    """Subtracts the num3 and num4"""
    state["final"] = state["final"] + f" This is you answer {state["num3"] - state["num4"]}"
    return state

def conditional_Func1(state : AgentState) -> AgentState:
    if state["operation1"] == "+":
        return "Addition1Edge"
    else:
        return "Subtraction1Edge"

def conditional_Func2(state : AgentState) -> AgentState:
    if state["operation2"] == "+":
        return "Addition2Edge"
    else:
        return "Subtraction2Edge"

graph = StateGraph(AgentState)
graph.add_node("Addition1",Add_Node1)
graph.add_node("Addition2",Add_Node2)
graph.add_node("Subtraction1",Sub_Node1)
graph.add_node("Subtraction2",Sub_Node2)
graph.add_node("router1",lambda state:state)
graph.add_node("router2",lambda state:state)

graph.add_edge(START,"router1")
graph.add_edge("Addition1","router2")
graph.add_edge("Subtraction1","router2")
graph.add_edge("Addition2",END)
graph.add_edge("Subtraction2",END)

graph.add_conditional_edges(
    "router1",
    conditional_Func1,
    {
        "Addition1Edge" : "Addition1",
        "Subtraction1Edge" : "Subtraction1"
    }
)
graph.add_conditional_edges(
    "router2",
    conditional_Func2,
    {
        "Addition2Edge" : "Addition2",
        "Subtraction2Edge" : "Subtraction2"
    }
)

app = graph.compile()

result = app.invoke({"num1" : 2,"num2" : 5,"num3" : 6,"num4" : 1,"operation1" : "+","operation2" : "-","final" : ""})
print(result["final"])
