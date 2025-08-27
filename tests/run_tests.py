"""
虚拟电厂测试运行器
VPP Test Runner

统一运行所有测试脚本的入口程序
"""

import os
import sys
import argparse
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
src_dir = os.path.join(project_root, 'src')
sys.path.insert(0, src_dir)


def print_header():
    """打印测试头部信息"""
    print("=" * 80)
    print(" " * 25 + "虚拟电厂系统测试套件")
    print(" " * 20 + "VPP System Test Suite")
    print("=" * 80)
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    print("-" * 80)


def run_basic_tests():
    """运行基础功能测试"""
    print("\n🔧 基础功能测试")
    print("-" * 50)
    
    try:
        from tests.test_vpp_system import run_tests
        success = run_tests()
        return success
    except Exception as e:
        print(f"❌ 基础功能测试失败: {e}")
        return False


def run_scheduling_modes_tests():
    """运行调度模式测试"""
    print("\n🎛️ 调度模式测试")
    print("-" * 50)
    
    try:
        from tests.test_scheduling_modes import run_comprehensive_test
        success = run_comprehensive_test()
        return success
    except Exception as e:
        print(f"❌ 调度模式测试失败: {e}")
        return False


def run_optimization_objectives_tests():
    """运行优化目标测试"""
    print("\n🎯 优化目标测试")
    print("-" * 50)
    
    try:
        from tests.test_optimization_objectives import run_comparison_demo
        run_comparison_demo()
        return True
    except Exception as e:
        print(f"❌ 优化目标测试失败: {e}")
        return False


def run_adjustable_loads_tests():
    """运行可调负荷测试"""
    print("\n⚡ 可调负荷测试")
    print("-" * 50)
    
    try:
        from tests.test_adjustable_loads import test_adjustable_loads
        success = test_adjustable_loads()
        return success
    except Exception as e:
        print(f"❌ 可调负荷测试失败: {e}")
        return False


def run_ancillary_services_tests():
    """运行辅助服务测试"""
    print("\n🔋 辅助服务测试")
    print("-" * 50)
    
    try:
        from tests.test_ancillary_services import test_ancillary_services
        success = test_ancillary_services()
        return success
    except Exception as e:
        print(f"❌ 辅助服务测试失败: {e}")
        return False


def run_cbc_tests():
    """运行CBC求解器测试"""
    print("\n🔨 CBC求解器测试")
    print("-" * 50)
    
    try:
        # 直接执行test_cbc.py文件
        import subprocess
        cbc_test_path = os.path.join(current_dir, 'test_cbc.py')
        result = subprocess.run([sys.executable, cbc_test_path], 
                               capture_output=True, text=True, 
                               cwd=project_root)
        
        print(result.stdout)
        if result.stderr:
            print("错误输出:", result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ CBC求解器测试失败: {e}")
        return False


def run_complete_flow_tests():
    """运行完整流程测试"""
    print("\n🔄 完整流程测试")
    print("-" * 50)
    
    try:
        from tests.test_complete_flow import test_complete_flow
        success = test_complete_flow()
        return success
    except Exception as e:
        print(f"❌ 完整流程测试失败: {e}")
        return False


def run_all_tests():
    """运行所有测试"""
    print_header()
    
    test_results = {}
    
    # 定义测试列表
    tests = [
        ("基础功能", run_basic_tests),
        ("CBC求解器", run_cbc_tests),
        ("调度模式", run_scheduling_modes_tests),
        ("优化目标", run_optimization_objectives_tests),
        ("可调负荷", run_adjustable_loads_tests),
        ("辅助服务", run_ancillary_services_tests),
        ("完整流程", run_complete_flow_tests),
    ]
    
    # 逐个运行测试
    for test_name, test_func in tests:
        try:
            success = test_func()
            test_results[test_name] = success
        except Exception as e:
            print(f"❌ {test_name}测试执行异常: {e}")
            test_results[test_name] = False
    
    # 打印测试结果总结
    print_test_summary(test_results)
    
    return test_results


def print_test_summary(test_results):
    """打印测试结果总结"""
    print("\n" + "=" * 80)
    print(" " * 30 + "测试结果总结")
    print("=" * 80)
    
    passed_tests = sum(1 for success in test_results.values() if success)
    total_tests = len(test_results)
    
    print(f"\n📊 总体结果: {passed_tests}/{total_tests} 个测试通过")
    print("-" * 60)
    
    for test_name, success in test_results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"{test_name:<15} {status}")
    
    overall_success = all(test_results.values())
    print(f"\n🎯 整体测试状态: {'✅ 全部通过' if overall_success else '❌ 部分失败'}")
    print(f"📅 测试完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if not overall_success:
        print("\n💡 建议:")
        print("1. 检查失败的测试模块的错误信息")
        print("2. 确认依赖包安装正确")
        print("3. 检查CBC求解器路径配置")
        print("4. 查看详细错误日志")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="虚拟电厂系统测试运行器")
    parser.add_argument("--test", choices=[
        "basic", "cbc", "scheduling", "objectives", 
        "loads", "ancillary", "flow", "all"
    ], default="all", help="选择要运行的测试类型")
    
    args = parser.parse_args()
    
    if args.test == "basic":
        run_basic_tests()
    elif args.test == "cbc":
        run_cbc_tests()
    elif args.test == "scheduling":
        run_scheduling_modes_tests()
    elif args.test == "objectives":
        run_optimization_objectives_tests()
    elif args.test == "loads":
        run_adjustable_loads_tests()
    elif args.test == "ancillary":
        run_ancillary_services_tests()
    elif args.test == "flow":
        run_complete_flow_tests()
    else:  # all
        run_all_tests()


if __name__ == "__main__":
    main()