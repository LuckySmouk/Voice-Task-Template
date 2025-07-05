from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime, timedelta
import pickle
import os
import pytz
import logging
from config.settings import GOOGLE_CALENDAR_CREDENTIALS, GOOGLE_CALENDAR_TOKEN, DEFAULT_EVENT_DURATION_HOURS, TIME_ZONE, GOOGLE_CALENDAR_ID

logger = logging.getLogger("GoogleCalendar")

def get_calendar_service():
    """Получает сервис Google Calendar"""
    creds = None
    
    try:
        if os.path.exists(GOOGLE_CALENDAR_TOKEN):
            with open(GOOGLE_CALENDAR_TOKEN, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Обновление токена Google Calendar...")
                creds.refresh(Request())
            else:
                logger.info("Требуется авторизация Google Calendar...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    GOOGLE_CALENDAR_CREDENTIALS, 
                    ['https://www.googleapis.com/auth/calendar.events']
                )
                creds = flow.run_local_server(port=0)
            
            with open(GOOGLE_CALENDAR_TOKEN, 'wb') as token:
                pickle.dump(creds, token)
        
        service = build('calendar', 'v3', credentials=creds, cache_discovery=False)
        logger.info("✅ Сервис Google Calendar успешно инициализирован")
        return service
        
    except Exception as e:
        logger.error(f"❌ Ошибка при инициализации сервиса Google Calendar: {e}", exc_info=True)
        return None

def create_calendar_event(task_name, due_date):
    """Создает событие в Google Calendar"""
    if not due_date:
        logger.error("❌ Не указана дата для события")
        return False
        
    try:
        service = get_calendar_service()
        if not service:
            logger.error("❌ Не удалось получить сервис Google Calendar")
            return False
            
        tz = pytz.timezone(TIME_ZONE)
        
        # Если дата не имеет часового пояса, назначаем TIME_ZONE
        if due_date.tzinfo is None:
            start_time = tz.localize(due_date)
        else:
            start_time = due_date
        
        end_time = start_time + timedelta(hours=DEFAULT_EVENT_DURATION_HOURS)
        
        event = {
            'summary': task_name,
            'description': f'Задача: {task_name}',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': TIME_ZONE,
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': TIME_ZONE,
            },
        }
        
        logger.info(f"Создаю событие в Google Calendar: '{task_name}' на {start_time}")
        
        created_event = service.events().insert(calendarId=GOOGLE_CALENDAR_ID, body=event).execute()
        
        logger.info(f'✅ Событие создано: {created_event.get("htmlLink", "без ссылки")}')
        return True
            
    except Exception as e:
        logger.error(f"❌ Ошибка при создании события: {e}", exc_info=True)
        return False
