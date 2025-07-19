# AI SQL Agent for PostgreSQL

## Features
- Connects to PostgreSQL using SQLAlchemy
- Auto-inspects schema (tables + columns)
- Sends schema + user prompt to OpenAI to generate SQL queries
- Executes SQL and returns DataFrame as JSON

## How to Run

1. Create `.env` file from `.env.example`
2. Install dependencies: `pip install -r requirements.txt`
3. Start FastAPI server: `uvicorn app.main:app --reload`

## Endpoints

- `POST /get-sql-query` - Returns SQL query for natural language prompt
- `POST /get-dataframe` - Executes query and returns DataFrame
