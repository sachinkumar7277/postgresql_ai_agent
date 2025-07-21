from fastapi import FastAPI
from sqlalchemy import text
from .schemas import PromptRequest, RawSQLQuery
from .services import (
    get_data_from_prompt,
    generate_sql_query,
    get_schema_description,
    get_data_from_raw_query
)
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add this to enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/get-sql-query")
def get_sql_query(request: PromptRequest):
    schema = get_schema_description()
    sql = generate_sql_query(request.prompt, schema)
    return {"sql_query": sql}

@app.post("/get-dataframe")
def get_dataframe(request: PromptRequest):
    result = get_data_from_prompt(request.prompt)
    return result

@app.post("/fetch-employee-data-by-mobile")
def fetch_employee_data(request: RawSQLQuery):
    result = get_data_from_raw_query(text(request.raw_query))
    return result


@app.get("/fetch-db-schema")
def fetch_db_schema():
    schema = get_schema_description()
    return {"schema": schema}
