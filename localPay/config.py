import os

from dotenv import load_dotenv

load_dotenv()

connection_string = os.getenv("CONNECTION_STRING")
secret_key = os.getenv("SECRET_KEY")
algorithm = os.getenv("ALGORITHM")
access_token_expires_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
redis_url = os.getenv("REDIS_URL")
refresh_token_expire_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))