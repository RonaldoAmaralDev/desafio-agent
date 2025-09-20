import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

LOG_DIR = Path(os.getenv("LOG_DIR", "/tmp/desafio-agent-logs"))
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_FILE = LOG_DIR / "app.log"

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Formatter used for console and file handlers
_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

# Console handler (stdout)
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(_formatter)
_console_handler.setLevel(LOG_LEVEL)

# Rotating file handler
_file_handler = RotatingFileHandler(str(LOG_FILE), maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8")
_file_handler.setFormatter(_formatter)
_file_handler.setLevel(LOG_LEVEL)

def configure_logging(force: bool = False) -> None:
    root = logging.getLogger()
    if root.handlers and not force:
        return

    if force:
        for h in list(root.handlers):
            root.removeHandler(h)

    root.setLevel(LOG_LEVEL)
    root.addHandler(_console_handler)
    root.addHandler(_file_handler)

def get_logger(name: str = None) -> logging.Logger:
    if name is None:
        name = "app"
    return logging.getLogger(name)
