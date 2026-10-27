from typing import TypedDict,List,Union
from langgraph.graph import StateGraph,START,END
from langchain_core.messages import HumanMessage,AIMessage
from langchain_ollama import ChatOllama

class AgentState(TypedDict):
    messages : List[Union[HumanMessage,AIMessage]]

llm = ChatOllama(model="qwen3.5:4b")


def process(state: AgentState) -> AgentState:
    response = llm.invoke(state["messages"])
    print(f"\nAI: {response.content}")
    state["messages"].append(response)
    return state


graph = StateGraph(AgentState)
graph.add_node("process", process)
graph.add_edge(START, "process")
graph.add_edge("process", END)
agent = graph.compile()

convo_history = []
user_input = input("Enter: ")

while user_input != "exit":
    convo_history.append(HumanMessage(content=user_input))
    convo_history = agent.invoke({"messages" : convo_history})["messages"]
    user_input = input("Enter: ")



