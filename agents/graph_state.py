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
    message_type: str
    reply: str
    retrieved_chunks: List[str]

    # New ingestion metadata
    last_ingestion_time: Optional[str]      # ISO string or simple timestamp
    last_ingestion_source: Optional[str]    # e.g., "sample_data"

    needs_ingestion: Optional[bool]         # Planner sets this to True if ingestion is needed

    file_content: Optional[str]             # File content for ingestion




# user_input is what comes from the API.
# reply is what our node will set.
# This adds message_type, which planner will set.
# Extend GraphState for retrieved chunks