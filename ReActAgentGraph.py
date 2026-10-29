from typing import Sequence, Annotated, TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import BaseMessage, SystemMessage
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages




class AgentState(TypedDict):
    messages : Annotated[Sequence[BaseMessage], add_messages]

@tool
def add_Numbers(a: int, b: int) -> int:
    """Tool Function that takes in two numbers and returns their sum"""
    return a + b

ToolList = [add_Numbers]
llm = ChatOllama(model="qwen3.5:4b").bind_tools(tools=ToolList)

def Agent(state : AgentState) -> AgentState:
    """Agent Function that takes in a state and returns a state"""
    system_call = SystemMessage(content="You are my AI , please help me")
    response = llm.invoke([system_call, state["messages"]])
    return {"messages": [response]}

def continuer(state : AgentState) -> AgentState:
    """Continuer Function"""
    last_message = state["messages"][-1]
    if not last_message.tool_calls:
        return "end"
    else:
        return "tool"


graph = StateGraph(AgentState)
graph.add_node("Model",Agent)

tool_Node = ToolNode(tools=ToolList)
graph.add_node("ToolNode",tool_Node)
graph.add_edge(START,"Model")
graph.add_edge("ToolNode","Model")

graph.add_conditional_edges(
    "Model",
    continuer,
    {
        "tool" : "ToolNode",
        "end" : END
    }
)

app = graph.compile()

def print_stream(stream):
    for s in stream:
        message = s["messages"][-1]
        if isinstance(message, tuple):
            print(message)
        else:
            message.pretty_print()

inputs = {"messages": [("user", "Add 40 + 12 please.")]}
print_stream(app.stream(inputs, stream_mode="values"))


