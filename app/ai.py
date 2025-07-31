# API based AI Agent

# import os
# from openai import OpenAI
# from dotenv import load_dotenv

# # Load environment variables from .env
# load_dotenv()
# api_key = os.getenv("OPEN_AI_KEY")

# # Initialize OpenAI client
# client = OpenAI(api_key=api_key)


# def generate_sql_query(prompt: str, schema_description: str) -> str:
#     full_prompt = f"Database schema:\n{schema_description}\n\nUser request: {prompt}\nSQL Query:"
#     print(api_key)
#     print(full_prompt)
#     # response = client.chat.completions.create(
#     #     model="gpt-4.1",  # Or use "gpt-4" if you have access
#     #     messages=[
#     #         {"role": "system", "content": "You are a helpful assistant that converts natural language prompts into SQL queries based on the given schema."},
#     #         {"role": "user", "content": full_prompt}
#     #     ],
#     #     temperature=0.7,
#     #     max_tokens=150
#     # )
#     # print(full_prompt)
#     # print(response.data)
#     # print(response)
#     # print(response.choices)

#     # return response.choices[0].message.content.strip()



# Selenium Automation based AI Agent

from fastapi import FastAPI, HTTPException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .driver_manager import get_driver
from .session_utils import save_session_url, add_table_schema_into_session_memory
import time
import re

def slow_type(element, text, delay=0.01):
    for chunk in text.split('\n'):
        for char in chunk:
            element.send_keys(char)
            time.sleep(delay)  # simulate human typing
        element.send_keys(Keys.SHIFT, Keys.ENTER)  # new line (Shift+Enter in ProseMirror)


def clean_response(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def extract_sql_from_generated_response(response_text):
    match =  re.search(r"```sql(.*?)```", response_text, re.DOTALL | re.IGNORECASE)
    sql_only = match.group(1).strip() if match else "No SQL query found in response."
    return sql_only

def get_last_sql_code_block(driver):
    time.sleep(2)  # Give time for rendering

    # Get all code blocks with SQL language
    code_blocks = driver.find_elements(By.CSS_SELECTOR, "code.language-sql")

    if not code_blocks:
        print("No SQL code blocks found.")
        return ""

    # Pick the longest SQL block (to avoid SELECT * FROM roles; etc.)
    sql_code = max([cb.text.strip() for cb in code_blocks], key=len)
    print(f"SQL FETCHED FROM RESPONSE:\n{sql_code}")
    return sql_code

def ask_gpt(ai_prompt, table_schema_dict=None, user_prompt=None):
    print("######################################### Prompt reached to deriver  $$$$$$$$$$$$$$$$$$$$$$$$$$$$44")
    driver = get_driver()
    print("######################################### Deriver is ready to GO $$$$$$$$$$$$$$$$$$$$$$$$$$$$44")
    time.sleep(5)
    try:
        wait = WebDriverWait(driver, 70)
        print("⏳ Wait WebDriver instance created, waiting for textarea")

        # STEP 1: Wait for textarea
        try:
            time.sleep(7)
            input_div = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div#prompt-textarea")))
            print("✅ Found input div:", input_div)
        except Exception as e:
            print("❌ Failed to find textarea:", str(e))
            raise HTTPException(status_code=500, detail="Textarea not found or not clickable.")

        # STEP 2: Scroll into view
        try:
            driver.execute_script("arguments[0].scrollIntoView(true);", input_div)
            print("✅ Scrolled textarea into view")
            time.sleep(5)
        except Exception as e:
            print("❌ scrollIntoView failed:", str(e))
            raise HTTPException(status_code=500, detail=f"scrollIntoView error: {e}")

        # STEP 3: Click textarea
        try:
            input_div.click()
            print("✅ Clicked on textarea")
            time.sleep(1)
        except Exception as e:
            print("❌ Click failed:", str(e))
            raise HTTPException(status_code=500, detail=f"Textarea click failed: {e}")

        # STEP 4: Type prompt and submit
        try:
            # Usage:
            slow_type(input_div, ai_prompt)
            input_div.send_keys(Keys.ENTER)
            print("✅ Prompt sent")
        except Exception as e:
            print("❌ Failed to send prompt:", str(e))
            raise HTTPException(status_code=500, detail=f"Typing prompt failed: {e}")

        # STEP 5: Wait for response
        try:
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-message-author-role="assistant"]')))
            time.sleep(5)
            assistant_blocks = driver.find_elements(By.CSS_SELECTOR, '[data-message-author-role="assistant"]')

            if not assistant_blocks:
                raise Exception("Assistant blocks not found.")

            response_text = assistant_blocks[-1].text.strip()
            # response_text = clean_response(response_text)
            if not response_text:
                raise Exception("Assistant response is empty.")

            print("✅ Assistant response received")

        except Exception as e:
            print("❌ Failed to read response:", str(e))
            raise HTTPException(status_code=500, detail=f"Failed to read response: {e}")

        # step 6: Get sql query from sql code block from response
        try:
            time.sleep(5)
            code_element = driver.find_elements(By.CSS_SELECTOR, "code.language-sql")
            sql_code = code_element[-1].text.strip()
            print(f"SQL FETCHED FROM RESPONSE: {sql_code}")
            if table_schema_dict:
                add_table_schema_into_session_memory(table_schema_dict)
            return {"ai_agent_prompt":ai_prompt, "user_requested_prompt": user_prompt, "response": response_text, "sql_query": sql_code}
        except Exception as e:
            print("❌ No sql found or Failed to extract SQL:", e)
            add_table_schema_into_session_memory(table_schema_dict)
            return {"ai_agent_prompt":ai_prompt, "any_error_msg": e, "response": response_text, "sql_query": None}

    except Exception as e:
        print("❌ Fatal error:", str(e))
        raise HTTPException(status_code=500, detail=f"Fatal error: {str(e)}")

    finally:
        save_session_url(driver)

def add_all_tables_as_prompt(tables):
    prompt = f"You are a SQL Query generator, here is all my tables name {tables} please remember it, I will be sharing table schema later."
    return ask_gpt(prompt)
     
# def generate_sql_query(prompt: str, schema_description: str) -> str:
#     full_prompt = f"Database schema:\n{schema_description}\n\nUser request: {prompt}\nSQL Query:"
#     return ask_gpt(full_prompt, user_prompt=prompt)

def generate_sql_query(prompt: str) -> str:
    print("######################################### sending prompt to chat GPT  $$$$$$$$$$$$$$$$$$$$$$$$$$$$44")
    return ask_gpt(prompt, user_prompt=prompt)

def feed_table_schema_with_ai(schemas, table_schema_dict=None):
    prompt = f"You are a SQL Query generator, please remember this table schema : {schemas} we will request SQL Query based on these later."
    return ask_gpt(prompt, table_schema_dict=table_schema_dict)
