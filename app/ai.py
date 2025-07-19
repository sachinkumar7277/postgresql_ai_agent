import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_sql_query(prompt: str, schema_description: str) -> str:
    full_prompt = f"Database schema:\n{schema_description}\n\nUser request: {prompt}\nSQL Query:"
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=full_prompt,
        max_tokens=200,
        temperature=0,
    )
    return response.choices[0].text.strip()
