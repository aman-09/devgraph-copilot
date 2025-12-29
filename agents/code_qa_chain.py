from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

from app.config import settings


def get_llm() -> ChatOpenAI:
    """
    Return a chat model instance.

    This uses an OpenAI-compatible API (e.g., OpenAI, Groq, or another provider)
    configured via environment variables.
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY is not set in the environment/.env file")

    return ChatOpenAI(
        api_key=settings.openai_api_key,
        model=settings.llm_model_name,
        temperature=0.2,
    )


# Prompt: RAG-style
QA_PROMPT = ChatPromptTemplate.from_template(
    """
You are a helpful senior software engineer assistant.
You answer questions about the project DevGraph Copilot.

You MUST:
- Use only the provided context.
- If the context is insufficient, say you are not sure and suggest what could be done.

Context:
{context}

Question:
{question}
"""
)


def answer_with_context(question: str, retrieved_chunks: List[str]) -> str:
    """
    Use the LLM to answer a question based on retrieved context chunks.
    """
    context = "\n\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context available."

    llm = get_llm()
    chain = QA_PROMPT | llm  # prompt -> LLM

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )

    # response is an AIMessage; use .content
    return response.content.strip()


# This defines:
# A reusable get_llm().
# A RAG prompt template.
# answer_with_context(question, retrieved_chunks) that returns a natural language answer.
