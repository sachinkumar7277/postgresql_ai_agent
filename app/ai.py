import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
api_key = os.getenv("OPEN_AI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def generate_sql_query(prompt: str, schema_description: str) -> str:
    full_prompt = f"Database schema:\n{schema_description}\n\nUser request: {prompt}\nSQL Query:"
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # Or use "gpt-4" if you have access
        messages=[
            {"role": "system", "content": "You are a helpful assistant that converts natural language prompts into SQL queries based on the given schema."},
            {"role": "user", "content": full_prompt}
        ],
        temperature=0.7,
        max_tokens=150
    )

    return response.choices[0].message.content.strip()
