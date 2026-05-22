import sys
import logging
import structlog

def configure_logging(production_mode: bool = False):
    """
    Configures structlog bindings globally.
    If production_mode is True, it outputs pure structured JSON.
    Otherwise, it outputs clean, colorized text logs for your local terminal.
    """
    # 1. Clear out any existing standard logging handlers to avoid duplicate lines
    logging.basicConfig(handlers=[logging.StreamHandler(sys.stdout)], level=logging.INFO)
    
    # 2. Build the shared preprocessing chain
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    if production_mode:
        # Production output: Pure JSON objects
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Local development output: Colorized human-readable text
        processors.append(structlog.dev.ConsoleRenderer(colors=True, pad_level=False))

    structlog.configure(
        processors=processors,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )