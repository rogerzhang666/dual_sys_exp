"""
配置加载模块
"""
import os
import yaml
from typing import Dict, Any

class Config:
    def __init__(self, config_path: str = None):
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'config',
            'prompt_config.yaml'
        )
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """获取指定Agent的配置"""
        return self.config_data.get('agents', {}).get(agent_name, {})
