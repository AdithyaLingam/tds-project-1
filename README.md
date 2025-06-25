# 🧠 TDS Virtual TA

A **Virtual Teaching Assistant** API for IIT Madras’s Data Science Tools (TDS) course.  
It automatically answers student questions using scraped course material and forum posts (Discourse), and exposes a public REST endpoint.

---

## 🚀 Features

- **Web Scraper**: Collects course content and Discourse threads (Jan–Apr 2025) for contextual understanding.
- **API Endpoint**: Accepts POST requests with student queries and optional base64-encoded images.
- **Automated Responses**: Uses OpenAI GPT models to generate answers and provides relevant Discourse links.
- **Fast & Accurate**: Responds in under 30 seconds and validated using *Promptfoo* against realistic student queries.
- **Deployment-Ready**: Dockerized and deployed via Vercel/Heroku (or your chosen platform). Promptfoo config included.

---

## 📂 Project Structure
<pre>
tds-project-1/
├── api/
│   └── index.py                        # Entry point for FastAPI backend
│
├── app/
│   ├── __pycache__/
│   ├── config.py                       # Configuration settings
│   ├── main.py                         # App-level initialization and routes
│   ├── models.py                       # Pydantic models and schemas
│   └── rag_pipeline.py                 # Core Retrieval-Augmented Generation logic
│
├── data/
│   ├── chroma_db/                      # Local vector store (ChromaDB)
│   ├── discourse_json/                 # Scraped Discourse data (JSON)
│   └── tds_pages_md/                   # Course pages content (Markdown format)
│
├── node_modules/                       # Node dependencies (if used in frontend)
│
├── scripts/
│   ├── build_vector_store.py           # Script to build vector DB from scraped data
│   └── scrape_discourse.py             # Script to scrape Discourse forums
│
├── templates/
│   └── index.html                      # Basic HTML UI (if applicable)
│
├── Dockerfile                          # Container setup for deployment
├── docker-compose.yml                  # (Optional) Multi-service container config
├── promptfooconfig.yaml                # Promptfoo evaluation config
├── requirements.txt                    # Python dependencies
├── vercel.json                         # Deployment config for Vercel
├── Procfile                            # Heroku deployment entry point
├── LICENSE                             # MIT License
└── README.md                           # You are here 📄
</pre>

## ⚙️ Getting Started

### Prerequisites

- Python 3.x
- Docker & Docker Compose (if deploying via containers)
- OpenAI API Key

### Setup Steps

1. Clone the repo:
    ```bash
    git clone https://github.com/AdithyaLingam/tds-project-1.git
    cd tds-project-1
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    npm install        # if using JS/web files
    ```
3. Add your environment variables in `.env`:
    ```env
    OPENAI_API_KEY=your_openai_key_here
    ```
4. (Optional) Scrape Data:
    ```bash
    python scripts/scrape_discourse.py --start=2025-01-01 --end=2025-04-14
    ```
5. Run Locally:
    ```bash
    uvicorn api.main:app --reload
    ```
6. Test the API:
    ```bash
    curl -X POST https://your-app-url/api/ \
      -H "Content-Type: application/json" \
      -d '{"question":"What is X?","image":"<base64>"}'
    ```

---

## 🔍 Promptfoo Evaluation

A Promptfoo config is included for automated testing against sample student queries.

```bash
npx promptfoo eval --config promptfooconfig.yaml
promptfoo view


