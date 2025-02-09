import os
from dotenv import load_dotenv

load_dotenv()

mongo_uri: str = os.environ.get("MONGO_URI")
redis_uri: str = os.environ.get("REDIS_URI")
redis_password: str = os.environ.get("REDIS_PASSWORD")