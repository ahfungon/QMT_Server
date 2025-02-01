# 股票策略接口程序

这是一个基于 Flask 的股票策略管理系统，提供 RESTful API 接口来管理股票交易策略。

## 功能特点

- 创建和管理股票交易策略
- 支持买入/卖出操作
- 灵活的价格区间设置
- 支持止盈止损设置
- JSON 格式的数据交互

## 安装步骤

1. 克隆项目到本地
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
3. 配置数据库：
   创建 .env 文件并设置以下环境变量：
   ```
   MYSQL_HOST=localhost
   MYSQL_PORT=3306
   MYSQL_USER=your_username
   MYSQL_PASSWORD=your_password
   MYSQL_DATABASE=stock_strategy
   ```

4. 运行程序：
   ```bash
   python app.py
   ```

## API 接口说明

### 1. 创建策略
- 端点：`POST /api/v1/strategies`
- 请求体示例：
```json
{
    "stock_name": "示例股票",
    "stock_code": "000001",
    "action": "buy",
    "position_ratio": 0.3,
    "price_min": 10.5,
    "price_max": 11.0,
    "take_profit_price": 12.0,
    "stop_loss_price": 10.0,
    "other_conditions": "MA5上穿MA10",
    "reason": "技术面突破"
}
```

### 2. 更新策略
- 端点：`PUT /api/v1/strategies/<strategy_id>`
- 请求体格式同创建策略

### 3. 获取策略
- 获取所有策略：`GET /api/v1/strategies`
- 获取特定股票策略：`GET /api/v1/strategies?stock_code=000001`
- 查询参数：
  - stock_code：股票代码（可选）
  - is_active：是否有效（可选，默认为true）

### 4. 删除策略
- 端点：`DELETE /api/v1/strategies/<strategy_id>`

## 数据库结构

主要数据表：stock_strategies
- id：策略ID
- stock_name：股票名称
- stock_code：股票代码
- action：操作类型（买入/卖出）
- position_ratio：操作比例
- price_min：最小执行价
- price_max：最大执行价
- take_profit_price：止盈价
- stop_loss_price：止损价
- other_conditions：其他条件
- reason：操作理由
- created_at：创建时间
- updated_at：更新时间
- is_active：是否有效 