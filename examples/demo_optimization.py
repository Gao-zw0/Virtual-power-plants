"""
虚拟电厂优化演示脚本
VPP Optimization Demo

快速演示虚拟电厂调度优化的基本功能
"""

import os
import sys

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from src.data.data_generator import VPPDataGenerator
from src.models.vpp_model import VPPOptimizationModel
from src.solvers.optimization_solver import OptimizationSolver


def simple_demo():
    """简单演示"""
    print("🚀 虚拟电厂优化演示")
    print("="*50)
    
    try:
        # 1. 生成数据
        print("📊 生成示例数据...")
        generator = VPPDataGenerator()
        load_data, pv_data, wind_data, price_data = generator.generate_all_data()
        
        # 2. 创建模型
        print("\n🔧 构建优化模型...")
        model = VPPOptimizationModel(generator.time_index)
        energy_system = model.create_energy_system(load_data, pv_data, wind_data, price_data)
        
        # 3. 求解
        print("\n⚡ 执行优化求解...")
        solver = OptimizationSolver()
        success = solver.solve(energy_system)
        
        if success:
            print("✅ 优化成功完成！")
            stats = solver.get_solve_statistics()
            print(f"求解时间: {stats.get('solve_time_seconds', 0):.2f} 秒")
        else:
            print("❌ 优化失败")
        
        return success
        
    except Exception as e:
        print(f"❌ 演示过程出错: {e}")
        return False


if __name__ == "__main__":
    simple_demo()