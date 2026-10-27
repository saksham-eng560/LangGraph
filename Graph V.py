from typing import List, TypedDict
from langgraph.graph import StateGraph,START,END
import random

class AgentState(TypedDict):
    player_name : str
    lower_bound : int
    upper_bound : int
    guess : List[int]
    status : str

def setup_game(state : AgentState) -> AgentState:
    """Sets up the game by initializing the guess list"""
    state["guess"] = []
    state["player_name"] = input("Enter your name: ")
    state["lower_bound"] = int(input("Enter the lower bound: "))
    state["upper_bound"] = int(input("Enter the upper bound: "))
    if state["lower_bound"] > state["upper_bound"]:
        raise ValueError("The lower bound must be less than or equal to the upper bound.")
    state["status"] = "continue"
    return state

def guess_number(state : AgentState) -> AgentState:
    """Guesses a number and adds it to the guess list"""
    state["guess"].append(random.randint(state["lower_bound"], state["upper_bound"]))
    print(f"{state['player_name']}, I guess {state['guess'][-1]}")
    return state

def hint_node(state : AgentState) -> AgentState:
    """Updates the bounds and stores the next graph route."""
    last_guess = state["guess"][-1]
    user_input = input("Enter if it's too high, too low, or correct: ").strip().lower()
    if user_input == "correct":
        print("I Guessed it!")
        state["status"] = "end"
    elif user_input == "too high":
        state["upper_bound"] = last_guess - 1
        state["status"] = "continue"
    elif user_input == "too low":
        state["lower_bound"] = last_guess + 1
        state["status"] = "continue"
    else:
        raise ValueError("Enter 'too high', 'too low', or 'correct'.")

    if state["status"] == "continue" and state["lower_bound"] > state["upper_bound"]:
        raise ValueError("The hints are inconsistent; no possible number remains.")
    return state

def route_after_hint(state : AgentState) -> str:
    return state["status"]

graph = StateGraph(AgentState)
graph.add_node("Setup", setup_game)
graph.add_node("Guess", guess_number)
graph.add_node("Hint", hint_node)
graph.add_edge(START, "Setup")
graph.add_edge("Setup", "Guess")
graph.add_edge("Guess", "Hint")
graph.add_conditional_edges(
    "Hint",
    route_after_hint,
    {
        "continue" : "Guess",
        "end" : END
    }
)
app = graph.compile()
result = app.invoke({"player_name" : "", "lower_bound" : -1, "upper_bound" : -1})