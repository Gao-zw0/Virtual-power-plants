"""
虚拟电厂数据生成器
VPP Data Generator

生成虚拟电厂优化调度所需的各类时间序列数据
"""

import os
import numpy as np
import pandas as pd
import yaml
from typing import Dict, Tuple, Optional
from scipy.interpolate import interp1d


class VPPDataGenerator:
    """虚拟电厂数据生成器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化数据生成器
        
        Args:
            config_path: 配置文件路径，如果为None则使用默认配置
        """
        self.config = self._load_config(config_path)
        self.periods = self.config['time_settings']['periods']
        self.time_index = self._create_time_index()
        
        # 设置随机种子确保结果可重现
        np.random.seed(self.config.get('random_seed', 42))
        
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """加载配置文件"""
        if config_path is None:
            # 使用默认配置路径
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'config', 'system_config.yaml'
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            return config
        except FileNotFoundError:
            print(f"配置文件未找到: {config_path}，使用默认配置")
            return self._get_default_config()
        except Exception as e:
            print(f"加载配置文件失败: {e}，使用默认配置")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict:
        """获取默认配置"""
        return {
            'time_settings': {
                'periods': 24,
                'start_date': '2024-01-01',
                'frequency': 'H'
            },
            'load_profile': {
                'base_load_pattern': [45, 42, 40, 38, 37, 39, 42, 48, 55, 60, 
                                     65, 68, 70, 72, 70, 68, 66, 65, 62, 58, 
                                     55, 52, 48, 46],
                'load_uncertainty': 0.02
            },
            'renewable_patterns': {
                'pv_pattern': [0, 0, 0, 0, 0, 0, 0.05, 0.15, 0.35, 0.55,
                              0.75, 0.85, 0.90, 0.95, 0.90, 0.80, 0.65, 0.45,
                              0.25, 0.10, 0.02, 0, 0, 0],
                'weather_uncertainty': {
                    'mean': 0.9,
                    'std': 0.1,
                    'min': 0.3,
                    'max': 1.0
                }
            },
            'electricity_prices': {
                'base_price_pattern': [300, 280, 260, 250, 250, 270, 320, 380, 420, 450,
                                      480, 500, 520, 540, 530, 510, 480, 460, 440, 420,
                                      400, 370, 340, 320],
                'price_volatility': 0.05
            },
            'energy_resources': {
                'photovoltaic': {'capacity_mw': 50},
                'wind': {'capacity_mw': 30}
            },
            'random_seed': 42
        }
    
    def _create_time_index(self) -> pd.DatetimeIndex:
        """创建时间索引"""
        start_date = self.config['time_settings']['start_date']
        frequency = self.config['time_settings']['frequency']
        
        return pd.date_range(
            start=start_date, 
            periods=self.periods, 
            freq=frequency
        )
    
    def _interpolate_pattern(self, pattern: list, target_periods: int) -> np.ndarray:
        """插值扩展模式到目标时间段数"""
        if len(pattern) == target_periods:
            return np.array(pattern)
        
        # 使用三次样条插值
        f = interp1d(
            np.linspace(0, 1, len(pattern)), 
            pattern, 
            kind='cubic',
            bounds_error=False,
            fill_value='extrapolate'
        )
        
        return f(np.linspace(0, 1, target_periods))
    
    def generate_load_profile(self) -> pd.Series:
        """
        生成负荷需求曲线数据
        
        Returns:
            负荷需求时间序列 (MW)
        """
        # 获取基础负荷模式
        base_pattern = self.config['load_profile']['base_load_pattern']
        uncertainty = self.config['load_profile']['load_uncertainty']
        
        # 插值到目标时间段
        load_pattern = self._interpolate_pattern(base_pattern, self.periods)
        
        # 添加随机不确定性
        noise = np.random.normal(0, uncertainty, self.periods)
        load_profile = load_pattern * (1 + noise)
        
        # 确保负荷为正值
        load_profile = np.maximum(load_profile, load_pattern * 0.5)
        
        return pd.Series(
            load_profile, 
            index=self.time_index, 
            name='load_demand_mw'
        )
    
    def generate_pv_profile(self) -> pd.Series:
        """
        生成光伏发电出力曲线数据
        
        Returns:
            光伏发电时间序列 (MW)
        """
        # 获取光伏出力模式和配置
        pv_pattern = self.config['renewable_patterns']['pv_pattern']
        weather_config = self.config['renewable_patterns']['weather_uncertainty']
        pv_capacity = self.config['energy_resources']['photovoltaic']['capacity_mw']
        
        # 插值到目标时间段
        pv_normalized = self._interpolate_pattern(pv_pattern, self.periods)
        
        # 应用装机容量
        pv_output = pv_normalized * pv_capacity
        
        # 添加天气不确定性
        weather_factor = np.random.normal(
            weather_config['mean'], 
            weather_config['std'], 
            self.periods
        )
        weather_factor = np.clip(
            weather_factor, 
            weather_config['min'], 
            weather_config['max']
        )
        
        pv_output = pv_output * weather_factor
        
        # 确保出力非负
        pv_output = np.maximum(pv_output, 0)
        
        return pd.Series(
            pv_output, 
            index=self.time_index, 
            name='pv_generation_mw'
        )
    
    def generate_wind_profile(self) -> pd.Series:
        """
        生成风电发电出力曲线数据
        
        Returns:
            风电发电时间序列 (MW)
        """
        wind_capacity = self.config['energy_resources']['wind']['capacity_mw']
        
        # 使用Weibull分布模拟风速特性
        shape_parameter = 2.0  # Weibull形状参数
        wind_normalized = np.random.weibull(shape_parameter, self.periods)
        
        # 标准化到0-1范围并限制最大值
        wind_normalized = np.clip(wind_normalized * 0.6, 0, 1)
        
        # 应用装机容量
        wind_output = wind_normalized * wind_capacity
        
        return pd.Series(
            wind_output, 
            index=self.time_index, 
            name='wind_generation_mw'
        )
    
    def generate_electricity_prices(self) -> pd.Series:
        """
        生成电力市场价格数据
        
        Returns:
            电价时间序列 (元/MWh)
        """
        # 获取电价配置
        price_pattern = self.config['electricity_prices']['base_price_pattern']
        volatility = self.config['electricity_prices']['price_volatility']
        
        # 插值到目标时间段
        prices = self._interpolate_pattern(price_pattern, self.periods)
        
        # 添加价格波动
        price_volatility = np.random.normal(1, volatility, self.periods)
        prices = prices * price_volatility
        
        # 确保价格为正值
        prices = np.maximum(prices, np.array(price_pattern).min() * 0.5)
        
        return pd.Series(
            prices, 
            index=self.time_index, 
            name='electricity_price_yuan_mwh'
        )
    
    def generate_all_data(self) -> Tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
        """
        生成所有数据
        
        Returns:
            Tuple[负荷数据, 光伏数据, 风电数据, 电价数据]
        """
        print("正在生成虚拟电厂数据...")
        
        load_data = self.generate_load_profile()
        pv_data = self.generate_pv_profile()
        wind_data = self.generate_wind_profile()
        price_data = self.generate_electricity_prices()
        
        print(f"数据生成完成！时间段: {self.periods} 小时")
        print(f"负荷范围: {load_data.min():.1f} - {load_data.max():.1f} MW")
        print(f"光伏出力范围: {pv_data.min():.1f} - {pv_data.max():.1f} MW")
        print(f"风电出力范围: {wind_data.min():.1f} - {wind_data.max():.1f} MW")
        print(f"电价范围: {price_data.min():.1f} - {price_data.max():.1f} 元/MWh")
        
        return load_data, pv_data, wind_data, price_data
    
    def save_data(self, output_dir: str = "outputs") -> str:
        """
        保存生成的数据到文件
        
        Args:
            output_dir: 输出目录
            
        Returns:
            保存的文件路径
        """
        # 生成所有数据
        load_data, pv_data, wind_data, price_data = self.generate_all_data()
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 合并数据到DataFrame
        data_df = pd.DataFrame({
            'load_demand_mw': load_data,
            'pv_generation_mw': pv_data,
            'wind_generation_mw': wind_data,
            'electricity_price_yuan_mwh': price_data
        })
        
        # 保存到CSV文件
        timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
        filename = f"vpp_input_data_{timestamp}.csv"
        filepath = os.path.join(output_dir, filename)
        
        data_df.to_csv(filepath, index=True, encoding='utf-8-sig')
        
        print(f"数据已保存到: {filepath}")
        return filepath


# 示例使用
if __name__ == "__main__":
    # 创建数据生成器
    generator = VPPDataGenerator()
    
    # 生成并保存数据
    filepath = generator.save_data()
    
    # 显示生成的数据
    load_data, pv_data, wind_data, price_data = generator.generate_all_data()
    
    print("\n数据预览:")
    print(f"时间范围: {generator.time_index[0]} 到 {generator.time_index[-1]}")
    print(f"总时间段: {len(generator.time_index)} 小时")