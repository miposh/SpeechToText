import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, 'module_context'):
            record.module_context = record.name.split('.')[-1]
        return True


def get_logging_config() -> Dict[str, Any]:
    log_dir = Path("bot/logs")
    log_dir.mkdir(exist_ok=True)
    
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'detailed': {
                'format': (
                    '%(asctime)s | %(levelname)-8s | %(module_context)s | '
                    '%(funcName)s:%(lineno)d | %(message)s'
                ),
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'simple': {
                'format': '%(levelname)s | %(module_context)s | %(message)s'
            }
        },
        'filters': {
            'context_filter': {
                '()': ContextFilter,
            }
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'simple',
                'filters': ['context_filter'],
                'stream': sys.stdout
            },
            'file_debug': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'DEBUG',
                'formatter': 'detailed',
                'filters': ['context_filter'],
                'filename': 'bot/logs/debug.log',
                'maxBytes': 10485760,
                'backupCount': 5,
                'encoding': 'utf-8'
            },
            'file_error': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'ERROR',
                'formatter': 'detailed',
                'filters': ['context_filter'],
                'filename': 'bot/logs/error.log',
                'maxBytes': 10485760,
                'backupCount': 5,
                'encoding': 'utf-8'
            }
        },
        'loggers': {
            'bot': {
                'level': 'DEBUG',
                'handlers': ['console', 'file_debug', 'file_error'],
                'propagate': False
            },
            'handlers': {
                'level': 'DEBUG',
                'handlers': ['console', 'file_debug', 'file_error'],
                'propagate': False
            },
            'thread_save': {
                'level': 'DEBUG',
                'handlers': ['console', 'file_debug', 'file_error'],
                'propagate': False
            },
            'database': {
                'level': 'DEBUG',
                'handlers': ['console', 'file_debug', 'file_error'],
                'propagate': False
            },
            'middleware': {
                'level': 'DEBUG',
                'handlers': ['console', 'file_debug', 'file_error'],
                'propagate': False
            },
            'aiogram': {
                'level': 'WARNING',
                'handlers': ['console', 'file_error'],
                'propagate': False
            },
            'httpx': {
                'level': 'WARNING',
                'handlers': ['file_debug'],
                'propagate': False
            },
            'urllib3': {
                'level': 'WARNING',
                'handlers': ['file_debug'],
                'propagate': False
            }
        },
        'root': {
            'level': 'INFO',
            'handlers': ['console', 'file_error']
        }
    }


def setup_logging() -> None:
    config = get_logging_config()
    logging.config.dictConfig(config)
    
    logger = logging.getLogger('bot.config.logging_config')
    logger.info("Centralized logging configuration initialized")


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)