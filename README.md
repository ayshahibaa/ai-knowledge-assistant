# Enterprise AI Knowledge Assistant — Dubai Property Law

A retrieval-augmented generation (RAG) system that answers questions about Dubai real estate legislation with article-level citations, grounded entirely in official source documents. Think of it as an internal ChatGPT that answers only from a curated document corpus — not the open internet.

## Why this exists

General-purpose chatbots hallucinate on legal questions and cite nothing. This system retrieves the relevant passage from the actual legislation, then generates an answer constrained to that passage — with the article and decree number attached, so every claim is traceable to source. When the corpus doesn't contain the answer, it says so rather than inventing one.

The corpus is Dubai property law (tenancy, rent caps, eviction, registration), but the pipeline is domain-agnostic: swap the documents and it becomes an HR, IT-support, or finance-policy assistant.

## Architecture

```
Streamlit UI
     │
     ▼
Retrieval  ──►  ChromaDB (vector store)
     │          Sentence-Transformers (embeddings)
     │          Cross-Encoder (reranking)
     ▼
Generation ──►  Groq / Llama 3.3 (multi-model failover)
     │
     ▼
Cited answer
```

**Pipeline:** PDF → text extraction → chunking → embeddings → ChromaDB → semantic retrieval → rerank → grounded generation → cited answer.

## Features

- **Grounded answers with citations** — every response cites the source document and page/article; refuses cleanly when the answer isn't in the corpus.
- **Multi-document ingestion** — upload multiple PDFs at once; per-file error isolation so one bad file doesn't break the batch.
- **Multi-provider LLM abstraction** — generation is decoupled from retrieval, with automatic failover across models and retry-on-rate-limit.
- **Document filtering** — restrict retrieval to specific documents, which doubles as a debugging tool for isolating retrieval vs. generation errors.
- **Source-translation transparency** — English translations are surfaced with a note that the Arabic original is authoritative.

## Tech stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| Embeddings | Sentence-Transformers (`all-MiniLM-L6-v2`) |
| Vector store | ChromaDB (persistent) |
| Reranking | Cross-Encoder (`ms-marco-MiniLM-L-6-v2`) |
| Generation | Groq (Llama 3.3 70B, with fallback chain) |
| PDF parsing | pypdf |

## Getting started

### Prerequisites
- Python 3.10+
- A Groq API key ([console.groq.com/keys](https://console.groq.com/keys)) — free tier is sufficient

### Installation

```bash
git clone https://github.com/<your-username>/ai-knowledge-assistant.git
cd ai-knowledge-assistant

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the project root:

```
GROQ_API_KEY=gsk_your_key_here
GROQ_MODELS=llama-3.3-70b-versatile,openai/gpt-oss-120b,qwen/qwen3.6-27b,llama-3.1-8b-instant
```

`.env` is gitignored — never commit your key.

### Run

```bash
streamlit run ui.py
```

Upload PDFs in the sidebar, click **Ingest**, then ask questions.

## Project structure

```
ai-knowledge-assistant/
├── app/
│   ├── config.py       # environment + settings
│   ├── ingest.py       # PDF → chunks → embeddings → ChromaDB
│   ├── retrieve.py     # query → relevant chunks (+ reranking)
│   └── generate.py     # chunks + question → cited answer
├── data/               # source PDFs (gitignored)
├── chroma_db/          # vector store (auto-created, gitignored)
├── .streamlit/
│   └── config.toml     # UI theme
├── ui.py               # Streamlit app
├── requirements.txt
└── .env                # secrets (gitignored)
```

## Data sources

All legislation is sourced from official Dubai Government portals:
- Dubai Legislation Portal (`dlp.dubai.gov.ae`)
- Dubai Land Department / Rental Disputes Center (`dubailand.gov.ae`)

English texts are official translations; the Arabic original is the legally authoritative version. This is noted in-app and should be understood as a limitation of any English-language answer.

## Roadmap

- [ ] Article-boundary chunking (split on `Article (N)` rather than fixed size)
- [ ] Hybrid search (BM25 + vector) for exact-identifier matching
- [ ] Evaluation harness with a labelled question set and accuracy scoring
- [ ] FastAPI backend + Streamlit as thin client
- [ ] Conversation memory for follow-up questions
- [ ] HTML ingestion (for auto-translated Arabic legislation)
- [ ] Docker + docker-compose for deployment
- [ ] Tool calling (e.g. rent-increase calculator invoking Decree 43 tiers)

## Disclaimer

This is a portfolio and educational project. It is not legal advice. Answers are generated from a limited document set and may be incomplete or based on superseded provisions. Consult a qualified legal professional and the authoritative Arabic legislation for any real decision.

