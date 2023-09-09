from os import getenv
from os.path import join, dirname
from dotenv import load_dotenv

# Create .env file path.
dotenv_path = join(dirname(__file__), ".env")

# Load file from the path.
load_dotenv(dotenv_path)

BOT_TOKEN = getenv("BOT_TOKEN", "")
URL_BASE = 'https://api.telegram.org/file/bot' + BOT_TOKEN + '/'
