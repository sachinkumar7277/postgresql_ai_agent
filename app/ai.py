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


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .cookies import get_cookies_from_file
import time
import re


def setup_driver():
    options = uc.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")
    
    # Optional: headless mode if needed
    # options.add_argument("--headless=new")

    driver = uc.Chrome(options=options)
    driver.get("https://chatgpt.com")
    time.sleep(5)
    
    
    # Add cookies
    cookies = get_cookies_from_file()
    
    for cookie in cookies:
        if cookie["name"].startswith("__Host-"):
            print(f"❌ Skipping HTTP-only or secure cookie: {cookie['name']}")
            continue
        try:
            if 'sameSite' in cookie:
                del cookie['sameSite']  # selenium sometimes errors on this
            driver.add_cookie(cookie)
        except Exception as e:
            print(f"❌ Failed to add cookie: {cookie}\nError: {e}")

    driver.get("https://chatgpt.com")  # Refresh after adding cookies
    time.sleep(5)
    return driver

def slow_type(element, text, delay=0.01):
    for chunk in text.split('\n'):
        for char in chunk:
            element.send_keys(char)
            time.sleep(delay)  # simulate human typing
        element.send_keys(Keys.SHIFT, Keys.ENTER)  # new line (Shift+Enter in ProseMirror)


def clean_response(text):
    # Remove common ChatGPT formatting artifacts
    # text = text.replace("sql", "")
    # text = text.replace("Copy", "")
    # text = text.replace("Edit", "")
    # Remove empty lines and trim
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

def extract_sql_from_generated_response(response_text):
    match =  re.search(r"```sql(.*?)```", response_text, re.DOTALL | re.IGNORECASE)
    sql_only = match.group(1).strip() if match else "No SQL query found in response."
    return sql_only

def ask_gpt(schema_description, prompt):
    driver = setup_driver()
    time.sleep(5)
    try:
        wait = WebDriverWait(driver, 70)
        print("⏳ Wait WebDriver instance created, waiting for textarea")

        # STEP 1: Wait for textarea
        try:
            time.sleep(10)
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
            full_prompt = f"Database schema:\n{schema_description}\n\nUser request: {prompt}\nSQL Query:"
            # Usage:
            slow_type(input_div, full_prompt)
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
            code_element = driver.find_element(By.CSS_SELECTOR, "code.language-sql")
            sql_code = code_element.text.strip()
            return {"requested_prompt": full_prompt, "ai_agent_prompt":full_prompt, "response": response_text, "sql_query": sql_code}
        except Exception as e:
            print("Failed to extract SQL:", e)
            return "No SQL query found in response."

    except Exception as e:
        print("❌ Fatal error:", str(e))
        raise HTTPException(status_code=500, detail=f"Fatal error: {str(e)}")

    finally:
        driver.quit()




def generate_sql_query(prompt: str, schema_description: str) -> str:
    return ask_gpt(schema_description, prompt)

    
