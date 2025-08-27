"""
虚拟电厂调度模式测试程序
VPP Scheduling Modes Test Program

测试不同调度模式的功能和性能
"""

import os
import sys
import time
import unittest
from datetime import datetime
from typing import Dict, List

# 添加src目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

# 导入项目模块
from src.models.scheduling_modes import VPPSchedulingManager, SchedulingMode, OptimizedVPPModel
from src.data.data_generator import VPPDataGenerator


class TestVPPSchedulingModes(unittest.TestCase):
    """虚拟电厂调度模式测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.manager = VPPSchedulingManager()
        self.data_generator = VPPDataGenerator()
        self.load_data, self.pv_data, self.wind_data, self.price_data = \
            self.data_generator.generate_all_data()
        
        print(f"\n{'='*60}")
        print(f"测试数据生成完成")
        print(f"时间段数: {len(self.data_generator.time_index)}")
        print(f"负荷峰值: {max(self.load_data):.1f} MW")
        print(f"光伏峰值: {max(self.pv_data):.1f} MW")
        print(f"风电峰值: {max(self.wind_data):.1f} MW")
        print(f"{'='*60}")
    
    def test_mode_manager_initialization(self):
        """测试调度模式管理器初始化"""
        print(f"\n🔧 测试调度模式管理器初始化...")
        
        # 测试管理器创建
        self.assertIsNotNone(self.manager)
        self.assertIsNotNone(self.manager.config)
        
        # 测试模式配置初始化
        self.assertEqual(len(self.manager.mode_configs), len(SchedulingMode))
        
        print("✓ 调度模式管理器初始化成功")
    
    def test_available_modes_listing(self):
        """测试可用模式列表"""
        print(f"\n📋 测试可用模式列表...")
        
        available_modes = self.manager.list_available_modes()
        
        # 验证模式数量
        expected_modes = len(SchedulingMode)
        self.assertEqual(len(available_modes), expected_modes)
        
        # 打印所有可用模式
        for mode, description in available_modes:
            print(f"  • {mode.value}: {description}")
        
        print(f"✓ 共发现 {len(available_modes)} 个调度模式")
    
    def test_renewable_storage_mode(self):
        """测试可再生能源+储能模式"""
        print(f"\n🌞 测试可再生能源+储能模式...")
        
        mode = SchedulingMode.RENEWABLE_STORAGE
        success = self._test_single_mode(mode)
        
        self.assertTrue(success, f"{mode.value} 模式测试失败")
        print(f"✓ {mode.value} 模式测试通过")
    
    def test_adjustable_storage_mode(self):
        """测试可调负荷+储能模式"""
        print(f"\n⚡ 测试可调负荷+储能模式...")
        
        mode = SchedulingMode.ADJUSTABLE_STORAGE
        success = self._test_single_mode(mode)
        
        self.assertTrue(success, f"{mode.value} 模式测试失败")
        print(f"✓ {mode.value} 模式测试通过")
    
    def test_traditional_mode(self):
        """测试传统模式"""
        print(f"\n🏭 测试传统模式...")
        
        mode = SchedulingMode.TRADITIONAL
        success = self._test_single_mode(mode)
        
        self.assertTrue(success, f"{mode.value} 模式测试失败")
        print(f"✓ {mode.value} 模式测试通过")
    
    def test_no_renewable_mode(self):
        """测试无可再生能源模式"""
        print(f"\n🔋 测试无可再生能源模式...")
        
        mode = SchedulingMode.NO_RENEWABLE
        success = self._test_single_mode(mode)
        
        self.assertTrue(success, f"{mode.value} 模式测试失败")
        print(f"✓ {mode.value} 模式测试通过")
    
    def test_storage_only_mode(self):
        """测试纯储能模式"""
        print(f"\n🔋 测试纯储能模式...")
        
        mode = SchedulingMode.STORAGE_ONLY
        success = self._test_single_mode(mode)
        
        self.assertTrue(success, f"{mode.value} 模式测试失败")
        print(f"✓ {mode.value} 模式测试通过")
    
    def test_full_system_mode(self):
        """测试完整系统模式"""
        print(f"\n🌐 测试完整系统模式...")
        
        mode = SchedulingMode.FULL_SYSTEM
        success = self._test_single_mode(mode)
        
        self.assertTrue(success, f"{mode.value} 模式测试失败")
        print(f"✓ {mode.value} 模式测试通过")
    
    def _test_single_mode(self, mode: SchedulingMode) -> bool:
        """测试单个调度模式"""
        try:
            # 创建模式特定的模型
            model = self.manager.create_optimized_model(mode, self.data_generator.time_index)
            self.assertIsNotNone(model)
            self.assertIsInstance(model, OptimizedVPPModel)
            
            # 创建能源系统
            energy_system = model.create_energy_system(
                self.load_data, self.pv_data, self.wind_data, self.price_data
            )
            self.assertIsNotNone(energy_system)
            
            # 验证系统
            validation_success = model.validate_system()
            self.assertTrue(validation_success, f"{mode.value} 系统验证失败")
            
            # 获取系统概要
            summary = model.get_mode_summary()
            self.assertIsNotNone(summary)
            self.assertIn('scheduling_mode', summary)
            self.assertEqual(summary['scheduling_mode'], mode.value)
            
            print(f"    - 组件总数: {summary.get('total_components', 0)}")
            print(f"    - 包含资源: {', '.join(summary.get('included_resources', []))}")
            
            # 测试资源配置
            resources = self.manager.get_mode_resources(mode)
            self.assertIsInstance(resources, dict)
            
            expected_resources = self._get_expected_resources(mode)
            for resource, expected in expected_resources.items():
                self.assertEqual(resources.get(resource, False), expected, 
                               f"{mode.value} 模式中 {resource} 资源配置不正确")
            
            return True
            
        except Exception as e:
            print(f"    ❌ {mode.value} 模式测试失败: {str(e)}")
            return False
    
    def _get_expected_resources(self, mode: SchedulingMode) -> Dict[str, bool]:
        """获取调度模式预期的资源配置"""
        expected = {
            SchedulingMode.RENEWABLE_STORAGE: {
                'photovoltaic': True,
                'wind': True,
                'gas_turbine': False,
                'battery_storage': True,
                'adjustable_loads': False,
                'ancillary_services': False
            },
            SchedulingMode.ADJUSTABLE_STORAGE: {
                'photovoltaic': False,
                'wind': False,
                'gas_turbine': False,
                'battery_storage': True,
                'adjustable_loads': True,
                'ancillary_services': False
            },
            SchedulingMode.TRADITIONAL: {
                'photovoltaic': True,
                'wind': True,
                'gas_turbine': True,
                'battery_storage': True,
                'adjustable_loads': True,
                'ancillary_services': False
            },
            SchedulingMode.NO_RENEWABLE: {
                'photovoltaic': False,
                'wind': False,
                'gas_turbine': True,
                'battery_storage': True,
                'adjustable_loads': True,
                'ancillary_services': False
            },
            SchedulingMode.STORAGE_ONLY: {
                'photovoltaic': False,
                'wind': False,
                'gas_turbine': False,
                'battery_storage': True,
                'adjustable_loads': False,
                'ancillary_services': False
            },
            SchedulingMode.FULL_SYSTEM: {
                'photovoltaic': True,
                'wind': True,
                'gas_turbine': True,
                'battery_storage': True,
                'adjustable_loads': True,
                'ancillary_services': True
            }
        }
        
        return expected.get(mode, {})
    
    def test_mode_descriptions(self):
        """测试模式描述功能"""
        print(f"\n📝 测试模式描述功能...")
        
        for mode in SchedulingMode:
            # 测试模式描述
            description = self.manager.get_mode_description(mode)
            self.assertIsInstance(description, str)
            self.assertGreater(len(description), 0)
            
            # 测试目标函数描述
            objective = self.manager.get_objective_function_description(mode)
            self.assertIsInstance(objective, str)
            self.assertGreater(len(objective), 0)
            
            print(f"  • {mode.value}:")
            print(f"    描述: {description}")
            print(f"    目标: {objective}")
        
        print("✓ 所有模式描述测试通过")


class VPPSchedulingModesPerformanceTest:
    """虚拟电厂调度模式性能测试"""
    
    def __init__(self):
        self.manager = VPPSchedulingManager()
        self.data_generator = VPPDataGenerator()
        self.load_data, self.pv_data, self.wind_data, self.price_data = \
            self.data_generator.generate_all_data()
    
    def run_performance_test(self):
        """运行性能测试"""
        print(f"\n{'='*80}")
        print("虚拟电厂调度模式性能测试")
        print(f"{'='*80}")
        
        results = {}
        
        for mode in SchedulingMode:
            print(f"\n🏃 测试 {mode.value} 模式性能...")
            
            start_time = time.time()
            
            try:
                # 创建模型
                model = self.manager.create_optimized_model(mode, self.data_generator.time_index)
                
                # 创建能源系统
                energy_system = model.create_energy_system(
                    self.load_data, self.pv_data, self.wind_data, self.price_data
                )
                
                # 验证系统
                validation_success = model.validate_system()
                
                if validation_success:
                    summary = model.get_mode_summary()
                    
                    creation_time = time.time() - start_time
                    
                    results[mode] = {
                        'creation_time': creation_time,
                        'components_count': summary.get('total_components', 0),
                        'success': True
                    }
                    
                    print(f"  ✓ 创建时间: {creation_time:.3f} 秒")
                    print(f"  ✓ 组件数量: {summary.get('total_components', 0)}")
                else:
                    results[mode] = {'success': False}
                    print(f"  ❌ 系统验证失败")
                
            except Exception as e:
                results[mode] = {'success': False, 'error': str(e)}
                print(f"  ❌ 测试失败: {str(e)}")
        
        self._print_performance_summary(results)
        return results
    
    def _print_performance_summary(self, results: Dict):
        """打印性能测试摘要"""
        print(f"\n{'='*80}")
        print("性能测试摘要")
        print(f"{'='*80}")
        
        print(f"{'模式':<20} {'状态':<10} {'创建时间(秒)':<12} {'组件数量':<10}")
        print("-" * 55)
        
        for mode, result in results.items():
            if result.get('success', False):
                status = "✓ 成功"
                creation_time = result.get('creation_time', 0)
                components = result.get('components_count', 0)
                print(f"{mode.value:<20} {status:<10} {creation_time:<11.3f} {components:<10}")
            else:
                status = "❌ 失败"
                print(f"{mode.value:<20} {status:<10} {'N/A':<12} {'N/A':<10}")


def run_comprehensive_test():
    """运行综合测试"""
    print("🚀 启动虚拟电厂调度模式综合测试...")
    
    # 单元测试
    print(f"\n{'='*80}")
    print("第1部分: 单元测试")
    print(f"{'='*80}")
    
    test_suite = unittest.TestSuite()
    test_loader = unittest.TestLoader()
    test_suite.addTests(test_loader.loadTestsFromTestCase(TestVPPSchedulingModes))
    
    runner = unittest.TextTestRunner(verbosity=2)
    test_result = runner.run(test_suite)
    
    # 性能测试
    print(f"\n{'='*80}")
    print("第2部分: 性能测试")
    print(f"{'='*80}")
    
    performance_tester = VPPSchedulingModesPerformanceTest()
    performance_results = performance_tester.run_performance_test()
    
    # 测试总结
    print(f"\n{'='*80}")
    print("测试总结")
    print(f"{'='*80}")
    
    total_tests = test_result.testsRun
    failures = len(test_result.failures)
    errors = len(test_result.errors)
    
    performance_success = sum(1 for r in performance_results.values() if r.get('success', False))
    performance_total = len(performance_results)
    
    print(f"单元测试: {total_tests - failures - errors}/{total_tests} 通过")
    print(f"性能测试: {performance_success}/{performance_total} 通过")
    
    if failures == 0 and errors == 0 and performance_success == performance_total:
        print("\n🎉 所有测试通过！虚拟电厂调度模式系统运行正常。")
        return True
    else:
        print(f"\n❌ 部分测试失败。失败数: {failures}, 错误数: {errors}, 性能测试失败数: {performance_total - performance_success}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="虚拟电厂调度模式测试程序")
    parser.add_argument("--unit-test", action="store_true", help="仅运行单元测试")
    parser.add_argument("--performance", action="store_true", help="仅运行性能测试")
    parser.add_argument("--mode", choices=[mode.value for mode in SchedulingMode], 
                       help="测试指定的调度模式")
    
    args = parser.parse_args()
    
    if args.unit_test:
        # 仅运行单元测试
        unittest.main(argv=[''], exit=False, verbosity=2)
    elif args.performance:
        # 仅运行性能测试
        tester = VPPSchedulingModesPerformanceTest()
        tester.run_performance_test()
    elif args.mode:
        # 测试指定模式
        tester = TestVPPSchedulingModes()
        tester.setUp()
        mode = SchedulingMode(args.mode)
        success = tester._test_single_mode(mode)
        print(f"\n{'✓' if success else '❌'} {mode.value} 模式测试{'通过' if success else '失败'}")
    else:
        # 运行综合测试
        run_comprehensive_test()