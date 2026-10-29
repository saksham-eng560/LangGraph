from langgraph.graph import StateGraph, START, END
from typing import List,TypedDict

class AgentState(TypedDict):
    name : str
    values : List[int]
    sum : int

def Greeter(state : AgentState) -> AgentState:
    state["name"] = "Hey " + state["name"]
    return state

def ValueOp(state : AgentState) -> AgentState:
    ans = 0
    for i in state["values"]:
        ans += i
    state["sum"] = ans
    return state

graph = StateGraph(AgentState)
graph.add_node("Node_1",Greeter)
graph.add_node("Node_2",ValueOp)
graph.add_edge(START,"Node_1")
graph.add_edge("Node_1","Node_2")
graph.add_edge("Node_2",END)

app = graph.compile()

result = app.invoke({"name" : "Saksham","values" : [9,1,5,3,5,6,2]})
print(result)
