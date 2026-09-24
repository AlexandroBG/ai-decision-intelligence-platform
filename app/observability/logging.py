import logging

LOGGER_NAME = "decisionai"


def get_logger() -> logging.Logger:
    logger = logging.getLogger(LOGGER_NAME)

    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler()

        formatter = logging.Formatter("%(levelname)s %(name)s %(message)s")

        handler.setFormatter(formatter)

        logger.addHandler(handler)

    logger.propagate = False

    return logger
