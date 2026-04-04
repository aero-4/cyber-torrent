from logging.config import dictConfig

LOG_FORMAT = (
    "[%(asctime)s] %(levelname)-8s %(name)s "
    "%(module)s:%(lineno)d %(funcName)s -> %(message)s "
    "%(error_code)s %(status_code)s "
    "%(path)s %(method)s %(details)s "
)


def setup_logging(level: str = "INFO") -> None:
    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "()": "logging.Formatter",
                    "format": LOG_FORMAT,
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                    "defaults": {
                        "error_code": "",
                        "status_code": "",
                        "path": "",
                        "method": "",
                        "details": "",
                    },
                },
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "stream": "ext://sys.stdout",
                    "formatter": "default",
                },
            },
            "loggers": {
                "": {
                    "handlers": ["console"],
                    "level": level,
                },
                "uvicorn": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
                "uvicorn.error": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
                "uvicorn.access": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
                "fastapi": {
                    "handlers": ["console"],
                    "level": level,
                    "propagate": False,
                },
            },
        }
    )
