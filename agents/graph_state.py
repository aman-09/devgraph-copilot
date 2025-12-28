from typing import TypedDict, Optional


class GraphState(TypedDict, total=False):
    """
    Shared state for the LangGraph workflow.

    Phase 2:
    - user_input: raw message from API
    - message_type: simple classification (e.g., 'question', 'other')
    - reply: response text
    """

    user_input: str
    message_type: Optional[str]
    reply: Optional[str]



# user_input is what comes from the API.
# reply is what our node will set.
# This adds message_type, which planner will set.