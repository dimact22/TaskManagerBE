import logging
import os

log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()

log_level = getattr(logging, log_level_str, logging.INFO)

# Базове налаштування логування
logging.basicConfig(
    level=log_level,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Додатковий логгер для імпорту в інших модулях
logger = logging.getLogger("app")
