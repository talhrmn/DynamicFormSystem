import logging
import sys
from functools import lru_cache

import structlog

"""
Configure a custom logger.
"""


def setup_logging():
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO,
    )

    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.add_log_level,
            structlog.processors.dict_tracebacks,
            structlog.processors.JSONRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        cache_logger_on_first_use=True,
    )


@lru_cache
def get_logger():
    """
    Returns a cached singleton instance of a pre-configured logger.
    """
    return structlog.get_logger()
