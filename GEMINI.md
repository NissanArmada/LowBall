    # Project Context: Lowball.ai

## 1. Project Overview
Lowball.ai is a mobile-first, AI-powered marketplace negotiation companion. It allows users to upload screenshots of used item listings and utilizes a **Unified Negotiation Agent** with internal Council-of-Thought reasoning to negotiate the lowest possible price with the human seller. 

**Core Objective:** Maintain an extremely modular, low-latency architecture that cleanly separates the mobile presentation layer from the persistent, multi-agent reasoning backend.

## 2. Monorepo Structure
- **`/mobile`**: React Native (Expo) application. Handles UI and local state.
- **`/backend`**: Python (FastAPI) application. Handles AI orchestration, OCR, and market scraping.
- **Type Bridge:** Automated script (`generate_types.py`) ensures end-to-end type safety between Pydantic and TypeScript.

## 3. Tech Stack & Environment
- **Frontend:** React Native (Expo), TypeScript.
- **Backend:** Python 3.11+, FastAPI, Uvicorn, **aiosqlite**.
- **Persistence:** Persistent session state via SQLite (non-blocking).
- **Real-Time Communication:** WebSockets with header-based auth.
- **Data Parsing:** Pydantic (strict schema validation).

## 3. System Architecture & Coding Principles
When generating code or refactoring this project, you MUST adhere to the following System Design constraints:

### A. Strict Separation of Concerns (SoC)
- **Frontend logic** must ONLY handle UI state and local hardware access. It should not contain any business logic or LLM orchestration.
- **Backend logic** must be stateless regarding the HTTP/WS connection but utilize the **Persistent Store** for session continuity.
- **Security:** Use `X-API-Token` headers for authentication. Enforce a 5MB maximum file size for all image uploads.
- **DI Pattern:** Use FastAPI Dependency Injection for all services (Store, AI clients, Limiter) to ensure testability.
- **Resilience:** All external API calls (LLMs, Vision, Scrapers) MUST be wrapped in a **Resilience Layer** implementing exponential backoff retries and **Circuit Breakers**.
- **Scraper Architecture:** Market data scraping MUST be decoupled from the primary request flow. Scrapers MUST update the persistent store asynchronously.
- **Infrastructure Safety:** 
    - **Rate Limiting:** All AI endpoints MUST enforce rate limits to prevent cost explosion.
    - **State Consistency:** WebSocket handlers MUST reload session state from the persistent store at the start of every message turn to pick up background updates.

### B. The Unified Negotiation Agent (Critical)
To minimize latency and cost while maintaining sophisticated reasoning, the system uses a single **Unified Negotiation Agent** rather than multiple separate LLM calls.
1. **Council-of-Thought:** The agent is prompted to simulate an internal "council" (Aggressive, Sympathetic, Analytical nodes) within its own reasoning chain before producing the final response.
2. **Native Structured Outputs:** The system MUST use LLM-native structured output features (e.g., Gemini Response Schemas) to guarantee valid JSON. The backend must NOT rely on regex or manual parsing.
3. **Memory Management:** Conversation history MUST use a sliding window (last 10 turns) to prevent context overflow and control token costs.
*Rule:* All inter-system communication must be strongly typed using Pydantic models.

### C. Asynchronous Non-Blocking Execution
- All LLM API calls, image processing (OCR), and external web scraping must use `async`/`await`. 
- NEVER block the main event loop. Use `aiosqlite` for DB and `BackgroundTasks` for long-running scraping.

### D. API Design & Data Flow
- **Image Uploads:** REST (`POST /api/v1/listing/analyze`).
  - Uses **Vision Analysis Agent** to extract metadata and suggest price targets.
  - Triggers a non-blocking `BackgroundTasks` for market data scraping.
- **Negotiation Chat:** WebSockets (`ws://.../api/v1/chat/{session_id}`).
  - Pushes human text to the **Unified Negotiation Agent**.
  - Returns a synthesized response with rationale and suggested price.

## 4. Code Style & Formatting Guidelines
- **TypeScript (Frontend):** Use functional components and standard React hooks. Strictly type all component props and API response payloads. No `any` types allowed.
- **Python (Backend):** Follow PEP 8. Use explicit type hints for all function arguments and return types. 
- **Error Handling:** Never swallow errors silently. On the backend, throw structured `HTTPException` objects. On the frontend, implement graceful fallback UI alerts for the user.

## 5. Development Workflow (Actionable Rules)
- When asked to create a new feature, outline the **System Design changes first** (API route updates, state changes) before writing the actual code implementation.
- Prioritize modularity. If a file exceeds 200 lines, automatically suggest breaking it into smaller utility modules.

