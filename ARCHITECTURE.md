# SHL Assessment Agent - Architecture Diagram

## High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT                                      │
│                    (Hiring Manager / Recruiter)                         │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ HTTP POST /chat
                                 │ {messages: [...]}
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          FASTAPI SERVER                                  │
│                         (Port 8000)                                      │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      GET /health                                   │  │
│  │                   → {"status": "ok"}                              │  │
│  └───────────────────────────────────────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │                      POST /chat                                    │  │
│  │              Stateless Conversation Handler                        │  │
│  └───────────────────────────┬───────────────────────────────────────┘  │
└────────────────────────────────┼────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      CONSTRAINT EXTRACTION                               │
│                         (GPT-4o-mini)                                    │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Input: Conversation history                                      │  │
│  │  Output: {                                                        │  │
│  │    "role": "Java developer",                                      │  │
│  │    "skills": ["coding", "OOP"],                                   │  │
│  │    "seniority": "mid-level",                                      │  │
│  │    "test_types": ["Knowledge & Skills"]                           │  │
│  │  }                                                                │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      INTENT CLASSIFICATION                               │
│                         (Rule-based + LLM)                               │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  Analyze last message + constraints                               │  │
│  │                                                                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐         │  │
│  │  │ CLARIFY  │  │RECOMMEND │  │  REFINE  │  │ COMPARE  │         │  │
│  │  │          │  │          │  │          │  │          │         │  │
│  │  │ Missing  │  │ Enough   │  │ Update   │  │ Explain  │         │  │
│  │  │  info?   │  │ context? │  │ constraints│ │differences│        │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘         │  │
│  │                                                                    │  │
│  │  ┌──────────┐                                                     │  │
│  │  │  REJECT  │                                                     │  │
│  │  │          │                                                     │  │
│  │  │ Off-topic│                                                     │  │
│  │  │  query?  │                                                     │  │
│  │  └──────────┘                                                     │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                │                │                │
                ▼                ▼                ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   CLARIFY    │  │  RECOMMEND   │  │   COMPARE    │
    │              │  │   / REFINE   │  │              │
    │ Generate     │  │              │  │ Fetch 2      │
    │ follow-up    │  │ Semantic     │  │ assessments  │
    │ question     │  │ Search       │  │ from catalog │
    └──────────────┘  └──────┬───────┘  └──────────────┘
                             │
                             ▼
        ┌─────────────────────────────────────────────────────────┐
        │            SEMANTIC SEARCH ENGINE                        │
        │                                                          │
        │  ┌────────────────────────────────────────────────────┐ │
        │  │ 1. Build query from constraints                    │ │
        │  │    "Java developer mid-level Knowledge & Skills"   │ │
        │  └────────────────────────────────────────────────────┘ │
        │                        ▼                                 │
        │  ┌────────────────────────────────────────────────────┐ │
        │  │ 2. Embed query (sentence-transformers)             │ │
        │  │    all-MiniLM-L6-v2                                │ │
        │  └────────────────────────────────────────────────────┘ │
        │                        ▼                                 │
        │  ┌────────────────────────────────────────────────────┐ │
        │  │ 3. Compute cosine similarity                       │ │
        │  │    with precomputed catalog embeddings             │ │
        │  └────────────────────────────────────────────────────┘ │
        │                        ▼                                 │
        │  ┌────────────────────────────────────────────────────┐ │
        │  │ 4. Rank by similarity score                        │ │
        │  │    Top 50 candidates                               │ │
        │  └────────────────────────────────────────────────────┘ │
        │                        ▼                                 │
        │  ┌────────────────────────────────────────────────────┐ │
        │  │ 5. Filter by constraints                           │ │
        │  │    - Test type (K, P, A, S, C)                     │ │
        │  │    - Seniority (Entry, Mid, Senior)                │ │
        │  │    - Job level                                     │ │
        │  └────────────────────────────────────────────────────┘ │
        │                        ▼                                 │
        │  ┌────────────────────────────────────────────────────┐ │
        │  │ 6. Return top 1-10 matches                         │ │
        │  └────────────────────────────────────────────────────┘ │
        └──────────────────────┬───────────────────────────────────┘
                               │
                               ▼
        ┌─────────────────────────────────────────────────────────┐
        │              SHL PRODUCT CATALOG                         │
        │                  (JSON Database)                         │
        │                                                          │
        │  ┌────────────────────────────────────────────────────┐ │
        │  │ 1000+ Assessments                                  │ │
        │  │                                                    │ │
        │  │ Each with:                                         │ │
        │  │  - name: "Java 8 (New)"                            │ │
        │  │  - link: "https://www.shl.com/..."                 │ │
        │  │  - description: "Measures knowledge of..."         │ │
        │  │  - keys: ["Knowledge & Skills"]                    │ │
        │  │  - job_levels: ["Mid-Professional"]                │ │
        │  │  - duration: "18 minutes"                          │ │
        │  │  - languages: ["English (USA)"]                    │ │
        │  └────────────────────────────────────────────────────┘ │
        │                                                          │
        │  Precomputed Embeddings (768-dim vectors)               │
        │  Loaded at startup for fast search                      │
        └──────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         RESPONSE GENERATION                              │
│                                                                          │
│  ┌───────────────────────────────────────────────────────────────────┐  │
│  │  {                                                                │  │
│  │    "reply": "Here are 5 assessments for Java developer:",        │  │
│  │    "recommendations": [                                           │  │
│  │      {                                                            │  │
│  │        "name": "Java 8 (New)",                                    │  │
│  │        "url": "https://www.shl.com/products/...",                 │  │
│  │        "test_type": "K"                                           │  │
│  │      },                                                           │  │
│  │      ...                                                          │  │
│  │    ],                                                             │  │
│  │    "end_of_conversation": false                                   │  │
│  │  }                                                                │  │
│  └───────────────────────────────────────────────────────────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ HTTP 200 OK
                                 │ JSON Response
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT                                      │
│                    Displays recommendations                              │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow Sequence

```
1. User sends message
   ↓
2. FastAPI receives POST /chat
   ↓
3. Extract constraints from conversation history (LLM)
   ↓
4. Classify intent (clarify/recommend/refine/compare/reject)
   ↓
5a. If CLARIFY → Generate question → Return
5b. If RECOMMEND/REFINE → Semantic search → Filter → Return top 10
5c. If COMPARE → Fetch assessments → Generate diff → Return
5d. If REJECT → Return refusal message
   ↓
6. Format response as JSON
   ↓
7. Return to client
```

## Component Interactions

```
┌──────────────┐
│   FastAPI    │◄────────────────────────────────────┐
│   Server     │                                      │
└──────┬───────┘                                      │
       │                                              │
       │ calls                                        │
       │                                              │
       ▼                                              │
┌──────────────┐         ┌──────────────┐            │
│   OpenAI     │         │  Sentence    │            │
│  GPT-4o-mini │         │ Transformers │            │
│              │         │              │            │
│ - Extract    │         │ - Embed      │            │
│   constraints│         │   queries    │            │
│ - Classify   │         │ - Compute    │            │
│   intent     │         │   similarity │            │
└──────────────┘         └──────┬───────┘            │
                                │                     │
                                │ searches            │
                                │                     │
                                ▼                     │
                         ┌──────────────┐            │
                         │   Catalog    │            │
                         │   (JSON)     │            │
                         │              │            │
                         │ - 1000+      │            │
                         │   assessments│            │
                         │ - Precomputed│            │
                         │   embeddings │            │
                         └──────────────┘            │
                                │                     │
                                │ returns results     │
                                │                     │
                                └─────────────────────┘
```

## Deployment Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      PRODUCTION                              │
│                                                              │
│  ┌────────────────┐                                         │
│  │ Load Balancer  │                                         │
│  │   (AWS ALB)    │                                         │
│  └────────┬───────┘                                         │
│           │                                                  │
│           ├──────────┬──────────┬──────────┐                │
│           │          │          │          │                │
│           ▼          ▼          ▼          ▼                │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐       │
│  │ Agent 1 │  │ Agent 2 │  │ Agent 3 │  │ Agent N │       │
│  │ (Docker)│  │ (Docker)│  │ (Docker)│  │ (Docker)│       │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘       │
│                                                              │
│  Each instance:                                             │
│  - FastAPI server                                           │
│  - Catalog loaded in memory                                 │
│  - Embeddings precomputed                                   │
│  - Stateless (no shared state)                              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ API calls
                           │
                           ▼
                  ┌─────────────────┐
                  │   OpenAI API    │
                  │   (External)    │
                  └─────────────────┘
```

## Key Design Principles

1. **Stateless**: All context in request → Horizontal scaling
2. **Grounded**: All URLs from catalog → No hallucinations
3. **Fast**: Precomputed embeddings → <2s response time
4. **Minimal**: Few dependencies → Easy deployment
5. **Robust**: Guard rails → Rejects off-topic queries
