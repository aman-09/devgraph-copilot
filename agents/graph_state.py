from typing import TypedDict, Optional, List


class GraphState(TypedDict, total=False):
    """
    Shared state for the LangGraph workflow.

    Phase 2.5 / 3:
    - user_input: raw message from API
    - message_type: simple classification (e.g., 'question', 'statement')
    - reply: response text
    - retrieved_chunks: list of text chunks retrieved from the vector store
    """

    user_input: str
    message_type: Optional[str]
    reply: Optional[str]
    retrieved_chunks: Optional[List[str]]




# user_input is what comes from the API.
# reply is what our node will set.
# This adds message_type, which planner will set.
# Extend GraphState for retrieved chunks