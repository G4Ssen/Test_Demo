"""
Structured logger using Loguru.
All services import `logger` from this module.
"""
import sys
from loguru import logger

logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> — <level>{message}</level>",
    level="INFO",
    colorize=True,
)
logger.add(
    "logs/pipeline.log",
    rotation="10 MB",
    retention="7 days",
    format="{time} | {level} | {name}:{function}:{line} — {message}",
    level="DEBUG",
)

__all__ = ["logger"]
