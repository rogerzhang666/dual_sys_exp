"""
配置加载模块
负责读取和解析YAML配置文件，为各个Agent提供配置信息
"""
import os  # 导入操作系统模块，用于处理文件路径
import yaml  # 导入YAML解析模块
from typing import Dict, Any  # 导入类型提示

class Config:
    def __init__(self, config_path: str = None):
        """初始化配置类
        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        # 如果未指定配置文件路径，则使用默认路径
        self.config_path = config_path or os.path.join(
            os.path.dirname(os.path.dirname(__file__)),  # 获取当前文件的上级目录
            'config',  # config目录
            'prompt_config.yaml'  # 配置文件名
        )
        # 加载配置文件内容
        self.config_data = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件
        Returns:
            Dict[str, Any]: 配置文件的内容，以字典形式返回
        """
        # 打开并读取YAML配置文件
        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)  # 解析YAML内容为Python字典

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """获取指定Agent的配置
        Args:
            agent_name: Agent的名称（如'dispatcher', 'sys1', 'sys2'）
        Returns:
            Dict[str, Any]: Agent的配置信息
        """
        # 从配置中获取指定Agent的配置，如果不存在则返回空字典
        return self.config_data.get('agents', {}).get(agent_name, {})
