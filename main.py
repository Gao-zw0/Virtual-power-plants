"""
虚拟电厂调度优化系统主程序
VPP Optimization System Main Entry

整合所有模块，执行完整的虚拟电厂优化调度流程
"""

import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# 导入项目模块
from src.data.data_generator import VPPDataGenerator
from src.models.vpp_model import VPPOptimizationModel
from src.models.scheduling_modes import VPPSchedulingManager, SchedulingMode, OptimizationObjective
from src.solvers.optimization_solver import OptimizationSolver
from src.analysis.result_analyzer import ResultAnalyzer
from src.visualization.plot_generator import PlotGenerator
from src.utils.file_manager import VPPFileManager, SessionContext

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


def main(scheduling_mode: Optional[str] = None):
    """主程序函数"""
    print_header()
    
    # 如果提供了调度模式参数，运行指定模式
    if scheduling_mode:
        return run_scheduling_mode(scheduling_mode)
    
    # 否则运行交互式模式选择
    return run_interactive_mode_selection()


def run_interactive_mode_selection():
    """运行交互式调度模式选择"""
    print("\n🔧 虚拟电厂调度模式选择")
    print("-" * 50)
    
    # 创建调度模式管理器
    manager = VPPSchedulingManager()
    
    # 选择优化目标
    print("步骤1: 选择优化目标")
    available_objectives = manager.list_available_objectives()
    
    print("可选的优化目标:")
    for i, (obj, description) in enumerate(available_objectives, 1):
        print(f"{i}. {obj.value}: {description}")
    
    try:
        obj_choice = input(f"\n请选择优化目标 (1-{len(available_objectives)}, 默认为1): ").strip()
        
        if obj_choice == "":
            selected_objective = available_objectives[0][0]  # 默认为成本最小化
        else:
            obj_index = int(obj_choice) - 1
            if 0 <= obj_index < len(available_objectives):
                selected_objective = available_objectives[obj_index][0]
            else:
                print("❌ 无效选择，使用默认目标")
                selected_objective = available_objectives[0][0]
        
        manager.set_optimization_objective(selected_objective)
        
    except (ValueError, KeyboardInterrupt):
        print("\n❌ 已取消操作")
        return False
    
    # 选择调度模式
    print(f"\n步骤2: 选择调度模式")
    available_modes = manager.list_available_modes()
    
    print("可选的调度模式:")
    for i, (mode, description) in enumerate(available_modes, 1):
        print(f"{i}. {mode.value}: {description}")
    
    # 添加批量运行选项
    print(f"{len(available_modes)+1}. all: 运行所有调度模式进行对比分析")
    
    try:
        choice = input(f"\n请选择调度模式 (1-{len(available_modes)+1}): ").strip()
        
        if choice == str(len(available_modes)+1) or choice.lower() == 'all':
            return run_all_modes_comparison_with_objective(selected_objective)
        else:
            mode_index = int(choice) - 1
            if 0 <= mode_index < len(available_modes):
                selected_mode = available_modes[mode_index][0]
                return run_scheduling_mode_by_enum_with_objective(selected_mode, selected_objective)
            else:
                print("❌ 无效选择")
                return False
    except (ValueError, KeyboardInterrupt):
        print("\n❌ 已取消操作")
        return False


def run_single_mode_analysis_with_objective(mode: SchedulingMode, objective: OptimizationObjective) -> Tuple[bool, Dict]:
    """运行带优化目标的单个调度模式分析"""
    total_start_time = time.time()
    
    # 创建文件管理器
    file_manager = VPPFileManager()
    
    # 使用会话上下文管理文件
    with SessionContext(file_manager, mode, objective) as session:
        
        try:
            # 步骤1: 数据生成
            print("\n🔸 步骤1: 生成虚拟电厂数据")
            print("-" * 40)
            
            data_generator = VPPDataGenerator()
            load_data, pv_data, wind_data, price_data = data_generator.generate_all_data()
            
            # 保存输入数据到会话目录
            input_data_path = data_generator.save_data_to_session(session, "input_data.csv")
            print(f"✓ 输入数据已保存: {input_data_path}")
            
            # 步骤2: 创建调度模式管理器和优化模型
            print("\n🔸 步骤2: 构建调度模式优化模型")
            print("-" * 40)
            
            manager = VPPSchedulingManager()
            model = manager.create_optimized_model(mode, data_generator.time_index, objective)
            energy_system = model.create_energy_system(load_data, pv_data, wind_data, price_data)
            
            # 验证系统
            if not model.validate_system():
                print("❌ 能源系统验证失败，程序终止")
                return False, {}
            
            system_summary = model.get_system_summary()
            print(f"✓ 能源系统构建完成")
            print(f"  - 组件总数: {system_summary['total_components']}")
            print(f"  - 时间段数: {system_summary['time_periods']}")
            print(f"  - 优化目标: {objective.value}")
            
            # 步骤3: 优化求解
            print("\n🔸 步骤3: 执行优化求解")
            print("-" * 40)
            
            try:
                opt_model = solph.Model(energy_system)
                print("✓ 优化模型创建成功")
                
                cbc_path = os.path.join(os.getcwd(), 'cbc', 'bin', 'cbc.exe')
                
                from pyomo.opt import SolverFactory
                solver = SolverFactory('cbc', executable=cbc_path)
                
                if not solver.available():
                    print("❌ CBC求解器不可用，程序终止")
                    return False, {}
                
                print(f"✓ 使用CBC求解器: {cbc_path}")
                
                solve_start_time = time.time()
                results = solver.solve(opt_model, tee=False)
                solve_time = time.time() - solve_start_time
                
                if str(results.solver.termination_condition).lower() in ['optimal', 'feasible']:
                    print("✓ 优化求解成功")
                    print(f"  - 求解时间: {solve_time:.2f} 秒")
                    
                    optimization_results = solph.processing.results(opt_model)
                else:
                    print(f"❌ 求解失败，状态: {results.solver.termination_condition}")
                    return False, {}
                    
            except Exception as e:
                print(f"❌ 求解过程中发生错误: {e}")
                return False, {}
            
            # 步骤4: 分析优化结果
            print("\n🔸 步骤4: 分析优化结果")
            print("-" * 40)
            
            analyzer = ResultAnalyzer()
            results_df, economics, technical_metrics = analyzer.analyze_results(
                optimization_results, energy_system, data_generator.time_index, price_data
            )
            
            # 保存结果到会话目录
            saved_files = analyzer.save_results_to_session(session)
            print(f"✓ 结果分析完成，已保存 {len(saved_files)} 个文件")
            
            # 步骤5: 生成可视化图表
            print("\n🔸 步骤5: 生成可视化图表")
            print("-" * 40)
            
            plot_generator = PlotGenerator()
            plot_path = plot_generator.generate_plots_to_session(
                results_df, economics, price_data, session, "optimization_results.png"
            )
            print(f"✓ 可视化图表已生成: {plot_path}")
            
            # 步骤6: 生成模式总结报告
            print("\n🔸 步骤6: 生成模式总结报告")
            print("-" * 40)
            
            # 创建模式特定的总结报告
            mode_summary = f"""
{"=" * 80}
虚拟电厂调度模式总结报告
{"=" * 80}

【模式信息】
调度模式: {mode.value}
优化目标: {objective.value}
模式描述: {manager.get_mode_description(mode)}
目标描述: {manager.get_objective_function_description(objective)}

【系统配置】
组件总数: {system_summary['total_components']}
时间段数: {system_summary['time_periods']}
起始时间: {system_summary['start_time']}
结束时间: {system_summary['end_time']}

【资源配置】
"""
            # 添加资源配置信息
            resources = manager.get_mode_resources(mode)
            for resource, enabled in resources.items():
                status = "✓ 启用" if enabled else "✗ 禁用"
                mode_summary += f"{resource}: {status}\n"
            
            mode_summary += f"\n\n{analyzer.generate_summary_report()}"
            
            mode_summary_path = session.save_file(
                'summary_report', 'mode_summary_report.txt', mode_summary
            )
            print(f"✓ 模式总结报告已生成: {mode_summary_path}")
            
            # 打印关键指标
            print(f"\n📊 关键指标:")
            print(f"  - 总负荷: {technical_metrics['load_total_mwh']:.1f} MWh")
            print(f"  - 可再生能源渗透率: {technical_metrics['renewable_penetration_ratio']:.1%}")
            print(f"  - 自给自足率: {technical_metrics['self_sufficiency_ratio']:.1%}")
            print(f"  - 净运行成本: {economics['net_cost_yuan']:,.0f} 元")
            print(f"  - 平均供电成本: {economics['average_cost_yuan_per_mwh']:.2f} 元/MWh")
            
            # 程序完成
            total_time = time.time() - total_start_time
            print(f"\n🎉 {mode.value} 调度模式（{objective.value}）优化完成！")
            print(f"🕰️  总耗时: {total_time:.2f} 秒")
            print(f"📁 会话目录: {session.session_dir}")
            
            return True, {
                'session_dir': str(session.session_dir),
                'economics': economics,
                'technical_metrics': technical_metrics,
                'solve_time': solve_time,
                'total_time': total_time
            }
            
        except Exception as e:
            print(f"❌ 系统错误: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, {}



def run_scheduling_mode_by_enum_with_objective(mode: SchedulingMode, objective: OptimizationObjective):
    """根据枚举运行带优化目标的调度模式"""
    success, summary = run_single_mode_analysis_with_objective(mode, objective)
    
    if success:
        print(f"\n✅ {mode.value} 调度模式（{objective.value}）运行成功！")
        return True
    else:
        print(f"\n❌ {mode.value} 调度模式运行失败")
        return False


def run_all_modes_comparison_with_objective(objective: OptimizationObjective):
    """运行所有调度模式进行带优化目标的对比分析"""
    print(f"\n🔄 运行所有调度模式进行对比分析（目标: {objective.value}）...")
    print("=" * 80)
    
    manager = VPPSchedulingManager()
    available_modes = [mode for mode, _ in manager.list_available_modes()]
    
    results_summary = []
    
    for i, mode in enumerate(available_modes, 1):
        print(f"\n[{i}/{len(available_modes)}] 运行 {mode.value} 模式（{objective.value}）...")
        print("-" * 60)
        
        success, summary = run_single_mode_analysis_with_objective(mode, objective)
        if success:
            results_summary.append((mode, summary))
        else:
            print(f"❌ {mode.value} 模式运行失败")
    
    # 生成对比报告
    if results_summary:
        generate_comparison_report_with_objective(results_summary, objective)
        print("\n✅ 所有调度模式对比分析完成！")
        return True
    else:
        print("\n❌ 所有调度模式运行均失败")
        return False


def generate_comparison_report_with_objective(results_summary: List[Tuple[SchedulingMode, Dict]], 
                                            objective: OptimizationObjective):
    """生成带优化目标的调度模式对比报告"""
    print("\n📊 生成调度模式对比报告")
    print("-" * 60)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"outputs/modes_comparison_{objective.value}_{timestamp}.txt"
    
    os.makedirs("outputs", exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write(f"虚拟电厂调度模式对比分析报告 - {objective.value.upper()}\n")
        f.write("=" * 80 + "\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"优化目标: {objective.value}\n\n")
        
        # 创建对比表格
        f.write("📋 调度模式对比表\n")
        f.write("-" * 60 + "\n")
        
        # 表头
        f.write(f"{'调度模式':<20} {'净运行成本(元)':<15} {'平均成本(元/MWh)':<18} {'运行时间(秒)':<12}\n")
        f.write("-" * 70 + "\n")
        
        # 数据行
        for mode, summary in results_summary:
            economics = summary.get('economics', {})
            net_cost = economics.get('net_cost_yuan', 0)
            avg_cost = economics.get('average_cost_yuan_per_mwh', 0)
            run_time = summary.get('total_time', 0)
            
            f.write(f"{mode.value:<20} {net_cost:>13,.0f} {avg_cost:>16.2f} {run_time:>10.2f}\n")
        
        f.write("\n" + "=" * 80 + "\n")
    
    print(f"✓ 对比报告已保存: {report_file}")
    
    # 在控制台显示简要对比
    print(f"\n📊 调度模式对比摘要（{objective.value}）:")
    print(f"{'模式':<20} {'净成本(万元)':<12} {'平均成本(元/MWh)':<16}")
    print("-" * 50)
    
    for mode, summary in results_summary:
        economics = summary.get('economics', {})
        net_cost = economics.get('net_cost_yuan', 0) / 10000  # 转换为万元
        avg_cost = economics.get('average_cost_yuan_per_mwh', 0)
        print(f"{mode.value:<20} {net_cost:>10.1f} {avg_cost:>14.2f}")


def run_all_modes_comparison():
    """运行所有调度模式进行对比分析"""
    print("\n🔄 运行所有调度模式进行对比分析...")
    print("=" * 80)
    
    manager = VPPSchedulingManager()
    available_modes = [mode for mode, _ in manager.list_available_modes()]
    
    results_summary = []
    
    for i, mode in enumerate(available_modes, 1):
        print(f"\n[{i}/{len(available_modes)}] 运行 {mode.value} 模式...")
        print("-" * 60)
        
        success, summary = run_single_mode_analysis(mode)
        if success:
            results_summary.append((mode, summary))
        else:
            print(f"❌ {mode.value} 模式运行失败")
    
    # 生成对比报告
    if results_summary:
        generate_comparison_report(results_summary)
        print("\n✅ 所有调度模式对比分析完成！")
        return True
    else:
        print("\n❌ 所有调度模式运行均失败")
        return False


def run_scheduling_mode(mode_name: str):
    """运行指定名称的调度模式"""
    try:
        mode = SchedulingMode(mode_name)
        return run_scheduling_mode_by_enum(mode)
    except ValueError:
        print(f"❌ 未知的调度模式: {mode_name}")
        print("可选模式: renewable_storage, adjustable_storage, traditional, no_renewable, storage_only, full_system")
        return False


def run_scheduling_mode_by_enum(mode: SchedulingMode):
    """根据枚举运行调度模式"""
    success, summary = run_single_mode_analysis(mode)
    
    if success:
        print(f"\n✅ {mode.value} 调度模式运行成功！")
        print("\n📊 关键指标:")
        if 'economics' in summary:
            economics = summary['economics']
            print(f"  - 净运行成本: {economics.get('net_cost_yuan', 0):,.0f} 元")
            print(f"  - 平均供电成本: {economics.get('average_cost_yuan_per_mwh', 0):.2f} 元/MWh")
        if 'technical_metrics' in summary:
            metrics = summary['technical_metrics']
            print(f"  - 总负荷: {metrics.get('load_total_mwh', 0):.1f} MWh")
            print(f"  - 可再生能源渗透率: {metrics.get('renewable_penetration_ratio', 0):.1%}")
            print(f"  - 自给自足率: {metrics.get('self_sufficiency_ratio', 0):.1%}")
        return True
    else:
        print(f"\n❌ {mode.value} 调度模式运行失败")
        return False


def run_single_mode_analysis(mode: SchedulingMode) -> Tuple[bool, Dict]:
    """运行单个调度模式分析"""
    total_start_time = time.time()
    
    try:
        # 步骤1: 数据生成
        print("\n🔸 步骤1: 生成虚拟电厂数据")
        print("-" * 40)
        
        data_generator = VPPDataGenerator()
        load_data, pv_data, wind_data, price_data = data_generator.generate_all_data()
        
        # 保存输入数据
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_file = data_generator.save_data(f"outputs/mode_{mode.value}")
        print(f"✓ 输入数据已保存: {data_file}")
        
        # 步骤2: 创建调度模式管理器和优化模型
        print("\n🔸 步骤2: 构建调度模式优化模型")
        print("-" * 40)
        
        manager = VPPSchedulingManager()
        model = manager.create_optimized_model(mode, data_generator.time_index)
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
        
        # 保存分析结果到模式专用目录
        output_dir = f"outputs/mode_{mode.value}"
        os.makedirs(output_dir, exist_ok=True)
        saved_files = analyzer.save_results(output_dir)
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
        plot_dir = f"outputs/mode_{mode.value}/plots"
        plot_file = plot_generator.generate_all_plots(
            results_df, economics, price_data, plot_dir
        )
        print(f"✓ 可视化图表已生成: {plot_file}")
        
        # 生成调度模式专用汇总报告
        print("\n🔸 生成调度模式汇总报告")
        print("-" * 40)
        
        mode_summary_report = generate_mode_summary_report(
            mode, model, economics, technical_metrics, analyzer
        )
        
        # 保存模式汇总报告
        report_file = os.path.join(output_dir, f"mode_summary_report_{timestamp}.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(mode_summary_report)
        
        print(mode_summary_report)
        print(f"✓ 调度模式报告已保存: {report_file}")
        
        # 程序完成
        total_time = time.time() - total_start_time
        print(f"\n🎉 {mode.value} 调度模式优化完成！")
        print(f"总用时: {total_time:.2f} 秒")
        print(f"结果文件保存在 {output_dir} 目录")
        
        # 返回成功状态和结果摘要
        summary = {
            'mode': mode,
            'economics': economics,
            'technical_metrics': technical_metrics,
            'total_time': total_time,
            'output_dir': output_dir
        }
        
        return True, summary
        
    except Exception as e:
        print(f"\n❌ {mode.value} 模式执行过程中发生错误:")
        print(f"错误类型: {type(e).__name__}")
        print(f"错误信息: {str(e)}")
        
        # 打印详细错误信息（调试用）
        import traceback
        print(f"\n详细错误信息:")
        traceback.print_exc()
        
        return False, {}
    
    finally:
        print(f"\n程序结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)


def generate_mode_summary_report(mode: SchedulingMode, model, economics: Dict, 
                               technical_metrics: Dict, analyzer) -> str:
    """生成调度模式专用汇总报告"""
    manager = VPPSchedulingManager()
    
    report = []
    report.append("=" * 80)
    report.append(f"虚拟电厂调度模式分析报告 - {mode.value.upper()}")
    report.append("=" * 80)
    report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 调度模式信息
    report.append("📋 调度模式信息")
    report.append("-" * 40)
    report.append(f"模式名称: {mode.value}")
    report.append(f"模式描述: {manager.get_mode_description(mode)}")
    report.append(f"目标函数: {manager.get_objective_function_description(mode)}")
    report.append("")
    
    # 资源配置信息
    report.append("🔧 资源配置")
    report.append("-" * 40)
    resources = manager.get_mode_resources(mode)
    for resource, enabled in resources.items():
        status = "✓" if enabled else "✗"
        report.append(f"{status} {resource}: {'启用' if enabled else '禁用'}")
    report.append("")
    
    # 经济性分析
    report.append("💰 经济性分析")
    report.append("-" * 40)
    for key, value in economics.items():
        if isinstance(value, (int, float)):
            if 'yuan' in key.lower():
                report.append(f"{key}: {value:,.2f} 元")
            elif 'ratio' in key.lower() or 'rate' in key.lower():
                report.append(f"{key}: {value:.2%}")
            else:
                report.append(f"{key}: {value:.2f}")
        else:
            report.append(f"{key}: {value}")
    report.append("")
    
    # 技术指标
    report.append("📊 技术指标")
    report.append("-" * 40)
    for key, value in technical_metrics.items():
        if isinstance(value, (int, float)):
            if 'mwh' in key.lower():
                report.append(f"{key}: {value:.1f} MWh")
            elif 'mw' in key.lower():
                report.append(f"{key}: {value:.1f} MW")
            elif 'ratio' in key.lower() or 'rate' in key.lower():
                report.append(f"{key}: {value:.2%}")
            else:
                report.append(f"{key}: {value:.2f}")
        else:
            report.append(f"{key}: {value}")
    report.append("")
    
    # 系统概要
    if hasattr(model, 'get_mode_summary'):
        system_summary = model.get_mode_summary()
        report.append("🏗️ 系统概要")
        report.append("-" * 40)
        report.append(f"组件总数: {system_summary.get('total_components', 0)}")
        report.append(f"时间段数: {system_summary.get('time_periods', 0)}")
        report.append(f"包含资源: {', '.join(system_summary.get('included_resources', []))}")
        report.append("")
    
    report.append("=" * 80)
    
    return '\n'.join(report)


def generate_comparison_report(results_summary: List[Tuple[SchedulingMode, Dict]]):
    """生成调度模式对比报告"""
    print("\n📊 生成调度模式对比报告")
    print("-" * 60)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"outputs/modes_comparison_report_{timestamp}.txt"
    
    os.makedirs("outputs", exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("虚拟电厂调度模式对比分析报告\n")
        f.write("=" * 80 + "\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 创建对比表格
        f.write("📋 调度模式对比表\n")
        f.write("-" * 60 + "\n")
        
        # 表头
        f.write(f"{'调度模式':<20} {'净运行成本(元)':<15} {'平均成本(元/MWh)':<18} {'运行时间(秒)':<12}\n")
        f.write("-" * 70 + "\n")
        
        # 数据行
        for mode, summary in results_summary:
            economics = summary.get('economics', {})
            net_cost = economics.get('net_cost_yuan', 0)
            avg_cost = economics.get('average_cost_yuan_per_mwh', 0)
            run_time = summary.get('total_time', 0)
            
            f.write(f"{mode.value:<20} {net_cost:>13,.0f} {avg_cost:>16.2f} {run_time:>10.2f}\n")
        
        f.write("\n")
        
        # 详细分析
        f.write("📊 详细分析\n")
        f.write("-" * 60 + "\n")
        
        for mode, summary in results_summary:
            f.write(f"\n🔧 {mode.value.upper()} 模式\n")
            f.write("-" * 30 + "\n")
            
            economics = summary.get('economics', {})
            technical_metrics = summary.get('technical_metrics', {})
            
            f.write(f"净运行成本: {economics.get('net_cost_yuan', 0):,.0f} 元\n")
            f.write(f"平均供电成本: {economics.get('average_cost_yuan_per_mwh', 0):.2f} 元/MWh\n")
            f.write(f"可再生能源渗透率: {technical_metrics.get('renewable_penetration_ratio', 0):.1%}\n")
            f.write(f"自给自足率: {technical_metrics.get('self_sufficiency_ratio', 0):.1%}\n")
            f.write(f"运行时间: {summary.get('total_time', 0):.2f} 秒\n")
        
        f.write("\n" + "=" * 80 + "\n")
    
    print(f"✓ 对比报告已保存: {report_file}")
    
    # 在控制台显示简要对比
    print("\n📊 调度模式对比摘要:")
    print(f"{'模式':<20} {'净成本(万元)':<12} {'平均成本(元/MWh)':<16}")
    print("-" * 50)
    
    for mode, summary in results_summary:
        economics = summary.get('economics', {})
        net_cost = economics.get('net_cost_yuan', 0) / 10000  # 转换为万元
        avg_cost = economics.get('average_cost_yuan_per_mwh', 0)
        print(f"{mode.value:<20} {net_cost:>10.1f} {avg_cost:>14.2f}")


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
            print("python main.py                          # 交互式模式选择")
            print("python main.py --demo                   # 运行演示模式(完整系统)")
            print("python main.py --mode=<mode_name>       # 运行指定调度模式")
            print("python main.py --compare-all             # 运行所有模式对比")
            print("python main.py --list-modes             # 列出所有可用模式")
            print("python main.py --help                   # 显示帮助信息")
            print("\n可用调度模式:")
            print("  - renewable_storage     : 可再生能源+储能")
            print("  - adjustable_storage    : 可调负荷+储能")
            print("  - traditional          : 传统模式（无辅助服务）")
            print("  - no_renewable         : 无可再生能源")
            print("  - storage_only         : 纯储能调度")
            print("  - full_system          : 完整系统")
        elif sys.argv[1] == "--list-modes":
            manager = VPPSchedulingManager()
            print("\n可用的虚拟电厂调度模式:")
            print("=" * 60)
            for mode, description in manager.list_available_modes():
                print(f"• {mode.value}: {description}")
        elif sys.argv[1] == "--compare-all":
            run_all_modes_comparison()
        elif sys.argv[1].startswith("--mode="):
            mode_name = sys.argv[1].split("=")[1]
            main(mode_name)
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("使用 python main.py --help 查看帮助信息")
    else:
        # 默认运行交互式模式选择
        main()