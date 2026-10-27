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
    state["message"] = f"Hey {state["name"]} this is sum of your values : {state['values']}"

    return state

graph = StateGraph(AgentState)

graph.add_node("Node",Node_Func)
graph.set_entry_point("Node")
graph.set_finish_point("Node")

app = graph.compile()

result = app.invoke({"message" : "Test1", "values" : [1,2,3,4],"name" : "Saksham"})

print(result)


