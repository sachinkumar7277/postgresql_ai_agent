from sqlalchemy import inspect
from sqlalchemy import text
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
# Only fetch all rows to get dataframe 
# def execute_query(sql: str) -> pd.DataFrame:
#     db = SessionLocal()
#     try:
#         result = db.execute(text(sql))
#         columns = result.keys()
#         rows = result.fetchall()
#         return pd.DataFrame(rows, columns=columns)
#     finally:
#         db.close()

# Fetch as well as execute insert delete update etc operations
def execute_query(sql: str) -> pd.DataFrame | str:
    db = SessionLocal()
    try:
        result = db.execute(text(sql))
        # Detect if it's a SELECT query
        if sql.strip().lower().startswith("select"):
            columns = result.keys()
            rows = result.fetchall()
            return pd.DataFrame(rows, columns=columns)
        else:
            db.commit()
            return "Query executed successfully."
    except Exception as e:
        db.rollback()
        return f"Error: {e}"
    finally:
        db.close()


# def get_data_from_prompt(prompt: str) -> dict:
#     schema = get_schema_description()
#     sql = generate_sql_query(prompt, schema)
    
#     df = execute_query(sql['sql_query'])
#     return {
#         "query": sql,
#         "data": df.to_dict(orient="records")
#     }


def get_data_from_prompt(prompt: str) -> dict:
    schema = get_schema_description()
    sql = generate_sql_query(prompt, schema)

    df_or_msg = execute_query(sql['sql_query'])
    print("df_or_msg :", df_or_msg)

    if isinstance(df_or_msg, pd.DataFrame):
        return {
            "query": sql,
            "data": df_or_msg.to_dict(orient="records")
        }
    else:
        # It's a string message like "Query executed successfully."
        return {
            "query": sql,
            "message": df_or_msg,
            "data": []
        }

    
# def get_data_from_raw_query(raw_query: str) -> dict:
#     df = execute_query(raw_query)
#     return {
#         "query": raw_query,
#         "data": df.to_dict(orient="records")
#     }


def get_data_from_raw_query(raw_query: str) -> dict:
    df_or_msg = execute_query(raw_query)

    if isinstance(df_or_msg, pd.DataFrame):
        return {
            "query": raw_query,
            "data": df_or_msg.to_dict(orient="records")
        }
    else:
        return {
            "query": raw_query,
            "message": df_or_msg,
            "data": []
        }
