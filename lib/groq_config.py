from dotenv import load_dotenv
import os

# Replace with your OpenAI API key

load_dotenv('../')

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

export GROQ_API_KEY = GROQ_API_KEY