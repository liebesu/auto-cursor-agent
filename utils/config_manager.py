"""
配置管理器

负责加载和管理系统配置
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from loguru import logger


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = None):
        """初始化配置管理器"""
        self.config_path = config_path or "config/config.yaml"
        self.config = self._load_config()
        logger.info(f"配置已加载: {self.config_path}")
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            logger.warning(f"配置文件不存在: {config_file}")
            return self._get_default_config()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            logger.success(f"配置文件加载成功: {config_file}")
            return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "ai_models": {
                "openai": {
                    "model": "gpt-4",
                    "max_tokens": 4000,
                    "temperature": 0.7
                }
            },
            "cursor": {
                "executable_path": "/Applications/Cursor.app/Contents/MacOS/Cursor",
                "wait_timeout": 30
            },
            "monitoring": {
                "check_interval": 30,
                "quality_threshold": 0.8
            },
            "logging": {
                "level": "INFO"
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """获取配置"""
        return self.config
    
    def get(self, key: str, default=None):
        """获取配置项"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

