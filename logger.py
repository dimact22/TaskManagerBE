import logging
import os
from logging.handlers import RotatingFileHandler

# Рівень логування із змінної середовища
log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Файл логів
log_file_path = os.getenv("LOG_FILE_PATH", "logs/app.log")
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

# Формат логів
log_format = logging.Formatter(
    "%(asctime)s [%(levelname)s] - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# FileHandler з ротацією за розміром
file_handler = RotatingFileHandler(log_file_path, maxBytes=1_000_000, backupCount=5)
file_handler.setFormatter(log_format)
file_handler.setLevel(log_level)

# ConsoleHandler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_format)
console_handler.setLevel(log_level)

# Отримання логгера
logger = logging.getLogger("app")
logger.setLevel(log_level)

# Уникаємо повторного додавання
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
