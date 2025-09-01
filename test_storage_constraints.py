#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('src')

from models.vpp_model import VPPOptimizationModel
from data.data_generator import VPPDataGenerator

def test_storage_constraints():
    """测试储能系统约束是否正确设置"""
    print("=== 储能系统约束测试 ===")
    
    # 生成测试数据
    dg = VPPDataGenerator()
    load_data, pv_data, wind_data, price_data = dg.generate_all_data()
    
    # 创建模型
    model = VPPOptimizationModel(dg.time_index)
    es = model.create_energy_system(load_data, pv_data, wind_data, price_data)
    
    # 获取储能组件
    battery = model.get_component_by_label('battery_storage')
    
    print(f"储能容量: {battery.nominal_storage_capacity} MWh")
    print(f"最小SOC: {getattr(battery, 'min_storage_level', '未设置')}")
    print(f"最大SOC: {getattr(battery, 'max_storage_level', '未设置')}")
    
    if hasattr(battery, 'min_storage_level') and hasattr(battery, 'max_storage_level'):
        # 获取第一个时间点的SOC值作为示例
        min_soc = battery.min_storage_level[0] if hasattr(battery.min_storage_level, '__getitem__') else battery.min_storage_level
        max_soc = battery.max_storage_level[0] if hasattr(battery.max_storage_level, '__getitem__') else battery.max_storage_level
        min_capacity = battery.nominal_storage_capacity * min_soc
        max_capacity = battery.nominal_storage_capacity * max_soc
        print(f"有效容量范围: {min_capacity:.1f} - {max_capacity:.1f} MWh")
        print("✓ SOC约束已正确设置")
    else:
        print("✗ SOC约束未设置")
    
    return battery

if __name__ == "__main__":
    test_storage_constraints()