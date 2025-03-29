"""
配置管理模块
负责加载和解析配置文件
"""
import os
from typing import Dict, Any, Optional
import yaml

class Config:
    """配置管理类：负责加载和解析配置文件"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初始化配置管理器
        Args:
            config_path: 可选的配置文件路径，如果不提供则使用默认路径
        """
        # 如果没有提供配置文件路径，使用默认路径
        if config_path is None:
            # 获取当前文件所在目录
            current_dir = os.path.dirname(os.path.abspath(__file__))
            # 构建默认配置文件路径
            config_path = os.path.join(os.path.dirname(current_dir), 'config', 'prompt_config.yaml')
            
        # 加载配置文件
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
            
    def get_agents_config(self) -> Dict[str, Any]:
        """获取所有Agent的配置
        Returns:
            Dict[str, Any]: 包含所有Agent配置的字典
        """
        return self.config.get('agents', {})
