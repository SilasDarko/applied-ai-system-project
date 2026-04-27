"""
logger_setup.py  —  Centralised logging configuration and input guardrails.

Sets up both a file handler (logs/app.log) and a console handler so every
step of the pipeline is recorded for reliability evaluation.
"""

import logging
import os
import re
import sys
from pathlib import Path


def setup_logging(log_dir: str = "logs") -> None:
    """
    Configure the root logger with:
      - StreamHandler  → console (INFO and above)
      - FileHandler    → logs/app.log (DEBUG and above, append mode)
    Safe to call multiple times; duplicate handlers are avoided.
    """
    root = logging.getLogger()
    if root.handlers:
        return  # already configured

    root.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        "%(asctime)s  %(levelname)-8s  %(name)s  —  %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)
    root.addHandler(ch)

    # File
    Path(log_dir).mkdir(parents=True, exist_ok=True)
    log_path = os.path.join(log_dir, "app.log")
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)
    root.addHandler(fh)

    logging.getLogger(__name__).info("Logging initialised → %s", log_path)


# ---------------------------------------------------------------------------
# Input guardrails
# ---------------------------------------------------------------------------
MAX_INPUT_LENGTH  = 500
MIN_INPUT_LENGTH  = 3
_ALLOWED_PATTERN  = re.compile(r"^[\w\s',.\-!?()&]+$")

_guard_logger = logging.getLogger("guardrail")


def validate_input(text: str) -> tuple[bool, str]:
    """
    Validate user input before sending to the AI layer.

    Returns (is_valid: bool, cleaned_text_or_error_message: str).
    """
    if not isinstance(text, str):
        _guard_logger.warning("Input rejected: not a string (%s)", type(text))
        return False, "Input must be a text string."

    text = text.strip()

    if len(text) < MIN_INPUT_LENGTH:
        _guard_logger.warning("Input rejected: too short (%d chars)", len(text))
        return False, f"Please describe what you want to hear (at least {MIN_INPUT_LENGTH} characters)."

    if len(text) > MAX_INPUT_LENGTH:
        _guard_logger.warning("Input rejected: too long (%d chars)", len(text))
        return False, f"Input too long — please keep it under {MAX_INPUT_LENGTH} characters."

    if not _ALLOWED_PATTERN.match(text):
        _guard_logger.warning("Input rejected: disallowed characters")
        return False, "Input contains unsupported characters. Use plain text only."

    _guard_logger.debug("Input passed guardrail: %r", text[:60])
    return True, text