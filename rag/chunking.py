from typing import List


def simple_line_chunker(text: str) -> List[str]:
    """
    Phase 3 placeholder:
    Very naive 'chunker' that splits text by lines.

    Later we will replace this with proper recursive character
    splitting / code-aware chunking.
    """
    # Split on newline and drop empty lines
    return [line for line in text.splitlines() if line.strip()]
