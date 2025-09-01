# 虚拟电厂调度模式用户手册

## 目录
1. [概述](#概述)
2. [调度模式分类](#调度模式分类)
3. [模式详细说明](#模式详细说明)
4. [使用方法](#使用方法)
5. [性能对比分析](#性能对比分析)
6. [配置说明](#配置说明)
7. [常见问题](#常见问题)

## 概述

虚拟电厂调度优化系统支持6种不同的调度模式，根据参与优化调度的可调资源类型进行划分。每种模式针对不同的应用场景和业务需求，提供定制化的优化策略和目标函数。

### 系统特点
- **模块化设计**: 每种调度模式独立配置，互不干扰
- **灵活配置**: 支持资源组合的自由选择
- **多目标优化**: 针对不同场景的专用目标函数
- **性能对比**: 内置模式对比分析功能
- **可视化展示**: 自动生成分析图表和报告

## 调度模式分类

### 按可调资源类型分类

| 模式名称 | 可再生能源 | 传统发电 | 储能系统 | 可调负荷 | 辅助服务 | 适用场景 |
|---------|-----------|---------|----------|----------|----------|----------|
| renewable_storage | ✓ | ✗ | ✓ | ✗ | ✗ | 绿色能源园区 |
| adjustable_storage | ✗ | ✗ | ✓ | ✓ | ✗ | 工业园区需求侧管理 |
| traditional | ✓ | ✓ | ✓ | ✓ | ✗ | 常规电力系统调度 |
| no_renewable | ✗ | ✓ | ✓ | ✓ | ✗ | 传统电网环境 |
| storage_only | ✗ | ✗ | ✓ | ✗ | ✗ | 储能电站运营 |
| full_system | ✓ | ✓ | ✓ | ✓ | ✓ | 综合能源系统 |

### 按应用场景分类

#### 🌱 绿色能源应用
- **renewable_storage**: 纯绿色能源供电，适用于环保要求高的场景

#### 🏭 工业园区应用
- **adjustable_storage**: 重点关注需求侧管理和负荷调节
- **no_renewable**: 适用于可再生能源资源有限的地区

#### ⚡ 电力市场应用
- **storage_only**: 专门的储能电站运营优化
- **traditional**: 常规电力系统的调度优化

#### 🌐 综合系统应用
- **full_system**: 包含所有资源的完整系统优化

## 模式详细说明

### 1. renewable_storage - 可再生能源+储能模式

**资源配置**:
- ✅ 光伏发电系统 (50MW)
- ✅ 风力发电系统 (30MW)
- ✅ 电池储能系统 (50MW/200MWh)
- ❌ 传统发电机组
- ❌ 可调负荷
- ❌ 辅助服务

**目标函数**:
```
最小化: 储能运行成本 + 电网交易成本 - 可再生能源收益
```

**应用场景**:
- 绿色能源示范园区
- 新能源微电网
- 环保要求严格的区域
- 可再生能源消纳项目

**经济特点**:
- 净运行成本: ~23万元
- 平均供电成本: ~182元/MWh
- 可再生能源渗透率: 100%
- 自给自足率: ~53%

### 2. adjustable_storage - 可调负荷+储能模式

**资源配置**:
- ❌ 可再生能源
- ❌ 传统发电机组
- ✅ 电池储能系统 (50MW/200MWh)
- ✅ 冷机负荷 (20MW)
- ✅ 热机负荷 (15MW)
- ❌ 辅助服务

**目标函数**:
```
最小化: 可调负荷运行成本 + 储能运行成本 + 电网交易成本
```

**应用场景**:
- 工业园区能源管理
- 商业建筑群调度
- 需求响应项目
- 负荷聚合商业务

**经济特点**:
- 净运行成本: ~61万元
- 平均供电成本: ~484元/MWh
- 可调负荷参与率: 16.4%
- 需求侧调节能力: 35MW

### 3. traditional - 传统调度模式

**资源配置**:
- ✅ 光伏发电系统 (50MW)
- ✅ 风力发电系统 (30MW)
- ✅ 燃气机组 (100MW)
- ✅ 电池储能系统 (50MW/200MWh)
- ✅ 可调负荷 (35MW)
- ❌ 辅助服务

**目标函数**:
```
最小化: 发电成本 + 储能成本 + 可调负荷成本 + 电网交易成本
```

**应用场景**:
- 常规电力系统调度
- 分布式能源集成
- 多能源协调优化
- 电力现货市场参与

**经济特点**:
- 净运行成本: ~46.5万元
- 平均供电成本: ~369元/MWh
- 可再生能源渗透率: 49.1%
- 自给自足率: 100%

### 4. no_renewable - 无可再生能源模式

**资源配置**:
- ❌ 可再生能源
- ✅ 燃气机组 (100MW)
- ✅ 电池储能系统 (50MW/200MWh)
- ✅ 可调负荷 (35MW)
- ❌ 辅助服务

**目标函数**:
```
最小化: 传统发电成本 + 储能成本 + 可调负荷成本 + 电网交易成本
```

**应用场景**:
- 传统电网环境
- 可再生能源资源匮乏地区
- 电力系统过渡期
- 备用电源系统

**经济特点**:
- 净运行成本: ~74.9万元
- 平均供电成本: ~595元/MWh
- 自给自足率: 54.8%
- 传统发电依赖度高

### 5. storage_only - 纯储能调度模式

**资源配置**:
- ❌ 发电资源
- ✅ 电池储能系统 (50MW/200MWh)
- ❌ 可调负荷
- ❌ 辅助服务

**目标函数**:
```
最小化: 储能运行成本 + 电网交易成本
```

**应用场景**:
- 独立储能电站
- 电力系统调峰调频
- 电网侧储能项目
- 储能商业化运营

**经济特点**:
- 净运行成本: ~51.8万元
- 平均供电成本: ~411元/MWh
- 完全依赖电网供电
- 储能套利收益模式

### 6. full_system - 完整系统模式

**资源配置**:
- ✅ 光伏发电系统 (50MW)
- ✅ 风力发电系统 (30MW)
- ✅ 燃气机组 (100MW)
- ✅ 电池储能系统 (50MW/200MWh)
- ✅ 可调负荷 (35MW)
- ✅ 辅助服务 (调频+旋转备用)

**目标函数**:
```
最小化: 发电成本 + 储能成本 + 可调负荷成本 + 电网交易成本 - 辅助服务收益
```

**应用场景**:
- 综合能源系统
- 虚拟电厂运营
- 电力市场全面参与
- 多元化收益模式

**经济特点**:
- 净运行成本: ~46.5万元
- 平均供电成本: ~369元/MWh
- 辅助服务收益潜力
- 资源利用效率最高

## 使用方法

### 命令行接口

#### 1. 交互式模式选择
```bash
python main.py
```
系统将显示可用模式列表，用户可以选择要运行的模式。

#### 2. 指定模式运行
```bash
python main.py --mode=renewable_storage
python main.py --mode=adjustable_storage
python main.py --mode=traditional
python main.py --mode=no_renewable
python main.py --mode=storage_only
python main.py --mode=full_system
```

#### 3. 所有模式对比
```bash
python main.py --compare-all
```

#### 4. 查看可用模式
```bash
python main.py --list-modes
```

#### 5. 帮助信息
```bash
python main.py --help
```

### 程序化接口

```python
from src.models.scheduling_modes import VPPSchedulingManager, SchedulingMode
from src.data.data_generator import VPPDataGenerator

# 创建管理器和数据
manager = VPPSchedulingManager()
data_generator = VPPDataGenerator()
load_data, pv_data, wind_data, price_data = data_generator.generate_all_data()

# 创建特定模式的模型
model = manager.create_optimized_model(
    SchedulingMode.RENEWABLE_STORAGE, 
    data_generator.time_index
)

# 构建和求解系统
energy_system = model.create_energy_system(load_data, pv_data, wind_data, price_data)
# ... 执行优化求解 ...
```

## 性能对比分析

### 经济性对比

| 调度模式 | 净运行成本(万元) | 平均成本(元/MWh) | 成本排名 |
|---------|-----------------|-----------------|---------|
| renewable_storage | 23.0 | 182.37 | 🥇 最优 |
| traditional | 46.5 | 369.08 | 🥈 第二 |
| full_system | 46.5 | 369.08 | 🥈 第二 |
| storage_only | 51.8 | 410.96 | 第四 |
| adjustable_storage | 61.0 | 484.03 | 第五 |
| no_renewable | 74.9 | 594.80 | 🥉 最高 |

### 环保性对比

| 调度模式 | 可再生能源渗透率 | 碳排放相对水平 | 环保排名 |
|---------|-----------------|---------------|---------|
| renewable_storage | 100% | 最低 | 🥇 |
| traditional | 49.1% | 中等 | 🥈 |
| full_system | 49.1% | 中等 | 🥈 |
| adjustable_storage | 0% | 高 | 🥉 |
| storage_only | 0% | 高 | 🥉 |
| no_renewable | 0% | 最高 | 最差 |

### 灵活性对比

| 调度模式 | 供电可靠性 | 调节能力 | 灵活性排名 |
|---------|-----------|---------|-----------|
| full_system | 最高 | 最强 | 🥇 |
| traditional | 高 | 强 | 🥈 |
| no_renewable | 中等 | 中等 | 🥉 |
| adjustable_storage | 中等 | 中等 | 第四 |
| renewable_storage | 中等 | 弱 | 第五 |
| storage_only | 低 | 最弱 | 最差 |

## 配置说明

### 系统配置文件 (config/system_config.yaml)

#### 能源资源配置
```yaml
energy_resources:
  photovoltaic:
    capacity_mw: 50          # 光伏装机容量
    variable_cost_yuan_mwh: 5 # 光伏运维成本
  
  wind:
    capacity_mw: 30          # 风电装机容量
    variable_cost_yuan_mwh: 8 # 风电运维成本
  
  gas_turbine:
    capacity_mw: 100         # 燃气机组容量
    variable_cost_yuan_mwh: 600 # 燃气发电成本
    min_output_ratio: 0.3    # 最小出力比例
  
  battery_storage:
    power_capacity_mw: 50    # 储能功率容量
    energy_capacity_mwh: 200 # 储能能量容量
    charge_efficiency: 0.95  # 充电效率
    discharge_efficiency: 0.95 # 放电效率
```

#### 可调负荷配置
```yaml
adjustable_loads:
  chiller:
    rated_power_mw: 20       # 冷机额定功率
    operating_cost_yuan_mwh: 50 # 冷机运行成本
    min_power_ratio: 0.3     # 最小功率比例
  
  heat_pump:
    rated_power_mw: 15       # 热泵额定功率
    operating_cost_yuan_mwh: 40 # 热泵运行成本
    cop: 3.5                 # 制热系数
```

### 求解器配置文件 (config/solver_config.yaml)

```yaml
solver:
  name: "cbc"
  executable_path: "cbc/bin/cbc.exe"
  time_limit: 300          # 求解时间限制(秒)
  gap_tolerance: 0.01      # 收敛精度
  threads: 4               # 并行线程数
```

### 模式定制配置

每种调度模式都可以通过修改配置文件进行定制：

1. **资源容量调整**: 修改各资源的装机容量
2. **成本参数设置**: 调整各种成本和价格参数
3. **约束条件配置**: 设置运行约束和技术限制
4. **优化参数调节**: 调整求解器参数和收敛条件

## 输出文件说明

### 文件结构
```
outputs/
├── mode_{模式名称}/
│   ├── vpp_input_data_{时间戳}.csv           # 输入数据
│   ├── optimization_results_{时间戳}.csv     # 优化结果时间序列
│   ├── economics_analysis_{时间戳}.csv       # 经济性分析
│   ├── technical_metrics_{时间戳}.csv        # 技术指标
│   ├── mode_summary_report_{时间戳}.txt      # 模式汇总报告
│   └── plots/
│       └── vpp_optimization_results_{时间戳}.png # 可视化图表
└── modes_comparison_report_{时间戳}.txt       # 模式对比报告
```

### 关键输出指标

#### 经济性指标
- `net_cost_yuan`: 净运行成本
- `average_cost_yuan_per_mwh`: 平均供电成本
- `total_generation_cost_yuan`: 总发电成本
- `grid_purchase_cost_yuan`: 电网购电成本
- `ancillary_services_revenue_yuan`: 辅助服务收益

#### 技术指标
- `renewable_penetration_ratio`: 可再生能源渗透率
- `self_sufficiency_ratio`: 自给自足率
- `adjustable_load_ratio`: 可调负荷参与率
- `battery_round_trip_efficiency`: 储能充放电效率
- `supply_flexibility_index`: 供电灵活性指数

## 常见问题

### Q1: 如何选择合适的调度模式？

**A**: 根据以下因素选择：
- **资源条件**: 是否有可再生能源、储能系统等
- **应用场景**: 工业园区、绿色园区、储能电站等
- **经济目标**: 成本最小化、收益最大化、环保优先等
- **技术要求**: 供电可靠性、调节能力、响应速度等

### Q2: 为什么不同模式的运行成本差异很大？

**A**: 主要因素包括：
- **资源组合不同**: 可再生能源成本低，传统发电成本高
- **优化策略不同**: 不同模式的目标函数和约束条件不同
- **系统复杂度**: 资源越丰富，优化空间越大，成本越低
- **市场参与度**: 辅助服务等增值服务可以降低净成本

### Q3: 如何修改模式配置参数？

**A**: 可以通过以下方式：
1. **修改配置文件**: 直接编辑 `config/system_config.yaml`
2. **程序化配置**: 在代码中传入自定义配置参数
3. **模式继承定制**: 基于现有模式创建自定义模式

### Q4: 优化求解失败怎么办？

**A**: 检查以下方面：
1. **数据有效性**: 确保输入数据合理且无缺失
2. **约束可行性**: 检查约束条件是否过于严格
3. **求解器设置**: 调整时间限制、精度等参数
4. **系统配置**: 验证资源配置的合理性

### Q5: 如何解读优化结果？

**A**: 重点关注：
- **经济性**: 净运行成本、平均供电成本
- **技术性**: 可再生能源渗透率、自给自足率
- **可靠性**: 供电灵活性指数、功率平衡情况
- **环保性**: 碳排放水平、绿色能源使用比例

### Q6: 支持哪些扩展功能？

**A**: 系统支持：
- **自定义资源**: 添加新的发电或负荷资源
- **新增约束**: 实现特殊的技术或商业约束
- **目标函数定制**: 多目标优化、加权目标等
- **市场模型**: 不同电力市场机制的建模


---
