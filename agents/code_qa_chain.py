from typing import List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate  # <-- add this

from app.config import settings

def get_llm() -> ChatOpenAI:
    """
    Factory for the chat model (Groq via OpenAI-compatible API).
    """
    return ChatOpenAI(
        model=settings.llm_model_name,
        api_key=settings.groq_api_key,
        base_url=settings.llm_base_url,
        temperature=0.2,
    )



# llm = ChatOpenAI(
#     model=settings.llm_model_name,
#     api_key=settings.groq_api_key,
#     base_url=settings.llm_base_url,  # crucial: Groq endpoint
# )



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
    Standard QA-style answer using the RAG context.
    """
    context = "\n\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context available."

    llm = get_llm()
    chain = QA_PROMPT | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )
    return response.content.strip()



# Prompt: system design / architecture explainer
DESIGN_EXPLAINER_PROMPT = ChatPromptTemplate.from_template(
    """
You are a senior backend engineer explaining a system design in an interview.

The system is DevGraph Copilot, an agentic RAG backend built with FastAPI, LangGraph, and a local RAG pipeline.
Using only the provided context, produce a clear, structured explanation in this style:

- High-level overview (2–3 bullets)
- Main components and their roles
- How a request flows through the system
- Any trade-offs or future improvements you can see

If the context is insufficient to answer, say you are not sure and explain what extra information you would need.

Context:
{context}

Interview-style question:
{question}
"""
)

def explain_design_with_context(question: str, retrieved_chunks: List[str]) -> str:
    """
    Use the LLM to produce a system-design-style explanation
    based on the retrieved context chunks.
    """
    context = "\n\n".join(retrieved_chunks) if retrieved_chunks else "No relevant context available."

    llm = get_llm()
    chain = DESIGN_EXPLAINER_PROMPT | llm

    response = chain.invoke(
        {
            "context": context,
            "question": question,
        }
    )
    return response.content.strip()

