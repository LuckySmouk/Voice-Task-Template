import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()

# Настройки Notion
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
DATABASE_ID = os.getenv("DATABASE_ID")

# Настройки Google Calendar
raw_credentials = os.getenv("GOOGLE_CALENDAR_CREDENTIALS", "").strip()
 # если по какой-то ошибке попала строка вида os.getenv(...), принудительно сбросим
if raw_credentials.startswith("os.getenv"):
     GOOGLE_CALENDAR_CREDENTIALS = "credentials.json"
else:
     GOOGLE_CALENDAR_CREDENTIALS = raw_credentials or "credentials.json"
     
 # Файл токена для Google Calendar
raw_token = os.getenv("GOOGLE_CALENDAR_TOKEN", "").strip()
 # если по какой-то ошибке в переменную попала сама конструкция os.getenv(…), сбрасываем на дефолт
if raw_token.startswith("os.getenv"):
     GOOGLE_CALENDAR_TOKEN = "token.pickle"
else:
     GOOGLE_CALENDAR_TOKEN = raw_token or "token.pickle"
     

# ID календаря для Google Calendar
raw_id = os.getenv("GOOGLE_CALENDAR_ID", "").strip()
if raw_id.startswith("os.getenv"):
     GOOGLE_CALENDAR_ID = "primary"
else:
    GOOGLE_CALENDAR_ID = raw_id or "primary"

# Общие настройки
TIME_ZONE = os.getenv("TIME_ZONE", "Europe/Moscow")
DEFAULT_EVENT_DURATION_HOURS = int(os.getenv("DEFAULT_EVENT_DURATION_HOURS", "1"))

# Проверка обязательных переменных
if not NOTION_API_KEY:
    raise ValueError("NOTION_API_KEY не установлен в переменных окружения")
if not DATABASE_ID:
    raise ValueError("DATABASE_ID не установлен в переменных окружения")