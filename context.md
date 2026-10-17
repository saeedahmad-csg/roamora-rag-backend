# Project Handover & Context — Roamora Travels RAG Chatbot

**Date:** October 16, 2026  
**Status:** Local Development Complete & Tested | Ready for Cloud Deployment  

---

## 📌 Executive Summary
Today we built, integrated, and refined a production-ready **Retrieval-Augmented Generation (RAG)** chatbot for the **Roamora Travels** website. The chatbot answers customer travel queries strictly grounded in store tour catalogs and policy documents, with zero hallucination and a warm, helpful customer-service fallback.

---

## 🏗️ Architecture & Component Overview

```mermaid
flowchart TD
    subgraph Frontend [React + Vite (Lovable App)]
        A["frontend/src/components/chat-widget.tsx"] -->|POST /chat| B["FastAPI Backend (Port 8000)"]
    end

    subgraph Backend [Python FastAPI + LangChain]
        B --> C["FAISS Vector Store (49 Chunks)"]
        C -->|Top-3 Retrieved Context| D["Prompt Template"]
        D -->|Grounded Generation| E["Gemini 3.5 Flash Lite"]
    end

    subgraph Knowledge Base [Data Sources]
        F["data/company_info.txt (Policies, FAQs, Booking Guide)"] --> C
        G["data/products.xlsx (8 Tour Packages incl. Swat)"] --> C
    end
```

---

## ✅ What Was Completed Today

1. **RAG AI Pipeline & Models (`rag.py`)**:
   - **Generation LLM:** Integrated Google's fastest lightweight model: `gemini-3.5-flash-lite`.
   - **Embeddings:** Powered by `models/gemini-embedding-001`.
   - **Grounded Retrieval:** Vector similarity search retrieves top-3 relevant chunks.
   - **Graceful Fallback:** Replaced the blunt *"I don't know"* with a warm, professional fallback that directs unlisted destination inquiries to the *"Plan Your Trip"* form or team email (`hello@roamoratravels.com`).

2. **FastAPI REST Backend (`api.py`)**:
   - Automatically loads `GEMINI_API_KEY` from `.env` at startup.
   - Indexes documents once into FAISS at startup (49 chunks, zero runtime embedding latency).
   - Endpoints: `GET /health`, `POST /chat`, and `POST /reload` (for dynamic re-indexing).

3. **Frontend Chat Widget (`frontend/src/components/chat-widget.tsx`)**:
   - **Visible Floating Card:** Self-contained box with clean borders (`border-2 border-border`), shadows, and rounded corners (`rounded-2xl`).
   - **Prominent Exit Button:** Clear `✕ Exit` button in header + `Esc` key keyboard shortcut to close.
   - **Full Mobile Responsiveness:** Automatically adapts to full-screen mode on mobile devices with safe-area bottom padding for iPhone/Android.
   - **Clean Typography:** Sanitizer strips raw markdown `**` asterisks and formats lists into clean unicode bullet dots (`•`).
   - **Immediate Suggestion Dismissal:** Quick suggestion pills disappear immediately once any question is clicked or sent.
   - **Header Polish:** Removed cluttered subtitle line, keeping a clean title and status icon.

4. **Expanded Knowledge Base**:
   - **`data/company_info.txt`**: Added step-by-step booking guide (30% deposit, 70% balance due 21 days prior), family/children discount policies, luggage rules, dietary notice guidelines, and FAQs.
   - **`data/products.xlsx`**: Added **Swat Valley & Kalam Alpine Discovery** (4 Days / 3 Nights, $380 discounted / $450 regular) alongside Hunza, Skardu, Dubai, Bali, Istanbul, Paris, and Northern Circuit packages.

---

## 🚀 Deployment Action Plan & Current Status

### ✅ Step 1: Frontend + AI Backend Merged & Deployed to GitHub (COMPLETED)
To eliminate Render's credit-card paywall and external server dependencies, the backend AI consultant was **merged directly into the frontend** using TanStack Start & Nitro:
- **Repository:** `https://github.com/saeedahmad-csg/roamora-travels.git`
- **Branch:** `main`
- **Architecture Highlights:**
  - In-memory Knowledge Base ([`frontend/src/lib/knowledge-base.ts`](file:///d:/Projects/12-%20RAG%20Chatbot/frontend/src/lib/knowledge-base.ts)): Houses all 8 tour packages (Hunza, Skardu, Swat, Dubai, Bali, Istanbul, Paris, Northern Circuit) + booking terms, deposit & cancellation policies, baggage & health guidelines.
  - AI Engine ([`frontend/src/lib/roamora-ai.ts`](file:///d:/Projects/12-%20RAG%20Chatbot/frontend/src/lib/roamora-ai.ts)): Direct integration with Google Gemini (`gemini-3.8-flash` & `gemini-3.5-flash-lite`), grounded context injection, warm fallback for unlisted inquiries, and source citations.
  - TanStack Start Server Function ([`frontend/src/lib/chat-server.ts`](file:///d:/Projects/12-%20RAG%20Chatbot/frontend/src/lib/chat-server.ts)): Native RPC server function executed purely on the server.
  - Nitro & Vite Endpoints ([`frontend/src/server.ts`](file:///d:/Projects/12-%20RAG%20Chatbot/frontend/src/server.ts) & [`frontend/vite.config.ts`](file:///d:/Projects/12-%20RAG%20Chatbot/frontend/vite.config.ts)): Full support for `POST /api/chat` and `POST /chat` with CORS, both in local development (`npm run dev`) and in production on Cloudflare / Lovable.
  - Chat Widget ([`frontend/src/components/chat-widget.tsx`](file:///d:/Projects/12-%20RAG%20Chatbot/frontend/src/components/chat-widget.tsx)): Instant 0ms pre-mounted opening, auto-focus input, multi-turn conversation memory, and sleek custom scrollbars without Windows gray arrow buttons.
- **Latest Commit:** `14baf1b` (pushed to `main`).
- **Lovable Sync:** Lovable automatically pulls and builds the live website. Zero external servers needed!

### 📦 Standalone Python Backend (Optional / Archived)
The Python FastAPI codebase remains completely functional in the root directory for standalone deployments (e.g. Hugging Face Spaces):
- **Repository:** `https://github.com/saeedahmad-csg/roamora-rag-backend.git`
- **Files:** `api.py`, `rag.py`, `Dockerfile`, `Procfile`, `render.yaml`


---

## 💻 How to Run Locally Tomorrow (Reference)

If you need to test locally again:
```powershell
# Terminal 1: Backend
cd "d:\Projects\12- RAG Chatbot"
.\.venv\Scripts\python.exe -m uvicorn api:app --host 127.0.0.1 --port 8000

# Terminal 2: Frontend
cd "d:\Projects\12- RAG Chatbot\frontend"
npm run dev
```
* **Frontend:** [http://localhost:8080](http://localhost:8080)
* **Backend API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
