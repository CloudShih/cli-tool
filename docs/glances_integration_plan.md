# Glances 系统监控工具集成方案

## 项目概述

基于与 GEMINI AI 的技术协作，为 CLI Tool 项目设计 Glances 系统监控工具的完整集成方案。Glances 是一个跨平台的系统监控工具，支持 CPU、内存、磁盘、网络、进程监控。

## 技术架构决策

### 核心集成策略：Web API + Subprocess 回退

**选择理由：**
- **主要方式**：Glances Web API (http://localhost:61208/api/3)
  - 结构化 JSON 数据，易于解析
  - 丰富的 API 端点和指标
  - 解耦设计，更好的维护性
- **回退机制**：Subprocess 调用 `glances --stdout --json`
  - 用户未启动 web 服务器时的备选方案
  - 提供基本监控功能的保底选项

### MVC 架构设计

```
tools/glances/
├── __init__.py
├── plugin.py                 # 插件入口和接口实现
├── glances_controller.py     # 控制器：协调数据和视图
├── glances_model.py          # 模型：数据获取和处理
├── glances_view.py           # 视图：UI 组件和布局
└── components/               # UI 组件模块
    ├── __init__.py
    ├── system_overview.py    # 系统概览组件
    ├── process_monitor.py    # 进程监控组件
    ├── resource_charts.py    # 资源图表组件
    └── config_panel.py       # 配置面板组件
```

## 详细技术规格

### 1. 数据获取策略

#### Web API 模式（主要）
```python
# 端点优先级
PRIMARY_ENDPOINTS = [
    "/stats",           # 综合系统状态
    "/cpu",            # CPU 详细信息
    "/mem",            # 内存信息
    "/network",        # 网络统计
    "/diskio",         # 磁盘 I/O
    "/processes"       # 进程列表
]

# 连接配置
DEFAULT_CONFIG = {
    "base_url": "http://localhost:61208/api/3",
    "timeout": 5,
    "retry_attempts": 3,
    "fallback_enabled": True
}
```

#### Subprocess 回退模式
```python
# 回退命令选项
FALLBACK_COMMANDS = {
    "basic_stats": ["glances", "--stdout", "--json", "-t", "1"],
    "short_format": ["glances", "-c", "--stdout", "--json"]
}
```

### 2. UI 设计规格

#### 主界面布局优先级

**顶级显示（占用主要空间）：**
1. **系统概览面板**
   - CPU 使用率（总体 + 各核心）
   - 内存使用状态（总量/已用/可用/交换）
   - 负载平均值（1分钟/5分钟/15分钟）

2. **实时图表区域**
   - CPU 使用率时间线图
   - 内存使用趋势图
   - 网络吞吐量图表

3. **快速指标卡片**
   - 磁盘 I/O 读写速度
   - 网络上下行速度
   - 活跃进程数量

**次级标签页：**
- **进程监控**：资源消耗排行、可搜索过滤
- **磁盘空间**：各分区使用情况
- **网络详情**：各网络接口统计
- **传感器数据**：温度、风扇转速（如果可用）

#### UI 技术实现

```python
# PyQt5 组件选择
MAIN_COMPONENTS = {
    "overview": "QWidget with QGridLayout",
    "charts": "QChartView with QLineSeries", 
    "gauges": "QProgressBar + custom circular gauge",
    "process_table": "QTableWidget with sorting",
    "tabs": "QTabWidget for secondary data"
}

# 图表数据管理
CHART_CONFIG = {
    "data_points": 60,          # 1分钟历史数据
    "update_interval": 1000,    # 1秒更新间隔
    "data_structure": "collections.deque",
    "performance_target": "<100ms update time"
}
```

### 3. 线程和性能设计

#### 线程策略
```python
# 单工作线程设计（初期）
class GlancesDataWorker(QThread):
    """
    单一工作线程负责所有数据获取
    - 避免线程间竞争条件
    - 简化错误处理
    - 如性能成为瓶颈可后续拆分
    """
    
    data_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.stop_flag = False
        self.update_interval = 1000  # 可配置
```

#### 优雅关闭机制
```python
def cleanup(self):
    """插件卸载时的清理流程"""
    if self.data_worker:
        self.data_worker.stop_flag = True
        self.data_worker.quit()
        if not self.data_worker.wait(5000):  # 5秒超时
            self.data_worker.terminate()
            self.data_worker.wait(1000)
```

### 4. 配置管理

#### 用户可配置选项
```json
{
    "glances_api_url": {
        "type": "string",
        "default": "http://localhost:61208/api/3",
        "description": "Glances Web API 端点URL"
    },
    "api_port": {
        "type": "integer", 
        "default": 61208,
        "range": [1024, 65535],
        "description": "Glances Web API 端口"
    },
    "update_interval": {
        "type": "integer",
        "default": 1000,
        "range": [500, 10000],
        "description": "数据更新间隔（毫秒）"
    },
    "enable_subprocess_fallback": {
        "type": "boolean",
        "default": true,
        "description": "启用子进程回退模式"
    },
    "glances_executable_path": {
        "type": "string",
        "default": "glances",
        "description": "Glances 可执行文件路径"
    },
    "visible_metrics": {
        "type": "array",
        "default": ["cpu", "memory", "network", "disk"],
        "options": ["cpu", "memory", "network", "disk", "processes", "sensors"],
        "description": "显示的指标类型"
    },
    "chart_data_points": {
        "type": "integer",
        "default": 60,
        "range": [30, 300],
        "description": "图表数据点数量"
    },
    "adaptive_interval": {
        "type": "boolean", 
        "default": false,
        "description": "启用自适应更新间隔"
    }
}
```

### 5. 错误处理策略

#### 分层错误处理

**级别 1：工具检测**
```python
def check_glances_availability():
    """检查 Glances 工具可用性"""
    api_available = check_api_connection()
    subprocess_available = check_subprocess_glances()
    
    return {
        "web_api": api_available,
        "subprocess": subprocess_available,
        "recommended_mode": "web_api" if api_available else "subprocess"
    }
```

**级别 2：连接错误**
```python
ERROR_MESSAGES = {
    "api_connection_failed": "无法连接到 Glances Web API。请确保 Glances 以 web 模式运行。",
    "port_in_use": "端口 {port} 被占用。请检查 Glances 配置或选择其他端口。",
    "subprocess_failed": "无法通过命令行调用 Glances。请确保 Glances 已正确安装。",
    "no_data": "暂时无法获取系统数据。将在下次更新时重试。"
}
```

**级别 3：数据解析错误**
- JSON 格式验证
- 必要字段检查  
- 数据类型转换保护
- 部分数据可用时的优雅降级

### 6. 性能目标

#### 关键性能指标
```python
PERFORMANCE_TARGETS = {
    "ui_update_time": "< 100ms",           # UI更新响应时间
    "data_fetch_time": "< 500ms",          # 数据获取时间
    "memory_usage": "< 50MB",              # 插件内存占用
    "cpu_overhead": "< 5%",                # CPU开销
    "thread_cleanup": "< 5s"               # 线程清理时间
}
```

#### 优化策略
- 使用 `collections.deque` 管理图表数据
- 增量 UI 更新（仅更新变化的部分）
- 数据缓存和批量处理
- 异步网络请求避免 UI 阻塞

### 7. 跨平台兼容性

#### 平台特定考虑
```python
PLATFORM_CONFIG = {
    "windows": {
        "glances_install": "pip install glances",
        "executable_name": "glances.exe",
        "path_separator": ";",
        "default_paths": ["C:\\Python\\Scripts", "%APPDATA%\\Python\\Scripts"]
    },
    "linux": {
        "glances_install": "sudo apt install glances", 
        "executable_name": "glances",
        "path_separator": ":",
        "default_paths": ["/usr/bin", "/usr/local/bin", "~/.local/bin"]
    },
    "darwin": {
        "glances_install": "brew install glances",
        "executable_name": "glances", 
        "path_separator": ":",
        "default_paths": ["/usr/bin", "/usr/local/bin", "/opt/homebrew/bin"]
    }
}
```

## 实施计划

### Phase 1: 基础架构（第1-2周）
1. 创建插件骨架和 MVC 结构
2. 实现基础的 Web API 连接
3. 基本的 UI 布局和数据显示
4. 简单的错误处理机制

### Phase 2: 核心功能（第3-4周）  
1. 完整的数据获取和解析
2. 实时图表和可视化组件
3. Subprocess 回退机制
4. 线程管理和性能优化

### Phase 3: 用户体验（第5-6周）
1. 配置界面和选项管理
2. 错误处理和用户反馈
3. 跨平台测试和兼容性
4. 文档和使用指南

### Phase 4: 优化和完善（第7-8周）
1. 性能分析和优化
2. 自适应更新间隔
3. 高级可视化功能
4. 全面的测试覆盖

## 风险评估和缓解

### 主要风险
1. **Glances API 变更**
   - 缓解：版本检测和兼容性层
   - 备案：Subprocess 回退确保基本功能

2. **性能影响**
   - 缓解：性能监控和自适应间隔
   - 备案：用户可配置更新频率

3. **跨平台兼容性**
   - 缓解：多平台测试环境
   - 备案：平台特定的错误处理

## 总结

这个集成方案基于 GEMINI AI 的专业建议，采用 Web API 优先、Subprocess 回退的双重策略，确保在各种用户环境下都能提供可靠的系统监控功能。通过细致的错误处理、性能优化和用户体验设计，将为 CLI Tool 项目增加强大的系统监控能力。

---

**文档版本**: 1.0  
**创建日期**: 2025-08-14  
**协作方**: Claude Code × GEMINI AI  
**下一步**: 开始 Phase 1 基础架构实现