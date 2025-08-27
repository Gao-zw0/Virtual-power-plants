"""
文件整理工具
File Organization Tool

帮助整理和管理散乱的虚拟电厂项目文件
"""

import os
import shutil
import glob
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set
import re

from src.utils.file_manager import VPPFileManager, SessionContext
from src.models.scheduling_modes import SchedulingMode, OptimizationObjective


class VPPFileOrganizer:
    """虚拟电厂文件整理器"""
    
    def __init__(self, base_dir: str = "outputs"):
        self.base_dir = Path(base_dir)
        self.file_manager = VPPFileManager(base_dir)
        
    def scan_legacy_files(self) -> Dict[str, List[str]]:
        """扫描旧的散乱文件"""
        legacy_files = {
            'csv_files': [],
            'txt_files': [],
            'png_files': [],
            'old_directories': []
        }
        
        # 扫描CSV文件
        for csv_file in self.base_dir.glob("*.csv"):
            if csv_file.is_file():
                legacy_files['csv_files'].append(str(csv_file))
        
        # 扫描TXT文件
        for txt_file in self.base_dir.glob("*.txt"):
            if txt_file.is_file():
                legacy_files['txt_files'].append(str(txt_file))
        
        # 扫描PNG文件
        for png_file in self.base_dir.glob("*.png"):
            if png_file.is_file():
                legacy_files['png_files'].append(str(png_file))
        
        # 扫描旧目录结构
        for item in self.base_dir.iterdir():
            if item.is_dir() and self._is_legacy_directory(item):
                legacy_files['old_directories'].append(str(item))
        
        return legacy_files
    
    def _is_legacy_directory(self, dir_path: Path) -> bool:
        """判断是否为旧的目录结构"""
        dir_name = dir_path.name
        
        # 新格式: {mode}_{objective}_{timestamp}
        # 旧格式: mode_xxx, plots, reports等
        if dir_name in ['plots', 'reports']:  # 不包括archive目录
            return True
        
        # 检查是否为旧的mode_xxx格式
        if dir_name.startswith('mode_') and dir_name.count('_') < 3:
            return True
        
        return False
    
    def organize_files(self, dry_run: bool = True) -> Dict[str, int]:
        """整理文件"""
        stats = {
            'files_organized': 0,
            'directories_created': 0,
            'files_archived': 0
        }
        
        legacy_files = self.scan_legacy_files()
        
        if dry_run:
            print("🔍 文件整理预览（不会实际移动文件）:")
            self._preview_organization(legacy_files)
            return stats
        
        # 创建归档目录
        archive_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_dir = self.base_dir / "archive" / f"legacy_cleanup_{archive_timestamp}"
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # 归档散乱文件
        for file_type, files in legacy_files.items():
            if files:
                type_archive_dir = archive_dir / file_type
                type_archive_dir.mkdir(exist_ok=True)
                
                for file_path in files:
                    source = Path(file_path)
                    if source.exists():
                        target = type_archive_dir / source.name
                        shutil.move(str(source), str(target))
                        stats['files_archived'] += 1
        
        print(f"✓ 文件整理完成，已归档 {stats['files_archived']} 个文件到 {archive_dir}")
        return stats
    
    def _preview_organization(self, legacy_files: Dict[str, List[str]]):
        """预览文件整理"""
        total_files = sum(len(files) for files in legacy_files.values())
        
        print(f"发现 {total_files} 个需要整理的文件:")
        
        for file_type, files in legacy_files.items():
            if files:
                print(f"\n📁 {file_type}:")
                for file_path in files[:5]:  # 只显示前5个
                    print(f"  - {Path(file_path).name}")
                if len(files) > 5:
                    print(f"  ... 还有 {len(files) - 5} 个文件")
    
    def create_demo_session(self):
        """创建示例会话目录"""
        print("🎯 创建示例会话目录...")
        
        # 创建一个示例会话
        with SessionContext(
            self.file_manager,
            SchedulingMode.FULL_SYSTEM,
            OptimizationObjective.PROFIT_MAXIMIZATION
        ) as session:
            
            # 创建示例文件
            import pandas as pd
            
            # 示例输入数据
            demo_data = pd.DataFrame({
                'load_demand_mw': [50, 45, 40],
                'pv_generation_mw': [0, 10, 20],
                'wind_generation_mw': [15, 12, 8],
                'electricity_price_yuan_mwh': [400, 350, 300]
            })
            session.save_file('input_data', 'demo_input.csv', demo_data)
            
            # 示例结果数据
            demo_results = pd.DataFrame({
                'load_demand_mw': [50, 45, 40],
                'total_supply_mw': [50, 45, 40],
                'grid_purchase_mw': [35, 23, 12]
            })
            session.save_file('optimization_results', 'demo_results.csv', demo_results)
            
            # 示例报告
            demo_report = """
虚拟电厂优化结果示例报告
==============================

这是一个示例报告，展示新的文件管理系统的功能。

关键指标:
- 总负荷: 135.0 MWh
- 可再生能源渗透率: 15.6%
- 净运行成本: 123,456 元

系统运行正常。
"""
            session.save_file('summary_report', 'demo_report.txt', demo_report)
            
            print(f"✓ 示例会话已创建: {session.session_dir}")
    
    def list_all_sessions(self):
        """列出所有会话"""
        sessions = self.file_manager.list_sessions()
        
        if not sessions:
            print("📁 没有找到会话目录")
            return
        
        print(f"📁 发现 {len(sessions)} 个会话目录:")
        print(f"{'会话名称':<40} {'模式':<20} {'目标':<20} {'时间'}")
        print("-" * 90)
        
        for session in sessions:
            print(f"{session['directory']:<40} {session['mode']:<20} {session['objective']:<20} {session['timestamp']}")


def main():
    """主函数"""
    print("🗂️  虚拟电厂文件整理工具")
    print("=" * 50)
    
    organizer = VPPFileOrganizer()
    
    # 扫描当前文件状况
    print("\n1. 扫描当前文件状况...")
    legacy_files = organizer.scan_legacy_files()
    total_files = sum(len(files) for files in legacy_files.values())
    
    if total_files == 0:
        print("✓ 没有发现需要整理的文件")
    else:
        print(f"发现 {total_files} 个需要整理的文件")
        
        # 预览整理
        print("\n2. 预览文件整理...")
        organizer.organize_files(dry_run=True)
        
        # 询问是否执行整理
        while True:
            choice = input("\n是否执行文件整理？(y/n): ").strip().lower()
            if choice in ['y', 'yes']:
                print("\n3. 执行文件整理...")
                stats = organizer.organize_files(dry_run=False)
                break
            elif choice in ['n', 'no']:
                print("已取消文件整理")
                break
            else:
                print("请输入 y 或 n")
    
    # 创建示例会话
    print("\n4. 创建示例会话...")
    organizer.create_demo_session()
    
    # 列出所有会话
    print("\n5. 当前会话列表:")
    organizer.list_all_sessions()
    
    print("\n✅ 文件整理工具运行完成！")


if __name__ == "__main__":
    main()