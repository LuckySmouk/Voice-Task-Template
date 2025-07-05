import os
import sys
import logging
import vosk
import time
import pyaudio
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SpeechRecognition")

# Путь к модели Vosk
MODEL_PATH = os.path.join("models", "ru", "vosk-model-small-ru-0.22")

def check_model():
    """Проверяет наличие модели Vosk"""
    if not os.path.exists(MODEL_PATH):
        logger.error(f"Модель не найдена в {MODEL_PATH}")
        print(f"❌ Модель распознавания речи не найдена в {MODEL_PATH}")
        print("Скачайте с https://alphacephei.com/vosk/models")
        print("и распакуйте в папку models/ru")
        return False
    return True

def listen_command():
    """Распознает речь локально через Vosk"""
    try:
        if not check_model():
            return None
            
        # Загрузка модели (один раз)
        if not hasattr(listen_command, 'model'):
            logger.info(f"Загрузка модели Vosk из {MODEL_PATH}")
            listen_command.model = vosk.Model(MODEL_PATH)
        
        recognizer = vosk.KaldiRecognizer(listen_command.model, 16000)
        
        p = pyaudio.PyAudio()
        
        # Поиск подходящего устройства ввода
        device_index = None
        for i in range(p.get_device_count()):
            dev_info = p.get_device_info_by_index(i)
            if int(dev_info.get('maxInputChannels', 0)) > 0:
                device_index = i
                break
        
        if device_index is None:
            logger.error("Не найдено устройство ввода")
            return None
        
        frames_per_buffer = 4096
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=frames_per_buffer,
            input_device_index=device_index
        )
        
        print("🎤 Говорите...")
        timeout = 35  # секунд
        start_time = time.time()
        
        while True:
            try:
                data = stream.read(frames_per_buffer, exception_on_overflow=False)
                
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    recognized_text = result.get("text", "")
                    if recognized_text:
                        stream.stop_stream()
                        stream.close()
                        p.terminate()
                        return recognized_text
                else:
                    partial = json.loads(recognizer.PartialResult())
                    if "partial" in partial and partial["partial"]:
                        print(f"Слушаю: {partial['partial']}", end='\r')
                
                # Проверка таймаута
                if time.time() - start_time > timeout:
                    print("\n⏰ Таймаут ожидания речи")
                    break
                    
            except OSError as e:
                if "Input overflowed" in str(e):
                    logger.warning("Переполнение буфера микрофона")
                    continue
                else:
                    raise
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        return None
        
    except Exception as e:
        logger.error(f"Ошибка распознавания речи: {e}", exc_info=True)
        return None
