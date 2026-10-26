from typing import TypedDict,List
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    message : str
    values : List[int]
    name : str

def Node_Func(state : AgentState) -> AgentState:
    """Node Function that takes in a state and returns a state"""
    currList = state["values"]
    sum = 0
    for i in currList:
        sum += i
    state["values"] = sum
    state["name"] = "Saksham"
    state["message"] = f"Hey {state["name"]}"

    return state

def Node_Func_2(state : AgentState) -> AgentState:
    state["message"] = state["message"] + f" Your sum of vaues is : {state['values']}"
    return state

graph = StateGraph(AgentState)

graph.add_node("Node_1",Node_Func)
graph.add_node("Node_2",Node_Func_2)

graph.set_entry_point("Node_1")
graph.add_edge("Node_1","Node_2") # directed edge from Node_1 -> Node_2
graph.set_finish_point("Node_2")

app = graph.compile()

result = app.invoke({"values" : [1,2,3,4],"name" : "Saksham"})

print(result["message"])

from IPython.display import Image, display

png = app.get_graph().draw_mermaid_png()
with open("graph.png", "wb") as f:
    f.write(png)



