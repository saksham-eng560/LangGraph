from typing import TypedDict
from langgraph.graph import StateGraph,START,END

class AgentState(TypedDict):
    value1 : int
    value2 : int
    operation : str
    ans : str

def add_Node(state : AgentState) -> AgentState:
    """Node Function that takes in a state and returns a state"""
    state["ans"] = f"Addition of {state['value1']} and {state['value2']} is : {state['value1'] + state['value2']}"

    return state

def sub_Node(state : AgentState) -> AgentState:
    """Node Function that takes in a state and returns a state"""
    state["ans"] = f"Subtraction of {state['value1']} and {state['value2']} is : {state['value1'] - state['value2']}"

    return state

#conditonal Node Function that takes in a state and returns a state
def conditional_Node(state : AgentState) -> AgentState:
    """Conditional Node Function"""
    if state["operation"] == "add":
        return "AdditionEdge"
    else:
        return "SubtractionEdge"
#we will use lambda to tell the graph to go to the next node and this just doesnt return the state but also tells the graph to go to the next node

graph = StateGraph(AgentState)
graph.add_node("Conditional_Node",lambda state:state)
graph.add_node("Add_Node",add_Node)
graph.add_node("Sub_Node",sub_Node)
graph.add_edge(START,"Conditional_Node")
graph.add_edge("Add_Node",END)
graph.add_edge("Sub_Node",END)

graph.add_conditional_edges(
    "Conditional_Node",
    conditional_Node,
    { #Edge : Node
        "AdditionEdge" : "Add_Node",
        "SubtractionEdge" : "Sub_Node"
    }
)

app = graph.compile()

result = app.invoke({"value1" : 5, "value2" : 6, "operation" : "add"})
print(result["ans"])

from IPython.display import Image, display

png = app.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(png)
