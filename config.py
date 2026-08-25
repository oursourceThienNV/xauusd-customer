import os
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://180.93.144.96:8084"
)

APP_VERSION = os.getenv(
    "APP_VERSION",
    "1.2"
)