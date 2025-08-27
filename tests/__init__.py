"""
虚拟电厂测试包
VPP Tests Package

包含所有的测试脚本和测试工具
"""

# 测试包版本
__version__ = "1.0.0"

# 导出主要测试类和函数
from .test_vpp_system import TestVPPSystem, run_tests
from .test_scheduling_modes import TestVPPSchedulingModes

__all__ = [
    'TestVPPSystem',
    'TestVPPSchedulingModes', 
    'run_tests'
]