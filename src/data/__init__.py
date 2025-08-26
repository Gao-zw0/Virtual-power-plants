"""
数据生成模块
Data Generation Module

负责生成虚拟电厂优化所需的各类数据：
- 负荷需求数据
- 可再生能源出力数据
- 电价数据
"""

from .data_generator import VPPDataGenerator

__all__ = ['VPPDataGenerator']