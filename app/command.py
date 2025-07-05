import re
import dateparser
from datetime import datetime
import pytz
import logging

logger = logging.getLogger("CommandParser")

def parse_command(command):
    """Парсит голосовую команду и извлекает название задачи и дату"""
    if not command:
        return None
    
    command_lower = command.lower().strip()
    
    # Проверяем наличие ключевых слов для создания задачи
    if not any(word in command_lower for word in ["задач", "событие", "запись", "создай"]):
        return None
    
    # Извлекаем название задачи и дату
    task_name, date_part = extract_task_and_date(command)
    if not task_name:
        return None
    
    # Парсим дату
    parsed_date = parse_date(date_part) if date_part else None
    
    logger.info(f"Извлечено - Задача: '{task_name}', Дата: '{date_part}' -> {parsed_date}")
    
    return {
        "task": task_name,
        "due": parsed_date
    }

def extract_task_and_date(command):
    """Извлекает название задачи и дату из команды"""
    command_lower = command.lower().strip()
    
    # Сначала ищем задачу в кавычках
    quote_match = re.search(r"['\"]([^'\"]+)['\"]", command)
    if quote_match:
        task_name = quote_match.group(1)
        date_part = re.sub(r"['\"][^'\"]*['\"]", "", command_lower).strip()
        return task_name, clean_date_part(date_part)
    
    # Поддержка диапазонов дат "с ... по ..."
    range_match = re.search(r"(?:создай|запиши)\s+(?:задачу|событие)\s+(.+?)\s+с\s+(.+?)\s+по\s+(.+)", command_lower)
    if range_match:
        task_name = clean_task_name(range_match.group(1))
        start_date = range_match.group(2)
        end_date = range_match.group(3)
        return task_name, f"{start_date} - {end_date}"
    
    # Используем разделители "на", "к", "до"
    date_separators = [r"\s+на\s+дату\s+", r"\s+на\s+", r"\s+к\s+", r"\s+до\s+"]
    for separator in date_separators:
        # Ищем паттерн: команда + задача + разделитель + дата
        pattern = rf"(?:создай|запиши)\s+(?:задачу|событие|запись)\s+(.+?){separator}(.+)"
        match = re.search(pattern, command_lower)
        if match:
            task_name = clean_task_name(match.group(1))
            date_part = match.group(2)
            return task_name, clean_date_part(date_part)
    
    # Поиск даты в конце команды без разделителя
    date_pattern = r"(?:создай|запиши)\s+(?:задачу|событие|запись)\s+(.+?)\s+(\b(?:первое|второе|третье|четвертое|пятое|шестое|седьмое|восьмое|девятое|десятое|одиннадцатое|двенадцатое|тринадцатое|четырнадцатое|пятнадцатое|шестнадцатое|семнадцатое|восемнадцатое|девятнадцатое|двадцатое|двадцать первое|двадцать второе|двадцать третье|двадцать четвертое|двадцать пятое|двадцать шестое|двадцать седьмое|двадцать восьмое|двадцать девятое|тридцатое|тридцать первое|января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\b.*)"
    match = re.search(date_pattern, command_lower, re.IGNORECASE)
    if match:
        task_name = clean_task_name(match.group(1))
        date_part = match.group(2)
        return task_name, clean_date_part(date_part)
    
    # Извлечение только задачи без даты
    task_only_patterns = [
        r"(?:создай|запиши)\s+(?:задачу|событие|запись)\s+(.+)",
        r"(?:задачу|событие|запись)\s+(.+?)(?:\s+(?:на|к|до)|$)"
    ]
    for pattern in task_only_patterns:
        match = re.search(pattern, command_lower)
        if match:
            task_name = clean_task_name(match.group(1))
            return task_name, None
    
    return None, None

def clean_task_name(task_name):
    """Очищает название задачи от лишних слов"""
    if not task_name:
        return None
    
    # Убираем служебные слова из начала
    task_name = re.sub(r'^\s*(задачу|событие|запись)\s+', '', task_name).strip()
    
    # Убираем предлоги и служебные слова
    task_name = re.sub(r'\s+(на|к|в|до|с|по|для|от|из|под|над|между|перед|после|через|за|при|без|против|среди|вокруг|около|вместо|кроме|сверх|внутри|снаружи|вдоль|поперек|напротив|позади|впереди|слева|справа|сверху|снизу|внизу|вверху|дату|время)\s+', ' ', task_name).strip()
    
    # Убираем лишние пробелы
    task_name = re.sub(r'\s+', ' ', task_name).strip()
    
    return task_name if task_name else None

def clean_date_part(date_part):
    """Очищает строку с датой от лишних слов"""
    if not date_part:
        return None
    
    # Убираем команды создания и служебные слова
    date_part = re.sub(r'\b(создай|задачу|событие|запись|дату|время)\b', '', date_part).strip()
    
    # Убираем лишние пробелы
    date_part = re.sub(r'\s+', ' ', date_part).strip()
    
    return date_part if date_part else None

def parse_date(date_str):
    """Парсит дату или диапазон дат из строки"""
    if not date_str:
        return None
    
    date_str = preprocess_date(date_str)
    
    try:
        # Обработка диапазонов дат
        if "-" in date_str or "—" in date_str:
            parts = re.split(r"\s*[-—]\s*", date_str)
            if len(parts) == 2:
                start = dateparser.parse(parts[0], languages=["ru"], settings={"TIMEZONE": "Europe/Moscow", "RETURN_AS_TIMEZONE_AWARE": True})
                end = dateparser.parse(parts[1], languages=["ru"], settings={"TIMEZONE": "Europe/Moscow", "RETURN_AS_TIMEZONE_AWARE": True})
                if start and end:
                    return (start, end)
        
        # Обработка одиночной даты
        parsed = dateparser.parse(date_str, languages=["ru"], settings={"TIMEZONE": "Europe/Moscow", "RETURN_AS_TIMEZONE_AWARE": True})
        if parsed:
            return parsed
        
        return None
        
    except Exception as e:
        logger.error(f"Ошибка парсинга даты '{date_str}': {e}")
        return None

def preprocess_date(date_str):
    """Добавляет текущий год для относительных дат и нормализует формат"""
    date_str = date_str.lower()
    
    # Замена числительных на цифры
    replacements = {
        "первое": "1", "второе": "2", "третье": "3", "четвертое": "4", "пятое": "5",
        "шестое": "6", "седьмое": "7", "восьмое": "8", "девятое": "9", "десятое": "10",
        "одиннадцатое": "11", "двенадцатое": "12", "тринадцатое": "13", "четырнадцатое": "14",
        "пятнадцатое": "15", "шестнадцатое": "16", "семнадцатое": "17", "восемнадцатое": "18",
        "девятнадцатое": "19", "двадцатое": "20", "двадцать первое": "21", "двадцать второе": "22",
        "двадцать третье": "23", "двадцать четвертое": "24", "двадцать пятое": "25", "двадцать шестое": "26",
        "двадцать седьмое": "27", "двадцать восьмое": "28", "двадцать девятое": "29", "тридцатое": "30",
        "тридцать первое": "31",
        "двенадцатая": "12", "двенадцатое": "12", "двенадцатый": "12"
    }
    
    for word, num in replacements.items():
        date_str = date_str.replace(word, num)
    
    # Добавление года для относительных дат
    current_year = datetime.now().year
    if re.search(r"\b(?:января|февраля|марта|апреля|мая|июня|июля|августа|сентября|октября|ноября|декабря)\b", date_str):
        if str(current_year) not in date_str and str(current_year % 100) not in date_str:
            date_str += f" {current_year}"
    
    return date_str.strip()