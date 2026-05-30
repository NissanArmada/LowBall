<p align="center">
   <img src="https://c.tenor.com/M4kj6V6ZDOkAAAAd/tenor.gif" alt="Uma FB Marketplace">
</p>

# 💸 Lowball.ai (Work In Progress)

Lowball.ai is a mobile-first, AI-powered marketplace negotiation companion. It utilizes a sophisticated backend architecture to negotiate the best possible prices on marketplace listings (Facebook Marketplace, OfferUp) using a multi-persona "Council-of-Thought" reasoning engine.

This project is designed as an **Architectural Showcase**, prioritizing modularity, low latency, and high-fidelity system design patterns.

## 🚀 Key Architectural Pillars

### 1. Unified Negotiation Engine
Instead of multiple expensive and high-latency LLM calls, the system uses a single **Unified Agent** that simulates an internal "Council" (Aggressive, Sympathetic, and Analytical nodes) within a single inference chain.

### 2. High-Performance Backend (FastAPI)
- **100% Asynchronous:** Built with `FastAPI` and `uvicorn`, utilizing non-blocking I/O across the entire stack.
- **Persistent State:** Uses `aiosqlite` for a non-blocking, session-based persistence layer that survives disconnects and restarts.
- **Native Structured Outputs:** Guarantees 100% JSON reliability by leveraging LLM-native response schemas.

### 3. Engineering Standards
- **Dependency Injection (DI):** Decoupled service architecture for maximum testability and modularity.
- **Type-Safe Monorepo:** An automated bridge synchronizes Python Pydantic models with TypeScript interfaces, ensuring end-to-end type safety.
- **Observability:** Integrated middleware for real-time latency tracking and performance logging.
- **Memory Management:** Implements a sliding-window context to maintain low token costs and prevent context overflow.

## 📁 Project Structure

```text
/backend          # Python (FastAPI)
  ├── agents/     # Unified Agent logic (Council-of-Thought)
  ├── api/        # REST & WebSocket endpoints
  ├── core/       # Centralized Config & DI logic
  ├── models/     # Pydantic schemas (Source of Truth)
  ├── services/   # Persistence, Vision, Scraper, Limiter, and Resilience
  └── scripts/    # Type-generation & utility scripts

/mobile           # React Native (Expo)
  ├── app/        # Expo Router (Tabs: Home, Scanner, Chat)
  ├── components/ # Atomic UI components
  └── constants/  # Shared types and styling
```

## 🛠️ Getting Started

### Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

### Mobile Setup
```bash
cd mobile
npm install
npm start
```

## 📜 Development Conventions
All development must adhere to the mandates defined in **`GEMINI.md`**, which serves as the foundational system design guide for this repository (...or not i guess)
