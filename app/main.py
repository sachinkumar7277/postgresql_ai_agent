from fastapi import FastAPI
from sqlalchemy import text
from .schemas import PromptRequest, RawSQLQuery
from .services import (
    get_data_from_prompt,
    generate_sql_query,
    get_data_from_prompt_v2,
    get_all_tables_name,
    feed_schema_description
)
from .ai import (
    add_all_tables_as_prompt,
    feed_table_schema_with_ai
)

from .driver_manager import login_into_ai_and_save_cookies

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

@app.get("/login-into-chat-gpt")
def login_into_chat_gpt():
    return login_into_ai_and_save_cookies()

@app.get("/initiate-sql-ai-agent")
def fetch_db_schema():
    tables = get_all_tables_name()
    response = add_all_tables_as_prompt(tables)
    return response

@app.get("/load-db-tables-schema")
def fetch_db_tables_schema():
    schemas, table_schema_dict = feed_schema_description()
    return feed_table_schema_with_ai(schemas, table_schema_dict=table_schema_dict)

@app.post("/get-sql-query")
def get_sql_query(request: PromptRequest):
    print("######### Generate sql query triggered  $$$$$$$$$")
    sql = generate_sql_query(request.prompt)
    return sql

@app.post("/get-dataframe")
def get_dataframe(request: PromptRequest):
    result = get_data_from_prompt_v2(request.prompt)
    return result
