from sqlalchemy import inspect
from sqlalchemy import text
import pandas as pd
from .database import engine, SessionLocal
from .ai import generate_sql_query
from .session_utils import (
    add_table_schema_into_session_memory,
    get_cached_tables_schemas
)

def get_all_tables_name():
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    return tables

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
        print("################################ Sending sql to db engine ###################################")
        print(text(sql))
        result = db.execute(text(sql))
        print("############################## QUERY EXECUTED #########################")
        print(result)
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


def get_data_from_prompt(prompt: str) -> dict:
    schema = get_schema_description()
    sql = generate_sql_query(prompt, schema)
    print("SQL: ", sql)

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

def get_data_from_prompt_v2(prompt: str) -> dict:
    sql = generate_sql_query(prompt)
    print("SQL: ", sql)

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


def feed_schema_description():
    inspector = inspect(engine)
    schema = ""
    table_schema_dict = {}
    cached_table_schema = get_cached_tables_schemas()
    for table in inspector.get_table_names():
        if cached_table_schema and cached_table_schema.get(table) and cached_table_schema.get(table)['sent_to_gpt']:
            continue
        columns = inspector.get_columns(table)
        col_desc = ", ".join(f"{col['name']} {col['type']}" for col in columns)
        table_schema = f"{table}({col_desc})\n"
        table_schema_dict[table] = {"schema":table_schema, "sent_to_gpt": True }
        schema += table_schema
        if len(schema) > 150:
            break
    return schema, table_schema_dict
