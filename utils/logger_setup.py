"""
日志设置模块

配置系统日志记录
"""

import sys
from pathlib import Path
from loguru import logger
from typing import Dict, Any


def setup_logger(config: Dict[str, Any]):
    """设置日志配置"""
    
    # 移除默认处理器
    logger.remove()
    
    # 获取配置
    level = config.get('level', 'INFO')
    format_str = config.get('format', '{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}')
    rotation = config.get('rotation', '1 day')
    retention = config.get('retention', '7 days')
    
    # 控制台输出
    logger.add(
        sys.stderr,
        level=level,
        format=format_str,
        colorize=True
    )
    
    # 确保日志目录存在
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 文件输出
    logger.add(
        log_dir / "auto_cursor_agent.log",
        level=level,
        format=format_str,
        rotation=rotation,
        retention=retention,
        encoding="utf-8"
    )
    
    # 错误日志单独记录
    logger.add(
        log_dir / "error.log",
        level="ERROR",
        format=format_str,
        rotation=rotation,
        retention=retention,
        encoding="utf-8"
    )
    
    logger.success("日志系统已配置")

