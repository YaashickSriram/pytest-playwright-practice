import logging
from pathlib import Path

def get_logger():
    logger = logging.getLogger("framework")    
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter("\n %(asctime)s | %(levelname)s | %(name)s | %(message)s")
    log_dir = Path("test-results")
    log_dir.mkdir(parents=True, exist_ok=True)

    if not logger.handlers:

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        file_handler = logging.FileHandler(
            log_dir / "framework.log",
            encoding= "utf-8"
        )
        file_handler.setFormatter(formatter)

        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger




