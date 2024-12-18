import json
import logging
import os
from datetime import datetime
import structlog


class CustomJSONRenderer:
    def __call__(self, logger, name, event_dict):
        json_output = json.dumps(event_dict, indent=4)
        return f"{json_output}\n\n\n\n{'=' * 120}\n\n\n\n"


class AttackLogger:
    def __init__(self):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f'./log/{timestamp}.log'

        os.makedirs('./log', exist_ok=True)
        file_handler = logging.FileHandler(log_filename)
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(level=logging.INFO, handlers=[file_handler])

        structlog.configure(
            processors=[
                CustomJSONRenderer(),
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
        )

        self.logger = structlog.get_logger()

    def log(self, **kwargs):
        self.logger.info("attack log",
                         **kwargs)
