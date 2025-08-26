"""
虚拟电厂调度优化系统主程序
VPP Optimization System Main Entry

整合所有模块，执行完整的虚拟电厂优化调度流程
"""

import os
import sys
import time
from datetime import datetime

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# 导入项目模块
from src.data.data_generator import VPPDataGenerator
from src.models.vpp_model import VPPOptimizationModel
from src.solvers.optimization_solver import OptimizationSolver
from src.analysis.result_analyzer import ResultAnalyzer
from src.visualization.plot_generator import PlotGenerator

# 导入oemof模块
import oemof.solph as solph


def print_header():
    """打印程序头部信息"""
    print("=" * 80)
    print(" " * 20 + "虚拟电厂调度优化系统")
    print(" " * 15 + "Virtual Power Plant Optimization System")
    print("=" * 80)
    print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("基于 oemof-solph 构建，采用 CBC 求解器")
    print("-" * 80)


def main():
    """主程序函数"""
    print_header()
    
    total_start_time = time.time()
    
    try:
        # 步骤1: 数据生成
        print("\n🔸 步骤1: 生成虚拟电厂数据")
        print("-" * 40)
        
        data_generator = VPPDataGenerator()
        load_data, pv_data, wind_data, price_data = data_generator.generate_all_data()
        
        # 保存输入数据
        data_file = data_generator.save_data("outputs")
        print(f"✓ 输入数据已保存: {data_file}")
        
        # 步骤2: 创建优化模型
        print("\n🔸 步骤2: 构建能源系统优化模型")
        print("-" * 40)
        
        model = VPPOptimizationModel(data_generator.time_index)
        energy_system = model.create_energy_system(load_data, pv_data, wind_data, price_data)
        
        # 验证系统
        if not model.validate_system():
            print("❌ 能源系统验证失败，程序终止")
            return False
        
        system_summary = model.get_system_summary()
        print(f"✓ 能源系统构建完成")
        print(f"  - 组件总数: {system_summary['total_components']}")
        print(f"  - 时间段数: {system_summary['time_periods']}")
        
        # 步骤3: 优化求解
        print("\n🔸 步骤3: 执行优化求解")
        print("-" * 40)
        
        # 使用可靠的求解方法
        try:
            # 创建优化模型
            opt_model = solph.Model(energy_system)
            print("✓ 优化模型创建成功")
            
            # 设置CBC路径
            cbc_path = os.path.join(os.getcwd(), 'cbc', 'bin', 'cbc.exe')
            
            # 使用pyomo直接调用CBC
            from pyomo.opt import SolverFactory
            solver = SolverFactory('cbc', executable=cbc_path)
            
            if not solver.available():
                print("❌ CBC求解器不可用，程序终止")
                return False
            
            print(f"✓ 使用CBC求解器: {cbc_path}")
            
            # 求解
            solve_start_time = time.time()
            results = solver.solve(opt_model, tee=False)
            solve_time = time.time() - solve_start_time
            
            if str(results.solver.termination_condition).lower() in ['optimal', 'feasible']:
                print("✓ 优化求解成功")
                print(f"  - 求解时间: {solve_time:.2f} 秒")
                
                # 提取oemof结果
                optimization_results = solph.processing.results(opt_model)
                solve_success = True
            else:
                print(f"❌ 求解失败，状态: {results.solver.termination_condition}")
                return False
                
        except Exception as e:
            print(f"❌ 求解过程中发生错误: {e}")
            return False
        
        # 步骤4: 结果分析
        print("\n🔸 步骤4: 分析优化结果")
        print("-" * 40)
        
        analyzer = ResultAnalyzer()
        results_df, economics, technical_metrics = analyzer.analyze_results(
            optimization_results, energy_system, data_generator.time_index, price_data
        )
        
        # 保存分析结果
        saved_files = analyzer.save_results("outputs")
        print(f"✓ 结果分析完成，已保存 {len(saved_files)} 个文件")
        
        # 打印关键指标
        print(f"\n📊 关键指标:")
        print(f"  - 总负荷: {technical_metrics['load_total_mwh']:.1f} MWh")
        print(f"  - 可再生能源渗透率: {technical_metrics['renewable_penetration_ratio']:.1%}")
        print(f"  - 自给自足率: {technical_metrics['self_sufficiency_ratio']:.1%}")
        print(f"  - 净运行成本: {economics['net_cost_yuan']:,.0f} 元")
        print(f"  - 平均供电成本: {economics['average_cost_yuan_per_mwh']:.2f} 元/MWh")
        
        # 步骤5: 可视化
        print("\n🔸 步骤5: 生成可视化图表")
        print("-" * 40)
        
        plot_generator = PlotGenerator()
        plot_file = plot_generator.generate_all_plots(
            results_df, economics, price_data, "outputs/plots"
        )
        print(f"✓ 可视化图表已生成: {plot_file}")
        
        # 生成汇总报告
        print("\n🔸 生成汇总报告")
        print("-" * 40)
        
        summary_report = analyzer.generate_summary_report()
        print(summary_report)
        
        # 程序完成
        total_time = time.time() - total_start_time
        print(f"\n🎉 虚拟电厂优化调度完成！")
        print(f"总用时: {total_time:.2f} 秒")
        print(f"结果文件保存在 outputs 目录")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 程序执行过程中发生错误:")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        
        # 打印详细错误信息（调试用）
        import traceback
        print(f"\n详细错误信息:")
        traceback.print_exc()
        
        return False
    
    finally:
        print(f"\n程序结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)


def run_demo():
    """运行演示模式"""
    print("🚀 启动虚拟电厂优化调度演示...")
    success = main()
    
    if success:
        print("\n✅ 演示运行成功！")
        print("\n📁 输出文件说明:")
        print("  - outputs/vpp_input_data_*.csv: 输入数据")
        print("  - outputs/optimization_results_*.csv: 优化结果时间序列")
        print("  - outputs/economics_analysis_*.csv: 经济性分析")
        print("  - outputs/technical_metrics_*.csv: 技术指标")
        print("  - outputs/summary_report_*.txt: 汇总报告")
        print("  - outputs/plots/vpp_optimization_results_*.png: 可视化图表")
        print("\n💡 提示: 可以通过修改 config/ 目录下的配置文件来自定义系统参数")
    else:
        print("\n❌ 演示运行失败，请检查错误信息")
    
    return success


if __name__ == "__main__":
    # 检查命令行参数
    if len(sys.argv) > 1:
        if sys.argv[1] == "--demo":
            run_demo()
        elif sys.argv[1] == "--help":
            print("虚拟电厂调度优化系统 - 使用说明")
            print("-" * 50)
            print("python main.py          # 运行完整优化流程")
            print("python main.py --demo   # 运行演示模式")
            print("python main.py --help   # 显示帮助信息")
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("使用 python main.py --help 查看帮助信息")
    else:
        # 默认运行主程序
        main()