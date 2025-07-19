from sqlalchemy import inspect
import pandas as pd
from .database import engine, SessionLocal
from .ai import generate_sql_query

def get_schema_description():
    inspector = inspect(engine)
    schema = ""
    for table in inspector.get_table_names():
        columns = inspector.get_columns(table)
        col_desc = ", ".join(f"{col['name']} {col['type']}" for col in columns)
        schema += f"{table}({col_desc})\n"
    return schema

def execute_query(sql: str) -> pd.DataFrame:
    db = SessionLocal()
    try:
        result = db.execute(sql)
        columns = result.keys()
        rows = result.fetchall()
        return pd.DataFrame(rows, columns=columns)
    finally:
        db.close()

def get_data_from_prompt(prompt: str) -> dict:
    schema = get_schema_description()
    sql = generate_sql_query(prompt, schema)
    df = execute_query(sql)
    return {
        "query": sql,
        "data": df.to_dict(orient="records")
    }
    
def get_data_from_raw_query(raw_query: str) -> dict:
    df = execute_query(raw_query)
    return {
        "query": raw_query,
        "data": df.to_dict(orient="records")
    }
