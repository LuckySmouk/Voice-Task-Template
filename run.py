import logging
from app.speech import listen_command
from app.command import parse_command
from app.notion import create_notion_task
from app.google_calendar import create_calendar_event

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("Main")

def check_microphone():
    """Проверяет доступность микрофона"""
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        stream.stop_stream()
        stream.close()
        p.terminate()
        return True
    except Exception as e:
        logger.error(f"Микрофон недоступен: {e}")
        return False

def main():
    print("🎙️ Голосовой бот для Notion и Google Calendar")
    
    if not check_microphone():
        print("❌ Микрофон не найден. Проверьте подключение и драйверы.")
        input("Нажмите Enter для выхода...")
        return
    
    print("✅ Микрофон доступен")
    print("Загрузка модели речи... Это может занять 10-15 секунд")

    try:
        while True:
            print("\nГотов к команде. Скажите 'стоп' для выхода.")
            print("Ожидание команды...")
            
            command = listen_command()
            if not command:
                continue
            
            if "стоп" in command.lower():
                print("👋 Программа завершена")
                break
            
            print(f"Вы сказали: {command}")
            
            parsed = parse_command(command)
            if not parsed or "task" not in parsed:
                print("⚠️ Не могу распознать команду. Попробуйте: 'Создай задачу название задачи на дату'")
                continue
            
            task_name = parsed["task"]
            due_date = parsed.get("due")
            
            print(f"📝 Задача: '{task_name}'")
            
            # Обработка разных типов дат
            start_date = None
            end_date = None
            
            if due_date:
                if isinstance(due_date, tuple):
                    start_date, end_date = due_date
                    if start_date and end_date:
                        print(f"📅 Период: с {start_date.strftime('%Y-%m-%d %H:%M')} по {end_date.strftime('%Y-%m-%d %H:%M')}")
                    else:
                        print("📅 Дата: не удалось распознать период")
                        due_date = None
                else:
                    start_date = due_date
                    print(f"📅 Дата: {due_date.strftime('%Y-%m-%d %H:%M')}")
            else:
                print("📅 Дата: не указана")
            
            # Создание задачи в Notion
            print("Создание задачи в Notion...")
            notion_success = create_notion_task(task_name, due_date)
            if notion_success:
                print("✅ Задача создана в Notion")
            else:
                print("❌ Ошибка при создании задачи в Notion")
            
            # Создание события в Google Calendar (если указана дата)
            calendar_success = False
            if start_date:
                print("Создание события в Google Calendar...")
                calendar_success = create_calendar_event(task_name, start_date)
                if calendar_success:
                    print("✅ Событие создано в Google Calendar")
                else:
                    print("❌ Ошибка при создании события в Google Calendar")
            else:
                print("⚠️ Дата не указана - событие в календаре не создано")
            
            # Итоговый статус
            if notion_success and (calendar_success or not start_date):
                print("✅ Операция успешно завершена!")
            elif notion_success and start_date and not calendar_success:
                print("⚠️ Задача создана в Notion, но не удалось создать событие в календаре")
            elif not notion_success:
                print("❌ Не удалось создать задачу в Notion")
            
    except KeyboardInterrupt:
        print("\n👋 Программа остановлена пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}", exc_info=True)
        print(f"❌ Критическая ошибка: {e}")

if __name__ == "__main__":
    main()