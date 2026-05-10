"""
JARVIS Logger
=============
Centralized loguru-based logging system.
Outputs to console (rich formatted) and rotating file logs.
"""

from __future__ import annotations

import sys
import os
from pathlib import Path
from loguru import logger
from shared.constants import LOG_DIR, LOG_LEVEL, LOG_FORMAT, LOG_MAX_SIZE, LOG_RETENTION


def setup_logger(name: str = "jarvis") -> None:
    """
    Configure the global loguru logger.
    Call once at application startup.
    
    Args:
        name: Log file prefix name (e.g. 'backend', 'desktop')
    """
    # Remove default handler
    logger.remove()

    # ── Console handler (colorized) ───────────────────────────────────────────
    logger.add(
        sys.stderr,
        level=LOG_LEVEL,
        format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
        colorize=True,
        backtrace=True,
        diagnose=True,
    )

    # ── File handler (rotating) ───────────────────────────────────────────────
    log_dir = Path(LOG_DIR)
    log_dir.mkdir(exist_ok=True)

    logger.add(
        log_dir / f"{name}_{{time:YYYY-MM-DD}}.log",
        level=LOG_LEVEL,
        format=LOG_FORMAT,
        rotation=LOG_MAX_SIZE,
        retention=LOG_RETENTION,
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True,   # Thread-safe async-safe writing
    )

    logger.info(f"Logger initialized | name={name} | level={LOG_LEVEL}")


def get_logger(module_name: str):
    """
    Get a logger bound to a specific module name.
    
    Usage:
        log = get_logger(__name__)
        log.info("Hello from this module")
    """
    return logger.bind(name=module_name)
