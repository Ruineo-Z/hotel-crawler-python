import sys
import os
from pathlib import Path
from loguru import logger

# 确保日志目录存在
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 移除默认处理器
logger.remove()

# 设置上海时区 (UTC+8)
SHANGHAI_TIMEZONE = "Asia/Shanghai"

# 文件日志配置
logger.add(
    "logs/app.log",  # 日志文件路径
    rotation="10 MB",  # 日志大小达到10MB时轮转
    retention="1 week",  # 保留1周的日志
    compression="zip",  # 压缩轮转的日志
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",  # 日志格式
    level="INFO",  # 日志级别
    enqueue=True,  # 异步写入
    encoding="utf-8",  # 使用utf-8编码
    diagnose=True,  # 启用诊断信息（更详细的回溯）
)

# 控制台日志配置
logger.add(
    sink=sys.stderr,
    format="{time:YYYY-MM-DD HH:mm:ss} | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO",
    colorize=True,  # 彩色输出
    diagnose=True,  # 启用诊断信息
)

# 设置全局时区
os.environ["TZ"] = SHANGHAI_TIMEZONE


def get_logger(name=None):
    """
    获取带有上下文信息的logger

    Args:
        name: 可选的logger名称，通常使用模块名

    Returns:
        配置好的logger实例
    """
    if name:
        return logger.bind(name=name)
    return logger


# 导出logger
__all__ = ["logger", "get_logger"]
