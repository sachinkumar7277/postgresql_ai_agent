
# 🧠 AI SQL Agent with FastAPI + Selenium + OpenAI

This project is an **AI-powered SQL Agent** that takes **natural language prompts** and returns **SQL queries** and **dataframes** using:
- FastAPI (backend API)
- Selenium (to automate ChatGPT interaction)
- OpenAI (to generate SQL from prompts)
- SQLAlchemy (for database interaction)
- Persistent cookie-based session for seamless ChatGPT use

---

## 🔧 Features

- 🗝️ Login once manually, persist ChatGPT session using cookies.
- 🧠 Automatically load and feed your **PostgreSQL database schema** to GPT.
- 💬 Ask natural language questions like:  
  _"Give me total sales by region for last month"_ → Get raw SQL + DataFrame.
- 📄 Multi-turn schema memory using local session files (no token bloat).

---

## How to Run

1. Create `.env` file from `.env.example`
2. Install dependencies: `pip install -r requirements.txt`
3. Start FastAPI server: `uvicorn app.main:app --reload`

## Endpoints

- `POST /get-sql-query` - Returns SQL query for natural language prompt
- `POST /get-dataframe` - Executes query and returns DataFrame

### 1️⃣ Clone the Repo

```bash
https://github.com/sachinkumar7277/postgresql_ai_agent.git
cd postgresql_ai_agent

--- 

##  🧭 API Flow & Usage
🔐 1. Login to ChatGPT (Manual Login)


- GET /login-into-chat-gpt
- This will launch a browser using Selenium.
- Manually login to ChatGPT once.
- Your session cookies will be stored and reused.

🏗️ 2. Feed All Table Names to GPT

- GET /initiate-sql-ai-agent
- This will send the list of all tables in your DB to ChatGPT to help it understand your schema.

📊 3. Feed Table Schemas (one-by-one with token check)

- GET /load-db-tables-schema
- This loads and appends each table’s schema to ChatGPT in memory, avoiding token overload.

- If token threshold is exceeded, the process halts — call this API again to continue.

💬 4. Get Dataframe for a Prompt

POST /get-dataframe
Body (JSON)
{
  "prompt": "Get total revenue by product for Q1"
}

Response
{
  "data": [
    {"product": "A", "revenue": 10000},
    {"product": "B", "revenue": 9500}
  ],
  "sql_query": "SELECT product, SUM(revenue) FROM sales WHERE quarter = 'Q1' GROUP BY product"
}

🧠 Project Structure
.
├── app/
│   ├── __init__.py
│   ├── ai.py                  # Prompt builder and OpenAI API caller
│   ├── cookies.py             # Cookie loader/saver for ChatGPT session
│   ├── database.py            # SQLAlchemy DB connection
│   ├── driver_manager.py      # Singleton Selenium driver management
│   ├── main.py                # FastAPI entrypoint
│   ├── save_cookies.py        # Script to save cookies.json after login
│   ├── schemas.py             # Pydantic request/response models
│   ├── services.py            # Business logic for prompt -> SQL -> DataFrame
│   ├── session_utils.py       # Session memory manager
├── frontend/                  # (Optional) frontend code (React/Streamlit)
├── venv/                      # Python virtual environment
├── .env                       # Environment variables (should match .env.example)
├── .env.example               # Example env file
├── .gitignore
├── chatgpt_session_url.json   # Optional session storage
├── chatgpt_session.json       # Stores table schema memory
├── cookies.json               # Exported cookies to persist ChatGPT login
├── docker-compose.yml         # Docker + service config
├── Dockerfile                 # App containerization
├── README.md
├── requirements.txt           # Python dependencies

🛠️ Requirements
✅ Python 3.8+

✅ Google Chrome installed

✅ PostgreSQL running

✅ Manual login to ChatGPT (one-time)

✅ OpenAI account (free or pro)

💡 Example Use Case

1. GET /login-into-chat-gpt         # Login manually via browser (first time only)
2. GET /initiate-sql-ai-agent       # Send table names
3. GET /load-db-tables-schema       # Feed schema gradually
4. POST /get-dataframe              # Get SQL + results for prompt

🧑‍💻 Author
Sachin Kumar
GitHub: @sachinkumar7277
Demo link: https://www.youtube.com/watch?v=NuOZf_8jyy0

---
