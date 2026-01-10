Describe how Groq is wired in:

LLM client:
Uses Groq’s OpenAI-compatible /chat/completions endpoint.

Where used:
Planner prompt.
Code QA prompt with retrieved context.

Notes:
Why Groq (latency, cost, model choice).
How API keys are read from config/env (app/config.py).