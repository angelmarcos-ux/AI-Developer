# AI Client Enquiry Processor

An AI-powered tool that classifies incoming client enquiries, assesses confidence and sentiment, assigns priority, and generates suggested responses — enabling staff to handle client communications faster and more consistently.

## Who Is This For?

Staff members handling incoming client communications (emails, contact forms, live chat). The tool augments human judgement by providing instant classification, priority assessment, and draft replies that can be reviewed and sent.

---

## Architecture

```
┌──────────────────────┐        ┌──────────────────────┐        ┌─────────────────┐
│   Nuxt 3 Frontend    │  HTTP  │   Flask API Backend  │  HTTPS │   OpenAI GPT    │
│   (localhost:3000)   │───────▶│   (localhost:5000)   │───────▶│   (gpt-4o-mini) │
│                      │◀───────│                      │◀───────│                 │
│  - EnquiryForm.vue   │  JSON  │  - /api/analyse      │  JSON  │  - Classification│
│  - ResultCard.vue    │        │  - /api/history      │        │  - Sentiment     │
│  - HistoryList.vue   │        │  - /api/health       │        │  - Responses     │
└──────────────────────┘        └──────────────────────┘        └─────────────────┘
```

### Why Two Processes?

| Concern | Benefit |
|---------|---------|
| **Separation of concerns** | Frontend handles UI/UX; backend handles AI logic, validation, and API keys |
| **Independent scaling** | Backend can be deployed behind a load balancer without touching the frontend |
| **Security** | API keys never reach the browser; CORS restricts origins |
| **Flexibility** | Either layer can be swapped (e.g., replace Nuxt with React, or Flask with FastAPI) |

The Nuxt dev server proxies `/api` requests to Flask on port 5000, so the frontend never calls an external origin directly during development.

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | **Nuxt 3** (Vue 3) | SPA dashboard with file-based routing |
| Styling & UI | **Nuxt UI & Tailwind CSS** | Enterprise-grade component library and utility-first CSS |
| State | **Pinia** | Type-safe, modular state management |
| Backend | **FastAPI** | Modern, fast (high-performance), web framework for building APIs with Python |
| CORS | **fastapi.middleware.cors** | Cross-origin requests from the frontend |
| AI | **OpenAI SDK** (`openai` Python package) | Communicates with GPT API |
| Model | **GPT-4o-mini** | Cost-effective classification and generation |
| Config | **python-dotenv** | Loads `.env` for secrets |

---

## Setup Instructions

### Prerequisites

- Python 3.10+
- Node.js 18+
- An OpenAI API key ([platform.openai.com](https://platform.openai.com))

### 1. Clone / Download

```bash
git clone <repository-url>
cd folder
```

### 2. Backend Setup

```bash
cd backend

# Create your environment file
cp .env.example .env
# Edit .env and add your real API key:
#   OPENAI_API_KEY=sk-...

# Install dependencies
pip install -r requirements.txt

# Start the API server
python main.py
```

The Flask server starts on **http://localhost:5000**. Verify with:

```bash
curl http://localhost:5000/api/health
# → {"status": "healthy"}
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

The Nuxt app starts on **http://localhost:3000**.

### 4. Open the App

Navigate to [http://localhost:3000](http://localhost:3000) in your browser.

---

## How to Use

1. **Enter enquiry text** — Paste or type a client message into the text area on the main panel.
2. **Click "Analyse"** — The enquiry is sent to the Flask backend, which forwards it to GPT-4o-mini.
3. **View results** — The result card displays:
   - **Category** (e.g., "Support Request", "Complaint")
   - **Confidence score** (0.0–1.0)
   - **Sentiment** (positive / neutral / negative)
   - **Priority** (low / medium / high / urgent)
   - **Suggested response** — a professional draft reply
   - **Recommended actions** — concrete next steps for staff
   - **Reasoning** — why the AI chose this classification
   - **Vague input warning** — shown when confidence is below 0.4
4. **Check history** — The sidebar lists all previous analyses from the current session, most recent first.

---

## Prompt Engineering

This section details the design of the system prompt that drives the AI classification engine.

### System Prompt Design

The prompt in `ai_processor.py` follows a structured approach:

```text
You are an expert business enquiry analyst for a professional services firm.

Your task is to analyse incoming client enquiries and classify them accurately.

You MUST return valid JSON with the following fields:
- "category": One of these exact categories: "New Client Enquiry", "Support Request",
  "Complaint", "General Question", "Urgent/Escalation"
- "confidence": A float between 0.0 and 1.0 representing your certainty
- "sentiment": One of "positive", "neutral", or "negative"
- "priority": One of "low", "medium", "high", or "urgent"
- "suggested_response": A professional draft reply (2-4 sentences)
- "recommended_actions": A list of 2-4 concrete next steps
- "reasoning": Brief explanation of why this classification was chosen
```

Each category includes a **definition** and a **concrete example** so the model has clear anchoring points for classification decisions.

### Why Structured JSON Output?

- **Reliability** — `response_format: { type: "json_object" }` forces the model to return parseable JSON every time.
- **Consistent fields** — The prompt enumerates every expected field, so downstream code can rely on a stable schema.
- **Machine-readable** — Results can feed directly into dashboards, databases, or downstream automation without string parsing.

### Why Temperature 0.3?

```python
OPENAI_TEMPERATURE = 0.3  # Low temperature for consistent classification
```

- **Too low (0.0):** Fully deterministic — can produce robotic suggested responses.
- **Too high (0.7+):** Creative but less predictable classification; categories may drift.
- **0.3 sweet spot:** Classification stays consistent and repeatable while the `suggested_response` field retains enough natural language fluency.

### Confidence Calibration

The system prompt includes this instruction:

> "If the input is vague, nonsensical, or not a genuine client enquiry, still classify it to the best of your ability but set confidence below 0.4."

The backend then flags any result with `confidence < 0.4` by adding `is_vague: true`, which the frontend uses to show a warning to the user. This provides a built-in safety net for garbage input without refusing to respond entirely.

### Priority Assignment Rules

The prompt also encodes explicit priority rules:

| Priority | Trigger |
|----------|---------|
| urgent | Regulatory deadlines, legal matters, system outages |
| high | Complaints, time-sensitive requests (within 48 hours) |
| medium | New client enquiries, standard support requests |
| low | General questions, informational queries |

---

## Error Handling Strategy

### Input Validation (Backend)

| Check | Response |
|-------|----------|
| Empty or whitespace-only text | `"Enquiry text cannot be empty."` |
| Text exceeds 5,000 characters | `"Enquiry text exceeds the maximum length of 5000 characters."` |
| Missing `enquiry` field in request body | `"Request body must include an 'enquiry' field."` |

### Vague / Nonsensical Input Detection

Rather than rejecting ambiguous input, the system classifies it with low confidence (`< 0.4`) and sets the `is_vague` flag. The frontend displays a warning so the staff member knows the result should be treated cautiously.

### OpenAI API Error Handling

Each error type returns a user-friendly message:

| Error Class | Message |
|-------------|---------|
| `AuthenticationError` | "OpenAI authentication failed. Please check your API key." |
| `RateLimitError` | "OpenAI rate limit exceeded. Please try again in a moment." |
| `APIConnectionError` | "Could not connect to OpenAI API. Please check your network connection." |
| `APIError` | "OpenAI API error: {details}" |
| `JSONDecodeError` | "Failed to parse AI response as valid JSON." |
| Unexpected exceptions | "An unexpected error occurred: {details}" |

### Frontend Error Display

When `success: false` is returned, the frontend displays the error message inline so the user receives immediate, actionable feedback without leaving the page.

---

## Automation Potential

This prototype is designed as a foundation. Here's how it could plug into larger workflows:

### Email Integration

- **IMAP/POP3 polling**: A background worker polls an inbox at regular intervals, feeds new messages through `/api/analyse`, and stores the results.
- **Incoming webhook**: Services like SendGrid or Mailgun forward inbound emails as HTTP POSTs directly to the API.

### CRM Integration

- Push classification results, priority, and suggested responses to **Salesforce**, **HubSpot**, or **Zoho** via their REST APIs.
- Auto-populate custom fields: category, sentiment, priority.
- Create tasks/tickets for high-priority or urgent items.

### Task Queue (Async Processing)

- **Celery + Redis** for asynchronous processing of high-volume enquiries.
- Decouple the HTTP response from the AI call so users aren't waiting on OpenAI latency.
- Supports retry logic and dead-letter queues for failed API calls.

### Notifications

- **Slack/Teams webhooks**: Instant alerts for urgent or high-priority enquiries.
- Auto-route to the appropriate team channel based on category.
- Escalation rules: if no human responds within X minutes, re-notify or escalate.

### Database Persistence

- Currently implemented using **SQLite** via SQLAlchemy ORM for robust data storage.
- Easily swappable to **PostgreSQL** or **MySQL** by changing the `DATABASE_URL` environment variable for production deployments.
- Enables analytics dashboards: classification distribution, average confidence, response times.
- Full audit trail for compliance.

### Auto-Response

- For high-confidence classifications (e.g., > 0.9), configure automatic sending of the suggested response.
- Staff receive a digest of auto-handled enquiries for review.
- Configurable per-category: auto-reply to "General Question" but always require human review for "Complaint".

---

## Design Decisions

| Decision | Rationale |
|----------|-----------|
| **FastAPI** | Modern async architecture, built-in validation via Pydantic, and automatic Swagger docs. Replaces the old Flask implementation to provide true enterprise-grade scalability. |
| **Nuxt 3** | Modern Vue 3 framework with built-in dev proxy (`nitro.devProxy`), file-based routing, and composables. Ready for SSR if needed later. |
| **GPT-4o-mini** | Cost-effective for classification tasks (~10x cheaper than GPT-4o), fast response times (~1–2s), and sufficient intelligence for structured classification. |
| **Database** | SQLAlchemy and SQLite provide an enterprise-ready ORM setup. This is a massive upgrade from in-memory lists, ensuring data persistence while remaining zero-config for local development. |
| **Nuxt UI / Tailwind** | Provides a beautiful, accessible, and fully responsive enterprise FinTech/Terminal aesthetic component library (cards, forms, badges, icons) out-of-the-box, replacing plain CSS. |
| **Pinia** | The standard Vue state management library ensures global state is robustly managed, replacing simple reactive composables for scalability. |
| **Dev proxy** | Avoids CORS complexity in development; production would use a reverse proxy (e.g., nginx) instead. |

---

## Bonus Features Implemented

- **Confidence scoring** — The model self-assesses certainty; low-confidence results are flagged to the user.
- **Prompt engineering** — Detailed system prompt with category definitions, examples, priority rules, and structured output enforcement.
- **Comprehensive error handling** — Graceful handling of empty input, oversized input, vague content, and all OpenAI SDK error classes.
- **Automation potential** — Architecture designed for extensibility with clear integration points documented above.
- **Rate Limiting** — Integrated `slowapi` on the backend to prevent API abuse (limits endpoints to 5 requests/minute per IP) with graceful UI error handling.
- **Sentiment analysis** — Beyond classification, the model also assesses emotional tone.
- **Priority assignment** — Rule-based priority framework baked into the prompt.
- **Recommended actions** — Actionable next steps generated for staff, not just a classification label.

---

## API Reference

### `POST /api/analyse`

Analyse a client enquiry.

**Request:**
```json
{
  "enquiry": "I can't access my client portal and need my tax docs by Friday."
}
```

**Response (200):**
```json
{
  "success": true,
  "enquiry": "I can't access my client portal and need my tax docs by Friday.",
  "timestamp": "2026-05-11T10:30:00+00:00",
  "data": {
    "category": "Support Request",
    "confidence": 0.92,
    "sentiment": "negative",
    "priority": "high",
    "suggested_response": "Thank you for reaching out. I'm sorry to hear you're having trouble accessing the portal. Let me escalate this to our IT team immediately so we can restore your access well before Friday.",
    "recommended_actions": [
      "Escalate portal access issue to IT support",
      "Confirm client's identity and account details",
      "Follow up within 24 hours with resolution status"
    ],
    "reasoning": "Client is requesting help with an existing service (portal access) and has a time constraint, making this a high-priority support request.",
    "is_vague": false
  }
}
```

### `GET /api/history`

Retrieve all past analyses.

### `GET /api/health`

Health check — returns `{"status": "healthy"}`.

---

## License

This project is a prototype/demonstration. See repository for licence terms.
