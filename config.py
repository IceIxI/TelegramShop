import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("BOT_TOKEN")
admin = int(os.getenv("ADMIN_ID"))

I18N_DOMAIN = 'testbot'
BASE_DIR = Path(__file__).parent