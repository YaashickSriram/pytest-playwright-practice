import logging

def get_logger():
    logger = logging.getLogger("framework")

    logger.setLevel(logging.INFO)

    if not logger.handlers:
        console_handler = logging.StreamHandler()

        formatter = logging.Formatter("\n %(asctime)s | %(levelname)s | %(name)s | %(message)s")
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger




