import requests
import json
from datetime import datetime
import logging
from config.settings import DATABASE_ID, NOTION_API_KEY

logger = logging.getLogger("NotionClient")

def create_notion_task(task_name, due_date=None):
    """Создает задачу в Notion через REST API (только по названию, без даты)"""
    try:
        url = "https://api.notion.com/v1/pages"
        
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        # Формируем данные для создания страницы (только название задачи)
        data = {
            "parent": {"database_id": DATABASE_ID},
            "properties": {
                "Name": {
                    "title": [
                        {
                            "text": {
                                "content": task_name
                            }
                        }
                    ]
                },
                "Status": {
                    "select": {
                        "name": "To Do"
                    }
                }
            }
        }
        
        # НЕ добавляем дату в Notion - только в календарь
        logger.info(f"Создаю задачу в Notion: '{task_name}'")
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            logger.info("✅ Задача успешно создана в Notion")
            return True
        else:
            logger.error(f"❌ Ошибка API Notion: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Ошибка при создании задачи в Notion: {e}", exc_info=True)
        return False