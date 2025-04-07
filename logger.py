import logging

# Базове налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Додатковий логгер для імпорту в інших модулях
logger = logging.getLogger("app")
