from typing import Dict,TypedDict
from langgraph.graph import StateGraph

class State_Of_Graph(TypedDict):
    message : str 
    name : str              #STATE

def Node_Of_Graph(state : State_Of_Graph) -> State_Of_Graph:
    """First Node of the Graph , adds Greeting"""    #reqiured or LLM to understand the notion or use of the Node
    state["message"] = "Heyyyyyy" + " Howw are you doinggg"  
    state["name"] = " Sakshammm"             #NODE
    return state

graph = StateGraph(State_Of_Graph)      #GRAPH FORMATION

graph.add_node("Node_1",Node_Of_Graph) #Node_1 is the name and the Node_Of_Graph defines the functionality fo this node

#now we neeed virtaulstart and end to make the program know that it is a graph and it has a start and end point

graph.set_entry_point("Node_1")  #setting the entry point of the graph
graph.set_finish_point("Node_1")   #setting the exit point of the graph

app = graph.compile()

result = app.invoke({"message": "Hello","name" : "Saksham"}) #invoke with normal state

print(result['message'] + result['name']) # print by concatenating
