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

tds-project-1/
├── api/                     # FastAPI or Flask backend application (main logic lives here)
│   └── main.py              # Entry point for the API
│
├── app/                     # Optional: frontend templates or assets (if applicable)
│
├── data/                    # Scraped Discourse/course data (optional or temporary)
│
├── scripts/                 # Custom Python scripts
│   └── scrape_discourse.py # Script to scrape forum posts within a date range
│
├── templates/               # HTML templates (for web UI rendering)
│
├── Dockerfile               # Container setup for backend deployment
├── docker-compose.yml       # Optional multi-container orchestration
├── promptfooconfig.yaml     # Config for Promptfoo evaluation tool
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel deployment configuration
├── Procfile                 # Heroku deployment entry point
├── LICENSE                  # MIT License
└── README.md                # Project documentation

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


