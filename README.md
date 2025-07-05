# Voice Task Template for Notion & Google Calendar
# Шаблон проекта «Голосовые задачи в Notion и Google Календаре»

> **Важно:** Это именно шаблон — вы можете его склонировать и адаптировать под свои нужды.

---

## Описание

Данный проект предоставляет основу для создания голосового помощника, который:

1. Принимает голосовую команду.
2. Преобразует речь в текст (модуль `speach.py` на основе моделей Vosk).
3. Анализирует текстовую команду и разделяет её на:
   - **Название задачи/события**  
   - **Дату** или **период дат** (если указано).
4. Создаёт задачу в Notion (модуль `noition.py`).
5. При наличии даты — создаёт событие в Google Календаре (модуль `google-calendary.py`).

---

## Основные возможности

- Распознавание речи на русском языке (Vosk).
- Парсинг команд на выделение названия и даты/периодов.
- Интеграция с Notion API для создания задач.
- Интеграция с Google Calendar API для создания событий.
- Готовая структура для быстрого старта и доработки.

---

## Требования

- Python ≥ 3.8
- Активные API‑ключи:
  - Notion Integration Token и ID целевой базы/страницы
  - Google OAuth2 Credentials для Calendar API
- Установленные модели Vosk (см. раздел **Модели распознавания речи**).

## Установка

1. Клонируйте репозиторий:
   ```
   git clone https://github.com/yourusername/voice-task-template.git
   cd voice-task-template
   ```
2. Создайте и активируйте виртуальное окружение:
  ```
  python3 -m venv .venv
  source .venv/bin/activate      # Linux/macOS
  .venv\Scripts\activate         # Windows
  ```
3. Установите зависимости:
   ```
   pip install -r requirements.txt
   ```

## Конфигурация

# Все настройки хранятся в файле config/settings.py:
```
NOTION_TOKEN = "secret_xxx"
NOTION_DATABASE_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

GOOGLE_CREDENTIALS_FILE = "path/to/credentials.json"
GOOGLE_TOKEN_FILE = "path/to/token.json"

# Путь к модели Vosk (укажите одну из папок из models/)
VOSK_MODEL_PATH = "../models/vosk-model-small-ru-0.22"
# или
VOSK_MODEL_PATH = "../models/vosk-model-ru-0.42"

```

## Запуск
```
python run.py
```

# При старте:

- speach.py слушает микрофон и переводит звук в текст.
- command.py парсит текст на «название» и «дату/период».
- noition.py и google-calendary.py создают задачи/события.


## Модели распознавания речи

- vosk-model-small-ru-0.22 — лёгкая модель (низкие требования к ресурсам, чуть ниже точность).
- vosk-model-ru-0.42 — большая модель (более точная, но требует больше ОЗУ/CPU).
- Скачайте обе или одну из моделей и размещайте папки в каталоге models/.
