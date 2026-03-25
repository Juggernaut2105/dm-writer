import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Scraping settings
REQUEST_TIMEOUT = 15
SCRAPE_DELAY = 2  # seconds between requests
MAX_BODY_TEXT_LENGTH = 3000

# Gemini settings
GEMINI_MODEL = "gemini-2.0-flash"
