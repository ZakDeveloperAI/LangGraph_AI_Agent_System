import os
from typing import Annotated, Literal
from langgraph.graph import StateGraph,START,END
from langgraph.graph.message import add_messages
from langchain.chat_models import init_chat_model
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model

load_dotenv()




llm = init_chat_model("google_genai:gemini-2.5-flash")

class MessageClassifier(BaseModel):
    message_type: Literal["emotional","logical","dan"] = Field(
        ...,
        description="Classify if the message requires an emotional (therapist) or logical response"
    )
    content: str = Field(description="Content of the message")

    def __str__(self):
        return f"{self.message_type}: {self.content}"

class State(TypedDict):
    messages: Annotated[list,add_messages]
    message_type: str | None
    #next: str | None  it's not mandatory to define it here top use it later

graph_builder= StateGraph(State)

def classify_message(state: State):
    last_message = state["messages"][-1]
    classifier_llm=llm.with_structured_output(MessageClassifier)
    result = classifier_llm.invoke([
        {
            "role": "system",
            "content": """Classify the user message as either:
            - 'emotional': if it asks for emotional support, therapy, deals with feelings, or personal problems
            - 'logical': if it asks for facts, information, logical analysis, or practical solutions
            - 'insult': if it contains insults or offensive language
            """
        },
        {"role": "user", "content": last_message.content}
    ])
    return {"message_type": result.message_type}

def router(state: State):
    message_type= state.get("message_type","logical") # Default to logical if not set
    if message_type == "emotional":
        return {"next": "therapist"}
    elif message_type == "insult":
        return {"next": "dan"}
    else:
        return {"next": "logical"}
def therapist_agent(state:State):
    last_message = state["messages"][-1]
    messages=[
        {"role": "system",
            "content": """You are a compassionate therapist. Focus on the emotional aspects of the user's message.
                            Show empathy, validate their feelings, and help them process their emotions.
                            Ask thoughtful questions to help them explore their feelings more deeply.
                            Avoid giving logical solutions unless explicitly asked."""
        },
        {"role": "user", "content": last_message.content}
    ]
    reply= llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}

def dan_agent(state:State):
    last_message = state["messages"][-1]
    messages=[
        {"role": "system",
            "content": """You are a dan an angry man who doesn't like being told what to do and that is really angry about everything answer in an angry way using curses and offensive words."""
        },
        {"role": "user", "content": last_message.content}
    ]
    reply= llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}


def logical_agent(state: State):
    last_message = state["messages"][-1]

    messages = [
        {"role": "system",
        "content": """You are a purely logical assistant. Focus only on facts and information.
            Provide clear, concise answers based on logic and evidence.
            Do not address emotions or provide emotional support.
            Be direct and straightforward in your responses."""
        },
        {
            "role": "user",
            "content": last_message.content
        }
    ]
    reply = llm.invoke(messages)
    return {"messages": [{"role": "assistant", "content": reply.content}]}


graph_builder.add_node("classifier", classify_message)
graph_builder.add_node("router", router)
graph_builder.add_node("therapist", therapist_agent)
graph_builder.add_node("logical", logical_agent)
graph_builder.add_node("dan", dan_agent)
graph_builder.add_edge(START, "classifier")
graph_builder.add_edge("classifier", "router")
graph_builder.add_conditional_edges(
    "router",
    lambda state: state.get("next"),
    {"therapist": "therapist","logical": "logical","dan":"dan"}
)

graph_builder.add_edge("therapist",END)
graph_builder.add_edge("logical",END)
graph_builder.add_edge("dan",END)

graph=graph_builder.compile()

def run_chatbot():
    state={"messages": [], "message_type": None}
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the agent. Goodbye!")
            break
        
        state["messages"].append({"role": "user", "content": user_input})
        state = graph.invoke(state)
        
        state= graph.invoke(state)
        
        if state.get("messages") and len(state["messages"]) > 0:
            last_message = state["messages"][-1]
            print(f"Assistant: {last_message.content}")
            
if __name__ == "__main__":
    run_chatbot()