# 虚拟电厂优化调度建模说明

## 📋 目录
- [1. 建模概述](#1-建模概述)
- [2. 决策变量](#2-决策变量)
- [3. 目标函数](#3-目标函数)
- [4. 约束条件](#4-约束条件)
- [5. 模型特点](#5-模型特点)
- [6. 求解方法](#6-求解方法)

---

## 1. 建模概述

虚拟电厂优化调度问题是一个多时段、多资源的线性规划优化问题。系统目标是在满足电力平衡和设备运行约束的前提下，最小化系统总运行成本。

### 1.1 时间域设置
- **优化时长**: T = 24小时
- **时间步长**: Δt = 1小时
- **时间集合**: t ∈ {1, 2, ..., T}

### 1.2 资源类型
- **可再生能源**: 光伏发电、风力发电
- **传统机组**: 燃气轮机
- **储能系统**: 电池储能
- **可调负荷**: 冷机、热泵
- **电网交互**: 购电、售电

---

## 2. 决策变量

### 2.1 发电变量
- $P_{pv}(t)$ : 光伏发电功率 [MW]
- $P_{wind}(t)$ : 风力发电功率 [MW]
- $P_{gas}(t)$ : 燃气机组发电功率 [MW]
- $u_{gas}(t)$ : 燃气机组启停状态 {0,1}

### 2.2 储能变量
- $P_{bat}^{ch}(t)$ : 储能充电功率 [MW]
- $P_{bat}^{dis}(t)$ : 储能放电功率 [MW]
- $SOC(t)$ : 储能荷电状态 [%]
- $u_{ch}(t), u_{dis}(t)$ : 充放电状态变量 {0,1}

### 2.3 可调负荷变量
- $P_{chill}(t)$ : 冷机功率 [MW]
- $P_{heat}(t)$ : 热泵功率 [MW]

### 2.4 电网交互变量
- $P_{buy}(t)$ : 从电网购电功率 [MW]
- $P_{sell}(t)$ : 向电网售电功率 [MW]

---

## 3. 目标函数

### 3.1 总成本最小化目标

$$
\min Z = \sum_{t=1}^{T} \left[ C_{gen}(t) + C_{bat}(t) + C_{load}(t) + C_{grid}(t) \right]
$$

### 3.2 成本组成详解

#### 3.2.1 发电成本
$$
C_{gen}(t) = c_{pv} \cdot P_{pv}(t) + c_{wind} \cdot P_{wind}(t) + c_{gas} \cdot P_{gas}(t) + S_{gas} \cdot u_{gas}(t)
$$

其中：
- $c_{pv} = 5$ 元/MWh （光伏运维成本）
- $c_{wind} = 8$ 元/MWh （风电运维成本）
- $c_{gas} = 600$ 元/MWh （燃气变动成本）
- $S_{gas} = 10000$ 元 （燃气机组启动成本）

#### 3.2.2 储能成本
$$
C_{bat}(t) = c_{ch} \cdot P_{bat}^{ch}(t) + c_{dis} \cdot P_{bat}^{dis}(t)
$$

其中：
- $c_{ch} = 10$ 元/MWh （充电成本）
- $c_{dis} = 15$ 元/MWh （放电成本）

#### 3.2.3 可调负荷成本
$$
C_{load}(t) = c_{chill} \cdot P_{chill}(t) + c_{heat} \cdot P_{heat}(t)
$$

其中：
- $c_{chill} = 50$ 元/MWh （冷机运行成本）
- $c_{heat} = 40$ 元/MWh （热泵运行成本）

#### 3.2.4 电网交易成本
$$
C_{grid}(t) = c_{buy}(t) \cdot P_{buy}(t) - c_{sell}(t) \cdot P_{sell}(t)
$$

其中：
- $c_{buy}(t)$ : 分时购电价格 [元/MWh]
- $c_{sell}(t) = 0.95 \times c_{buy}(t)$ : 售电价格 [元/MWh]

---

## 4. 约束条件

### 4.1 电力平衡约束

#### 4.1.1 功率平衡
$$
P_{pv}(t) + P_{wind}(t) + P_{gas}(t) + P_{bat}^{dis}(t) + P_{buy}(t) = 
$$
$$
D(t) + P_{chill}(t) + P_{heat}(t) + P_{bat}^{ch}(t) + P_{sell}(t) \quad \forall t
$$

其中 $D(t)$ 为基础负荷需求。

### 4.2 设备容量约束

#### 4.2.1 可再生能源约束
$$
0 \leq P_{pv}(t) \leq P_{pv}^{max} \cdot CF_{pv}(t) \quad \forall t
$$
$$
0 \leq P_{wind}(t) \leq P_{wind}^{max} \cdot CF_{wind}(t) \quad \forall t
$$

其中：
- $P_{pv}^{max} = 50$ MW, $P_{wind}^{max} = 30$ MW
- $CF_{pv}(t), CF_{wind}(t)$ 为容量因子

#### 4.2.2 燃气机组约束
$$
P_{gas}^{min} \cdot u_{gas}(t) \leq P_{gas}(t) \leq P_{gas}^{max} \cdot u_{gas}(t) \quad \forall t
$$
$$
P_{gas}(t) - P_{gas}(t-1) \leq R_{up} \quad \forall t
$$
$$
P_{gas}(t-1) - P_{gas}(t) \leq R_{down} \quad \forall t
$$

其中：
- $P_{gas}^{max} = 100$ MW, $P_{gas}^{min} = 30$ MW
- $R_{up} = R_{down} = 30$ MW/h （爬坡速率）

### 4.3 储能系统约束

#### 4.3.1 功率约束
$$
0 \leq P_{bat}^{ch}(t) \leq P_{bat}^{max} \cdot u_{ch}(t) \quad \forall t
$$
$$
0 \leq P_{bat}^{dis}(t) \leq P_{bat}^{max} \cdot u_{dis}(t) \quad \forall t
$$
$$
u_{ch}(t) + u_{dis}(t) \leq 1 \quad \forall t
$$

#### 4.3.2 SOC约束
$$
SOC(t) = SOC(t-1) + \frac{\eta_{ch} \cdot P_{bat}^{ch}(t) - \frac{P_{bat}^{dis}(t)}{\eta_{dis}}}{E_{bat}^{max}} \cdot \Delta t \quad \forall t
$$
$$
SOC_{min} \leq SOC(t) \leq SOC_{max} \quad \forall t
$$
$$
SOC(0) = SOC_{init} = 0.5
$$

其中：
- $P_{bat}^{max} = 50$ MW, $E_{bat}^{max} = 200$ MWh
- $\eta_{ch} = \eta_{dis} = 0.95$
- $SOC_{min} = 0.2, SOC_{max} = 0.9$

### 4.4 可调负荷约束

#### 4.4.1 冷机约束
$$
P_{chill}^{min} \leq P_{chill}(t) \leq P_{chill}^{max} \quad \forall t
$$

其中：$P_{chill}^{max} = 20$ MW, $P_{chill}^{min} = 6$ MW

#### 4.4.2 热泵约束
$$
P_{heat}^{min} \leq P_{heat}(t) \leq P_{heat}^{max} \quad \forall t
$$

其中：$P_{heat}^{max} = 15$ MW, $P_{heat}^{min} = 3$ MW

### 4.5 电网交互约束

$$
0 \leq P_{buy}(t) \leq P_{buy}^{max} \quad \forall t
$$
$$
0 \leq P_{sell}(t) \leq P_{sell}^{max} \quad \forall t
$$

其中：$P_{buy}^{max} = 1000$ MW, $P_{sell}^{max} = 500$ MW

---

## 5. 模型特点

### 5.1 线性规划特性
- **变量类型**: 连续变量 + 二进制变量
- **目标函数**: 线性
- **约束条件**: 线性
- **模型规模**: 变量数 ≈ 200×T，约束数 ≈ 150×T

### 5.2 时间耦合
- **储能SOC**: 时间状态耦合
- **机组启停**: 启动成本时间耦合
- **爬坡约束**: 相邻时段功率耦合

### 5.3 不确定性处理
- **确定性优化**: 基于预测数据
- **鲁棒性**: 通过储能和可调负荷提供灵活性
- **滚动优化**: 实际应用中可采用滚动时域优化

---

## 6. 求解方法

### 6.1 求解器配置
- **主求解器**: CBC (Coin-or Branch and Cut)
- **问题类型**: MILP (Mixed Integer Linear Programming)
- **求解参数**:
  - 线程数: 4
  - 时间限制: 300秒
  - 最优性间隙: 1%

### 6.2 求解策略
```python
# CBC求解器配置
solver_options = {
    'threads': 4,
    'timeLimit': 300,
    'ratioGap': 0.01,
    'logLevel': 1
}
```

### 6.3 预处理技术
- **预求解**: 简化约束和变量
- **切割平面**: 提高求解效率
- **启发式算法**: 快速获得初始解

### 6.4 后处理分析
- **解的验证**: 检查约束满足情况
- **敏感性分析**: 关键参数影响分析
- **经济性评估**: 成本结构分析
- **技术指标**: 可再生能源利用率等

---

## 📊 典型求解结果

### 优化指标
- **求解时间**: 2-5秒
- **最优性间隙**: < 1%
- **可再生能源渗透率**: 49.1%
- **总运行成本**: 464,960元/天
- **可调负荷参与率**: 16.4%

### 关键洞察
1. **削峰填谷**: 储能系统有效平滑负荷曲线
2. **成本优化**: 可调负荷参与显著降低系统成本
3. **绿色调度**: 最大化可再生能源利用
4. **灵活响应**: 多元化资源提供系统调节能力

---

*本文档基于 oemof-solph 建模框架和 CBC 求解器实现的虚拟电厂优化调度系统。*