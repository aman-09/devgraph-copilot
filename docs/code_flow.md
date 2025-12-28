# DevGraph Copilot – Code Flow

## 1. Phase 1 – Request Flow

- Client sends GET `/`
- FastAPI handles the request in `app.main.read_root`
- Returns static JSON with a Phase 1 message

## 2. Phase 2+ – Planned Flow

- Client sends POST `/api/chat` (to be added)
- FastAPI will call a LangGraph app (to be added)
- Graph will run planner and other agents step-by-step
