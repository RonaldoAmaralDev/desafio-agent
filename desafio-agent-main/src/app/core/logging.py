import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import json
from app.core.config import settings

LOG_DIR = Path(settings.LOG_DIR)
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "nivel": record.levelname,
            "logger": record.name,
            "mensagem": record.getMessage(),
            "arquivo": record.pathname,
            "linha": record.lineno,
        }
        if record.exc_info:
            log_record["erro"] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)

text_formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
json_formatter = JsonFormatter()

_console_handler = logging.StreamHandler()
_console_handler.setFormatter(text_formatter)
_console_handler.setLevel(settings.LOG_LEVEL)

_file_handler = RotatingFileHandler(
    str(LOG_FILE),
    maxBytes=settings.LOG_MAX_BYTES,
    backupCount=settings.LOG_BACKUP_COUNT,
    encoding="utf-8",
)
_file_handler.setFormatter(json_formatter)
_file_handler.setLevel(settings.LOG_LEVEL)

def configure_logging(force: bool = False) -> None:
    """Configura logging global"""
    root = logging.getLogger()
    if root.handlers and not force:
        return

    if force:
        for h in list(root.handlers):
            root.removeHandler(h)

    root.setLevel(settings.LOG_LEVEL)
    root.addHandler(_console_handler)
    root.addHandler(_file_handler)

def get_logger(name: str = None) -> logging.Logger:
    """Obtém um logger nomeado"""
    if name is None:
        name = "app"
    return logging.getLogger(name)
