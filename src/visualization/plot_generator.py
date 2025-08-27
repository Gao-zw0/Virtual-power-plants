"""
可视化图表生成器
Plot Generator

生成虚拟电厂优化结果的可视化图表
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class PlotGenerator:
    """可视化图表生成器"""
    
    def __init__(self):
        """初始化图表生成器"""
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
        plt.rcParams['figure.figsize'] = (16, 12)
        
    def generate_all_plots(self, results_df: pd.DataFrame, economics: Dict, 
                          price_data: pd.Series, output_dir: str = "outputs/plots") -> str:
        """
        生成所有可视化图表
        
        Args:
            results_df: 结果数据框
            economics: 经济性分析
            price_data: 电价数据
            output_dir: 输出目录
            
        Returns:
            保存的图片文件路径
        """
        print("正在生成可视化图表...")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # 创建图表
        fig, axes = plt.subplots(3, 2, figsize=(16, 12))
        fig.suptitle('虚拟电厂调度优化结果分析', fontsize=16, fontweight='bold')
        
        # 1. 发电资源出力
        self._plot_generation_profile(axes[0, 0], results_df)
        
        # 2. 负荷与供应平衡
        self._plot_load_balance(axes[0, 1], results_df)
        
        # 3. 储能运行状态
        self._plot_battery_operation(axes[1, 0], results_df)
        
        # 4. 辅助服务
        self._plot_ancillary_services(axes[1, 1], results_df)
        
        # 5. 电价曲线
        self._plot_electricity_prices(axes[2, 0], price_data)
        
        # 6. 成本结构
        self._plot_cost_structure(axes[2, 1], economics)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图片
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vpp_optimization_results_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.show()
        
        print(f"图表已保存为: {filepath}")
        return filepath
    
    def generate_plots_to_session(self, results_df: pd.DataFrame, economics: Dict,
                                 price_data: pd.Series, session_context, 
                                 filename: str = "optimization_results.png") -> str:
        """
        生成图表并保存到会话目录
        
        Args:
            results_df: 结果数据框
            economics: 经济性分析
            price_data: 电价数据
            session_context: 会话上下文
            filename: 文件名
            
        Returns:
            保存的图片文件路径
        """
        print("正在生成可视化图表...")
        
        # 创建图表
        fig, axes = plt.subplots(3, 2, figsize=(16, 12))
        fig.suptitle('虚拟电厂调度优化结果分析', fontsize=16, fontweight='bold')
        
        # 1. 发电资源出力
        self._plot_generation_profile(axes[0, 0], results_df)
        
        # 2. 负荷与供应平衡
        self._plot_load_balance(axes[0, 1], results_df)
        
        # 3. 储能运行状态
        self._plot_battery_operation(axes[1, 0], results_df)
        
        # 4. 辅助服务
        self._plot_ancillary_services(axes[1, 1], results_df)
        
        # 5. 电价曲线
        self._plot_electricity_prices(axes[2, 0], price_data)
        
        # 6. 成本结构
        self._plot_cost_structure(axes[2, 1], economics)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存到会话目录
        plot_path = session_context.get_file_path('plots', filename)
        plt.savefig(plot_path, dpi=300, bbox_inches='tight')
        plt.close()  # 关闭图表以释放内存
        
        print(f"图表已保存为: {plot_path}")
        return str(plot_path)
    
    def _plot_generation_profile(self, ax, results_df):
        """绘制发电资源出力曲线"""
        time_index = results_df.index
        
        if 'pv_generation_mw' in results_df.columns:
            ax.plot(time_index, results_df['pv_generation_mw'], 
                   label='光伏发电', linewidth=2, color='orange')
        
        if 'wind_generation_mw' in results_df.columns:
            ax.plot(time_index, results_df['wind_generation_mw'], 
                   label='风力发电', linewidth=2, color='skyblue')
        
        if 'gas_generation_mw' in results_df.columns:
            ax.plot(time_index, results_df['gas_generation_mw'], 
                   label='燃气机组', linewidth=2, color='red')
        
        ax.set_title('可再生能源及传统能源出力', fontweight='bold')
        ax.set_ylabel('功率 (MW)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    def _plot_load_balance(self, ax, results_df):
        """绘制负荷与供应平衡"""
        time_index = results_df.index
        
        if 'load_demand_mw' in results_df.columns:
            ax.plot(time_index, results_df['load_demand_mw'], 
                   label='负荷需求', linewidth=2, color='black')
        
        if 'total_supply_mw' in results_df.columns:
            ax.plot(time_index, results_df['total_supply_mw'], 
                   label='总供应', linewidth=2, color='green', linestyle='--')
        
        ax.set_title('负荷需求与供应平衡', fontweight='bold')
        ax.set_ylabel('功率 (MW)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    def _plot_battery_operation(self, ax, results_df):
        """绘制储能运行状态"""
        time_index = results_df.index
        
        if 'battery_charge_mw' in results_df.columns and 'battery_discharge_mw' in results_df.columns:
            ax.bar(time_index, results_df['battery_charge_mw'], 
                  label='充电', color='blue', alpha=0.7, width=0.8)
            ax.bar(time_index, results_df['battery_discharge_mw'], 
                  label='放电', color='orange', alpha=0.7, width=0.8)
        
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax.set_title('储能系统充放电策略', fontweight='bold')
        ax.set_ylabel('功率 (MW)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    def _plot_ancillary_services(self, ax, results_df):
        """绘制辅助服务"""
        time_index = results_df.index
        
        # 检查是否有辅助服务数据
        has_ancillary_data = any(col in results_df.columns for col in 
                               ['freq_reg_up_mw', 'freq_reg_down_mw', 
                                'spin_reserve_up_mw', 'spin_reserve_down_mw'])
        
        if has_ancillary_data:
            # 绘制调频服务
            if 'freq_reg_up_mw' in results_df.columns:
                ax.plot(time_index, results_df['freq_reg_up_mw'], 
                       label='向上调频', linewidth=2, color='red', linestyle='--')
            
            if 'freq_reg_down_mw' in results_df.columns:
                ax.plot(time_index, results_df['freq_reg_down_mw'], 
                       label='向下调频', linewidth=2, color='blue', linestyle='--')
            
            # 绘制备用服务
            if 'spin_reserve_up_mw' in results_df.columns:
                ax.plot(time_index, results_df['spin_reserve_up_mw'], 
                       label='向上备用', linewidth=2, color='orange', linestyle='-.')
            
            if 'spin_reserve_down_mw' in results_df.columns:
                ax.plot(time_index, results_df['spin_reserve_down_mw'], 
                       label='向下备用', linewidth=2, color='green', linestyle='-.')
            
            ax.set_title('辅助服务提供策略', fontweight='bold')
        else:
            # 如果没有辅助服务数据，绘制可调负荷
            if 'chiller_load_mw' in results_df.columns:
                ax.plot(time_index, results_df['chiller_load_mw'], 
                       label='冷机负荷', linewidth=2, color='cyan')
            
            if 'heat_pump_load_mw' in results_df.columns:
                ax.plot(time_index, results_df['heat_pump_load_mw'], 
                       label='热机负荷', linewidth=2, color='orange')
            
            # 如果没有可调负荷数据，绘制电网交易
            if 'chiller_load_mw' not in results_df.columns and 'heat_pump_load_mw' not in results_df.columns:
                if 'grid_purchase_mw' in results_df.columns:
                    ax.plot(time_index, results_df['grid_purchase_mw'], 
                           label='购电', linewidth=2, color='red')
                
                if 'grid_sale_mw' in results_df.columns:
                    ax.plot(time_index, results_df['grid_sale_mw'], 
                           label='售电', linewidth=2, color='green')
                
                ax.set_title('电网交易策略', fontweight='bold')
            else:
                ax.set_title('可调负荷运行状态', fontweight='bold')
        
        ax.set_ylabel('功率 (MW)')
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _plot_adjustable_loads(self, ax, results_df):
        """绘制可调负荷（保留原有方法）"""
        time_index = results_df.index
        
        if 'chiller_load_mw' in results_df.columns:
            ax.plot(time_index, results_df['chiller_load_mw'], 
                   label='冷机负荷', linewidth=2, color='cyan')
        
        if 'heat_pump_load_mw' in results_df.columns:
            ax.plot(time_index, results_df['heat_pump_load_mw'], 
                   label='热机负荷', linewidth=2, color='orange')
        
        ax.set_title('可调负荷运行状态', fontweight='bold')
        ax.set_ylabel('功率 (MW)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    def _plot_grid_trading(self, ax, results_df):
        """绘制电网交易"""
        time_index = results_df.index
        
        if 'grid_purchase_mw' in results_df.columns:
            ax.plot(time_index, results_df['grid_purchase_mw'], 
                   label='购电', linewidth=2, color='red')
        
        if 'grid_sale_mw' in results_df.columns:
            ax.plot(time_index, results_df['grid_sale_mw'], 
                   label='售电', linewidth=2, color='green')
        
        ax.set_title('电网交易策略', fontweight='bold')
        ax.set_ylabel('功率 (MW)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    def _plot_electricity_prices(self, ax, price_data):
        """绘制电价曲线"""
        ax.plot(price_data.index, price_data.values, 
               label='电价', linewidth=2, color='purple')
        ax.set_title('电力市场价格', fontweight='bold')
        ax.set_ylabel('价格 (元/MWh)')
        ax.set_xlabel('时间')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
    def _plot_cost_structure(self, ax, economics):
        """绘制成本结构"""
        # 准备数据
        labels = []
        values = []
        colors = ['orange', 'skyblue', 'red', 'purple', 'cyan', 'gray']
        
        cost_items = [
            ('renewable_cost_yuan', '可再生能源'),
            ('gas_cost_yuan', '燃气发电'),
            ('battery_total_cost_yuan', '储能运行'),
            ('adjustable_loads_cost_yuan', '可调负荷'),
            ('grid_purchase_cost_yuan', '电网购电')
        ]
        
        # 添加辅助服务收入（作为负成本）
        ancillary_revenue = economics.get('ancillary_services_revenue_yuan', 0)
        if ancillary_revenue > 0:
            cost_items.append(('ancillary_services_revenue_yuan', '辅助服务收入'))
            colors.append('lightgreen')
        
        for key, label in cost_items:
            if key == 'ancillary_services_revenue_yuan':
                # 辅助服务收入作为负成本显示
                if key in economics and economics[key] > 0:
                    labels.append(f'辅助服务收入 (-{economics[key]:.0f}元)')
                    values.append(economics[key] * 0.3)  # 显示为较小的正值，以区分收入和成本
            elif key in economics and economics[key] > 0:
                labels.append(label)
                values.append(economics[key])
        
        if values:
            wedges, texts, autotexts = ax.pie(values, labels=labels, 
                                            colors=colors[:len(values)],
                                            autopct='%1.1f%%', startangle=90)
            ax.set_title('运行成本结构分析', fontweight='bold')
        else:
            ax.text(0.5, 0.5, '无成本数据', ha='center', va='center', 
                   transform=ax.transAxes, fontsize=12)
            ax.set_title('运行成本结构分析', fontweight='bold')


# 示例使用
if __name__ == "__main__":
    print("可视化模块已创建完成")