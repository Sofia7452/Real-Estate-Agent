# 多Agent系统使用指南

## 🚀 快速开始

### 1. 启动多Agent系统

```bash
# 使用新的多Agent配置启动
aiq serve --config_file configs/real_estate_multi_agent.yml --host 0.0.0.0 --port 8001
```

### 2. 或者修改启动脚本

编辑 `start.sh`，将配置改为多Agent版本：

```bash
# 修改这一行
aiq serve --config_file configs/real_estate_multi_agent.yml --host 0.0.0.0 --port 8001 &
```

## 🎯 使用方式

### 方式一：通过API调用

#### 单个Agent调用
```bash
# 调用房产调研Agent
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "分析上海浦东新区500万预算的购房选择",
    "agent": "property_researcher"
  }'

# 调用市场分析Agent  
curl -X POST http://localhost:8001/generate \
  -H "Content-Type: application/json" \
  -d '{
    "input": "分析2024年上海房地产市场趋势",
    "agent": "market_analyst"
  }'
```

#### 多Agent工作流调用
```bash
# 启动房产评估工作流
curl -X POST http://localhost:8001/workflow/property_evaluation \
  -H "Content-Type: application/json" \
  -d '{
    "property_address": "上海浦东新区某小区",
    "budget": 5000000,
    "requirements": "三室两厅，学区房"
  }'
```

### 方式二：通过Web界面

1. 访问前端界面: http://localhost:3000
2. 在聊天界面中选择Agent类型
3. 输入查询内容

### 方式三：命令行测试

```bash
# 进入Python环境
source .venv/bin/activate

# 测试单个Agent
python -c "
from aiq.runtime.loader import load_config
from aiq.runtime.runner import Runner

config = load_config('configs/real_estate_multi_agent.yml')
runner = Runner(config)

# 调用房产调研Agent
result = runner.run_agent('property_researcher', '分析北京朝阳区房价')
print(result)
"

# 测试工作流
python -c "
from aiq.runtime.loader import load_config  
from aiq.runtime.runner import Runner

config = load_config('configs/real_estate_multi_agent.yml')
runner = Runner(config)

# 启动客户接入工作流
workflow_input = {
    'customer_name': '张三',
    'phone': '13800138000',
    'budget': 8000000,
    'preferred_location': '上海徐汇区'
}
result = runner.run_workflow('customer_onboarding', workflow_input)
print(result)
"
```

## 🏗️ Agent功能说明

### 1. Property Researcher (房产调研Agent)
- **功能**: 房产信息收集、价格分析、区域调研
- **适用场景**: 
  - "上海浦东新区500万买房推荐"
  - "北京朝阳区三室户型分析"
  - "深圳学区房价格调研"

### 2. Market Analyst (市场分析Agent)
- **功能**: 市场趋势分析、投资建议、风险评估
- **适用场景**:
  - "2024年房地产市场预测"
  - "投资房产的风险分析"
  - "不同区域房价对比"

### 3. Customer Service (客户服务Agent)
- **功能**: 客户咨询、需求分析、预约安排
- **适用场景**:
  - "我想买一套三室的房子"
  - "预约看房时间"
  - "贷款政策咨询"

### 4. Coordinator (协调Agent)
- **功能**: 自动协调多Agent协作
- **调用方式**: 通过工作流自动调用

## ⚙️ 配置说明

### 自定义工具集成
在配置文件中添加自定义工具：

```yaml
tools:
  my_custom_tool:
    _type: custom_tool
    module: "real_estate_agents.tools.my_tool"
    description: "我的自定义工具"
```

### Agent参数调整
```yaml
agents:
  property_researcher:
    max_iterations: 10  # 最大迭代次数
    temperature: 0.7    # 创造性程度
    verbose: true       # 详细日志
```

## 🔧 故障排除

### 常见问题

1. **Agent未找到**
   ```bash
   # 检查Agent配置
   aiq info --config_file configs/real_estate_multi_agent.yml
   ```

2. **工具加载失败**
   - 确认工具模块路径正确
   - 检查Python导入路径

3. **API调用超时**
   - 增加超时时间
   - 检查网络连接

### 日志查看
```bash
# 查看详细日志
tail -f logs/aiq.log

# 调试模式启动
aiq serve --config_file configs/real_estate_multi_agent.yml --verbose
```

## 📊 监控和管理

### 查看运行状态
```bash
# 查看活跃Agent
curl http://localhost:8001/health

# 查看工作流状态  
curl http://localhost:8001/workflows/status
```

### 性能监控
```bash
# 监控资源使用
watch -n 1 "ps aux | grep aiq"

# 查看API性能
curl http://localhost:8001/metrics
```

## 🚀 高级用法

### 自定义工作流
创建自定义多Agent协作流程：

```python
# 在 real_estate_agents/workflows/custom_workflow.py 中
from aiq.builder.workflow import WorkflowBuilder

class CustomWorkflow(WorkflowBuilder):
    def build(self):
        # 定义多Agent协作逻辑
        self.add_step('property_researcher', '收集房产信息')
        self.add_step('market_analyst', '分析市场数据') 
        self.add_step('coordinator', '生成综合报告')
```

### 集成外部系统
```python
# 集成数据库、API等外部系统
from real_estate_agents.tools.external_integration import (
    CRMIntegration,
    PropertyAPIClient,
    PaymentGateway
)
```

现在你的多Agent系统已经准备好使用了！根据你的业务需求选择合适的调用方式。
