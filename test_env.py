from dotenv import load_dotenv
import os

# Attempt to load .env from the current directory
loaded = load_dotenv() 
print(f".env file loaded: {loaded}")

secret_key = os.getenv("SECRET_KEY")
db_url = os.getenv("DATABASE_URL")

print(f"SECRET_KEY from env: {secret_key}")
print(f"DATABASE_URL from env: {db_url}")

if secret_key:
    print("SECRET_KEY is found!")
else:
    print("SECRET_KEY is NOT found.")
