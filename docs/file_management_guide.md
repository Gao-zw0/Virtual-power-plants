# 虚拟电厂项目文件管理系统使用指南

## 🎯 概述

本项目已实现**统一的文件管理系统**，按照**调度模式**、**优化目标**和**时间戳**来组织所有生成的文件和结果，确保项目文件的有序管理和便于查找。

## 📁 新的文件组织结构

### 会话目录命名规则
```
{调度模式}_{优化目标}_{时间戳}
```
例如：`adjustable_storage_cost_minimization_20250827_134718`

### 标准目录结构
```
outputs/
├── {mode}_{objective}_{timestamp}/          # 会话目录
│   ├── data/                               # 输入数据
│   │   └── input_data.csv                  # 模拟数据
│   ├── results/                            # 优化结果
│   │   └── optimization_results.csv        # 时间序列结果
│   ├── economics/                          # 经济性分析
│   │   └── economics_analysis.csv          # 经济指标
│   ├── metrics/                            # 技术指标
│   │   └── technical_metrics.csv           # 技术性能指标
│   ├── plots/                              # 可视化图表
│   │   └── optimization_results.png        # 结果图表
│   ├── reports/                            # 报告文件
│   │   ├── summary_report.txt              # 汇总报告
│   │   └── mode_summary_report.txt         # 模式总结报告
│   ├── comparisons/                        # 对比分析（批量运行时）
│   ├── logs/                               # 日志文件
│   └── session_manifest.json               # 会话清单
└── archive/                                # 历史文件归档
    └── legacy_cleanup_{timestamp}/         # 旧文件归档
```

## 🔧 使用方法

### 1. 运行单个分析
```bash
python main.py
```
按提示选择：
1. **优化目标**（5种可选）
2. **调度模式**（6种可选）

### 2. 批量对比分析
在调度模式选择时输入 `7` 或 `all`，将运行所有模式进行对比。

### 3. 文件整理工具
```bash
python organize_files.py
```
- 自动扫描和整理散乱文件
- 将旧文件归档到 `archive/` 目录
- 创建示例会话目录

## 📊 文件类型说明

### 🗂️ 输入数据文件 (data/)
- **input_data.csv**: 包含负荷需求、光伏发电、风力发电、电价数据

### 📈 结果数据文件 (results/)
- **optimization_results.csv**: 每个时间段的详细优化结果，包含所有设备的运行状态

### 💰 经济分析文件 (economics/)
- **economics_analysis.csv**: 成本分解、收入计算、净成本等经济指标

### ⚡ 技术指标文件 (metrics/)
- **technical_metrics.csv**: 负荷率、可再生能源渗透率、储能效率等技术性能指标

### 📝 报告文件 (reports/)
- **summary_report.txt**: 标准汇总报告
- **mode_summary_report.txt**: 包含调度模式详细信息的总结报告

### 📊 图表文件 (plots/)
- **optimization_results.png**: 包含6个子图的综合分析图表

### 📋 会话清单 (session_manifest.json)
记录会话的完整信息，包括：
- 会话基本信息（模式、目标、时间）
- 文件结构清单
- 元数据

## 🎛️ 调度模式说明

| 模式 | 英文名称 | 包含资源 | 适用场景 |
|------|---------|----------|----------|
| 可再生+储能 | `renewable_storage` | 光伏+风电+储能 | 绿色能源园区 |
| 可调负荷+储能 | `adjustable_storage` | 冷机+热机+储能 | 工业园区需求侧管理 |
| 传统调度 | `traditional` | 除辅助服务外所有资源 | 常规电力系统 |
| 无可再生能源 | `no_renewable` | 燃气机组+储能+可调负荷 | 传统电网环境 |
| 纯储能 | `storage_only` | 仅储能系统 | 储能电站运营 |
| 完整系统 | `full_system` | 所有资源+辅助服务 | 综合能源系统 |

## 🎯 优化目标说明

| 目标 | 英文名称 | 优化重点 | 适用场景 |
|------|---------|----------|----------|
| 成本最小化 | `cost_minimization` | 最小化运行成本 | 传统电力系统 |
| 收益最大化 | `revenue_maximization` | 最大化售电和服务收入 | 市场化环境 |
| 利润最大化 | `profit_maximization` | 最大化收支差 | 商业化运营 |
| 辅助服务收益最大化 | `ancillary_revenue_max` | 最大化辅助服务收入 | 储能运营商 |
| 电网支撑优化 | `grid_support_optimized` | 平衡收益与电网稳定性 | 公用事业 |

## 📋 示例会话内容

### 会话名称示例
- `full_system_profit_maximization_20250827_134647`
- `renewable_storage_cost_minimization_20250827_140215`
- `adjustable_storage_ancillary_revenue_max_20250827_141230`

### 关键指标输出
```
📊 关键指标:
  - 总负荷: 1259.8 MWh
  - 可再生能源渗透率: 0.0%
  - 自给自足率: 0.0%
  - 净运行成本: 609,765 元
  - 平均供电成本: 484.03 元/MWh
```

## 🛠️ 高级功能

### 1. 会话查看
运行 `python organize_files.py` 可以：
- 查看所有历史会话
- 显示会话统计信息
- 创建示例会话

### 2. 文件归档
旧的散乱文件会自动归档到：
```
outputs/archive/legacy_cleanup_{timestamp}/
├── csv_files/          # 散乱的CSV文件
├── txt_files/          # 散乱的TXT文件  
├── png_files/          # 散乱的图片文件
└── old_directories/    # 旧的目录结构
```

### 3. 会话清单
每个会话都包含 `session_manifest.json`，记录：
- 会话创建时间
- 调度模式和优化目标
- 完整的文件结构清单
- 文件数量统计

## 🚀 最佳实践

### 1. 命名约定
- 调度模式使用下划线分隔的英文小写
- 优化目标使用描述性英文名称  
- 时间戳格式：`YYYYMMDD_HHMMSS`

### 2. 文件管理
- 定期运行 `organize_files.py` 清理散乱文件
- 利用会话目录进行项目结果分类
- 保留 `session_manifest.json` 用于追溯

### 3. 结果分析
- 使用会话目录比较不同配置的结果
- 利用批量运行功能生成对比报告
- 关注关键指标的变化趋势

## 📞 技术支持

- 文件管理器代码位置：`src/utils/file_manager.py`
- 文件整理工具：`organize_files.py`
- 主程序集成：`main.py` 已完全集成新的文件管理系统

---

**版本**: v3.0  
**更新日期**: 2025-08-27  
**新增功能**: 统一文件管理系统  
**关键改进**: 按模式+目标+时间的标准化文件组织