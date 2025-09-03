# app/core/logger.py
import sys
import logging
from loguru import logger

logger_format = (
    "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "{process.name} | "
    "{thread.name} | "
    "<cyan>{module}</cyan>.<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{level}</level> | <level>{message}</level>"
)

LOG_FILE = "logs/loguruLogs/{time:YYYY-MM-DD}.log"

def setup_logger(
    level: str = "DEBUG",
    format_type: str | None = None,
    debug_file: str = None,
    error_file: str = None,
    info_file: str = None,
):
    logger.remove()  # 移除默认 handler

    format_type = format_type or logger_format

    # 控制台输出
    logger.add(sys.stdout, level=level, format=format_type, colorize=True, enqueue=True)

    # 日志文件（按日切割）
    logger.add(LOG_FILE,
               level="DEBUG",
               format=format_type,
               rotation="00:00",
               retention="7 days",
               enqueue=True)

    # 分级输出可选
    if debug_file:
        logger.add(debug_file, level="DEBUG", format=format_type, enqueue=True)
    if error_file:
        logger.add(error_file, level="ERROR", format=format_type, enqueue=True)
    if info_file:
        logger.add(info_file, level="INFO", format=format_type, enqueue=True)

    # 标准库 logging 接入
    class InterceptHandler(logging.Handler):
        def emit(self, record):
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = record.levelno
            frame, depth = logging.currentframe(), 2
            while frame.f_code.co_filename == logging.__file__:
                frame = frame.f_back
                depth += 1
            logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

    logging.basicConfig(handlers=[InterceptHandler()], level=level)

    return logger


# 初始化 logger（自动接管 logging）
self_logging = setup_logger(level="INFO")
