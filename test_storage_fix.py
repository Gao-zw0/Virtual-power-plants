#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append('src')

from models.vpp_model import VPPOptimizationModel
from data.data_generator import VPPDataGenerator
from solvers.optimization_solver import OptimizationSolver
from models.scheduling_modes import VPPSchedulingManager, SchedulingMode

def test_storage_fix():
    """测试储能系统约束修复是否有效"""
    print("=== 储能系统约束修复测试 ===")
    
    # 生成测试数据
    dg = VPPDataGenerator()
    load_data, pv_data, wind_data, price_data = dg.generate_all_data()
    
    # 创建调度模式管理器
    mode_manager = VPPSchedulingManager()
    
    # 创建优化模型（使用storage_only模式）
    model = mode_manager.create_optimized_model(SchedulingMode.STORAGE_ONLY, dg.time_index)
    
    # 创建能源系统
    energy_system = model.create_energy_system(load_data, pv_data, wind_data, price_data)
    
    # 获取储能组件并检查约束
    battery = model.get_component_by_label('battery_storage')
    print(f"储能容量: {battery.nominal_storage_capacity} MWh")
    
    if hasattr(battery, 'min_storage_level') and hasattr(battery, 'max_storage_level'):
        min_soc = battery.min_storage_level[0] if hasattr(battery.min_storage_level, '__getitem__') else battery.min_storage_level
        max_soc = battery.max_storage_level[0] if hasattr(battery.max_storage_level, '__getitem__') else battery.max_storage_level
        min_capacity = battery.nominal_storage_capacity * min_soc
        max_capacity = battery.nominal_storage_capacity * max_soc
        print(f"SOC约束: {min_soc} - {max_soc}")
        print(f"有效容量范围: {min_capacity:.1f} - {max_capacity:.1f} MWh")
        print("✓ SOC约束已设置")
    else:
        print("✗ SOC约束未设置")
        return False
    
    # 运行优化
    print("\n开始运行优化...")
    solver = OptimizationSolver()
    success = solver.solve(energy_system)
    
    if not success:
        print("❌ 优化求解失败！")
        return False
    
    print("✓ 优化求解成功")
    
    # 获取优化结果
    results = solver.get_results()
    if not results:
        print("❌ 无法获取优化结果！")
        return False
    
    # 获取储能系统的结果
    from oemof.solph import views
    
    # 查找储能系统组件
    battery_component = None
    battery_name = None
    
    for component_name, component in model.components.items():
        if 'storage' in component_name.lower():
            battery_component = component
            battery_name = component_name
            print(f"找到储能系统: {component_name}")
            break
    
    if battery_component is None:
        print("❌ 未找到储能系统组件")
        print(f"可用组件: {list(model.components.keys())}")
        return False
    
    # 处理储能组件可能是列表的情况
    if isinstance(battery_component, list):
        if len(battery_component) > 0:
            battery = battery_component[0]
        else:
            print("❌ 储能组件列表为空")
            return False
    else:
        battery = battery_component
    
    print(f"储能系统类型: {type(battery)}")
    
    # 简化验证：直接检查配置是否正确应用
    try:
        capacity = getattr(battery, 'nominal_storage_capacity', 20)
        print(f"储能容量: {capacity} MWh")
        
        # 检查储能系统的所有属性
        print(f"储能系统属性:")
        for attr in dir(battery):
            if not attr.startswith('_'):
                try:
                    value = getattr(battery, attr)
                    if not callable(value):
                        print(f"  {attr}: {value} ({type(value)})")
                except:
                    pass
        
        # 检查min_storage_level和max_storage_level是否设置
        min_level = getattr(battery, 'min_storage_level', None)
        max_level = getattr(battery, 'max_storage_level', None)
        
        print(f"\nmin_storage_level: {min_level} ({type(min_level)})")
        print(f"max_storage_level: {max_level} ({type(max_level)})")
        
        if min_level is not None and max_level is not None:
            # 处理序列类型的SOC约束
            try:
                if hasattr(min_level, '__getitem__'):
                    print(f"min_level是序列类型")
                    # 直接访问第一个元素，不检查长度
                    min_soc_value = min_level[0]
                else:
                    print(f"min_level不是序列类型: {min_level}")
                    min_soc_value = min_level
            except Exception as e:
                print(f"处理min_level时出错: {e}")
                min_soc_value = None
                
            try:
                if hasattr(max_level, '__getitem__'):
                    print(f"max_level是序列类型")
                    # 直接访问第一个元素，不检查长度
                    max_soc_value = max_level[0]
                else:
                    print(f"max_level不是序列类型: {max_level}")
                    max_soc_value = max_level
            except Exception as e:
                print(f"处理max_level时出错: {e}")
                max_soc_value = None
            
            print(f"实际SOC约束值: {min_soc_value} - {max_soc_value}")
            print(f"min_soc_value类型: {type(min_soc_value)}, max_soc_value类型: {type(max_soc_value)}")
            
            # 检查SOC约束是否正确设置
            if min_soc_value is not None and max_soc_value is not None:
                if min_soc_value == 0.2 and max_soc_value == 0.9:
                    print("✓ SOC约束设置正确 (0.2 - 0.9)")
                    return True
                else:
                    print(f"❌ SOC约束设置不正确，期望 0.2 - 0.9，实际 {min_soc_value} - {max_soc_value}")
                    return False
            else:
                print(f"❌ SOC约束值为None: min_soc_value={min_soc_value}, max_soc_value={max_soc_value}")
                return False
        else:
            print("❌ 未找到SOC约束设置")
            return False
            
    except Exception as e:
        print(f"❌ 检查储能系统时出错: {e}")
        return False
    


if __name__ == "__main__":
    success = test_storage_fix()
    if success:
        print("\n🎉 储能系统约束修复成功！")
    else:
        print("\n❌ 储能系统约束修复失败！")