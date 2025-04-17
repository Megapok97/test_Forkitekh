import logging
import logging.handlers
import os


def setup_logger(name: str) -> logging.Logger:
    """
    Configures and returns a logger with console and rotating file handlers.

    Args:
        name (str): Name of the logger (typically the module name).

    Returns:
        logging.Logger: Configured logger instance with INFO level, console output, and rotating file logs.

    Notes:
        - Logs are written to 'logs/app.log' with a maximum size of 10MB and up to 5 backup files.
        - If the logger already has handlers, it is returned as is to prevent duplicate handlers.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        log_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(log_format)
        logger.addHandler(console_handler)

        os.makedirs("logs", exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            "logs/app.log", maxBytes=10_000_000, backupCount=5
        )
        file_handler.setFormatter(log_format)
        logger.addHandler(file_handler)

    return logger
