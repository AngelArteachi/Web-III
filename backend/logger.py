import os
import sys
import logging
from loki_logger_handler.loki_logger_handler import LokiLoggerHandler


def setup_logger():
    """
    Configura y retorna un logger personalizado con handlers para consola y Loki.

    Returns:
        logging.Logger: Logger configurado con handlers de consola y Loki
    """
    # Crear logger
    logger = logging.getLogger("fastapi_app ")

    # Obtener nivel de log desde variable de entorno
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    if log_level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    # Evitar duplicación de handlers si ya están configurados
    if logger.handlers :
        return logger

    # Crear handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logger.level)

    # Formato para los logs
    formatter = logging.Formatter(
        "%(levelname)s: %(asctime)s - %(name)s - %(message)s "
    )
    console_handler.setFormatter(formatter)

    # Crear handler para Loki
    loki_handler = LokiLoggerHandler(
        url="http://loki:3100/loki/api/v1/push",
        labels={"application": "FastAPI", "environment": "production"},
        label_keys={},
        timeout=10 ,
    )

    # Agregar handlers al logger
    logger.addHandler(loki_handler)
    logger.addHandler(console_handler)

    logger.info("Logger initialized successfully")

    return logger


# Crear instancia global del logger
logger = setup_logger()
