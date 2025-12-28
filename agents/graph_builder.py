from typing import Dict

from langgraph.graph import StateGraph, START, END

from .graph_state import GraphState


def planner_node(state: GraphState) -> GraphState:
    """
    Very simple 'planner' for Phase 2.5.

    It looks at user_input and classifies it:
    - if it ends with '?', treat as 'question'
    - otherwise 'statement'
    """
    user_input = state.get("user_input", "")
    msg_type = "question" if user_input.strip().endswith("?") else "statement"
    return {"message_type": msg_type}


def echo_node(state: GraphState) -> GraphState:
    """
    Simple node that uses both user_input and message_type.
    """
    user_input = state.get("user_input", "")
    msg_type = state.get("message_type", "unknown")

    reply_text = (
        f"Echo from LangGraph (type={msg_type}): you said -> {user_input}"
    )

    return {"reply": reply_text}


def build_graph():
    """
    Build and compile a minimal LangGraph graph for Phase 2.5:
    START -> planner_node -> echo_node -> END
    """
    builder = StateGraph(GraphState)

    # Register nodes
    builder.add_node("planner_node", planner_node)
    builder.add_node("echo_node", echo_node)

    # Edges: START -> planner_node -> echo_node -> END
    builder.add_edge(START, "planner_node")
    builder.add_edge("planner_node", "echo_node")
    builder.add_edge("echo_node", END)

    graph = builder.compile()
    return graph


graph_app = build_graph()



# echo_node is your first “agent” node (just logic).
# StateGraph(GraphState) tells LangGraph what state type to use.
# ​graph_app is what FastAPI will call.

# Now the flow is: START → planner_node → echo_node → END.
# ​No change needed in app/main.py for this step; /api/chat will now just get a richer reply.