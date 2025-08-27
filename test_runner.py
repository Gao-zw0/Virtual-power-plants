"""
测试运行脚本
Test Runner Script

提供便捷的测试运行接口
"""

import os
import sys
import subprocess

def run_tests(test_type="all"):
    """运行测试"""
    project_root = os.path.dirname(os.path.abspath(__file__))
    test_runner = os.path.join(project_root, 'tests', 'run_tests.py')
    
    cmd = [sys.executable, test_runner, '--test', test_type]
    
    try:
        result = subprocess.run(cmd, cwd=project_root)
        return result.returncode == 0
    except Exception as e:
        print(f"运行测试失败: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="虚拟电厂测试运行器")
    parser.add_argument("--type", choices=[
        "basic", "cbc", "scheduling", "objectives", 
        "loads", "ancillary", "flow", "all"
    ], default="all", help="测试类型")
    
    args = parser.parse_args()
    
    print("🚀 启动虚拟电厂测试...")
    success = run_tests(args.type)
    
    if success:
        print("✅ 测试运行完成")
    else:
        print("❌ 测试运行失败")
        sys.exit(1)