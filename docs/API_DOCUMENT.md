# QMT Server API 文档

## 基础信息

- 基础URL: 
  - `http://localhost:5000/api/v1`
  - `http://127.0.0.1:5000/api/v1`
- 所有响应格式均为 JSON
- 时间格式: `YYYY-MM-DD HH:mm:ss`

## 通用响应格式

```json
{
    "code": 200,       // 状态码
    "message": "成功",  // 响应消息
    "data": {}         // 响应数据
}
```

## 错误码说明

- 200: 成功
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## 接口列表

### 1. 策略分析

#### 请求信息
- 路径: `/api/v1/analyze_strategy`
- 方法: POST
- Content-Type: application/json

#### 请求参数
```json
{
    "strategy_text": "策略文本内容"
}
```

#### 响应示例
```json
{
    "code": 200,
    "message": "策略分析成功",
    "data": {
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 0.1,
        "price_min": 1500,
        "price_max": 1600,
        "take_profit_price": 1700,
        "stop_loss_price": 1450,
        "other_conditions": "日线MACD金叉",
        "reason": "技术面向好，估值合理",
        "execution_status": "pending"
    }
}
```

### 2. 获取策略列表

#### 请求信息
- 路径: `/api/v1/strategies`
- 方法: GET

#### 查询参数
- `sort_by`: 排序字段，可选值：updated_at, created_at，默认 updated_at
- `order`: 排序方式，可选值：desc, asc，默认 desc

#### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "id": 1,
            "stock_name": "贵州茅台",
            "stock_code": "600519",
            "action": "buy",
            "position_ratio": 0.1,
            "price_min": 1500,
            "price_max": 1600,
            "take_profit_price": 1700,
            "stop_loss_price": 1450,
            "other_conditions": "日线MACD金叉",
            "reason": "技术面向好，估值合理",
            "execution_status": "pending",
            "is_active": true,
            "created_at": "2024-02-01 10:00:00",
            "updated_at": "2024-02-01 10:00:00"
        }
    ]
}
```

### 3. 创建策略

#### 请求信息
- 路径: `/api/v1/strategies`
- 方法: POST
- Content-Type: application/json

#### 请求参数
```json
{
    "stock_name": "贵州茅台",
    "stock_code": "600519",
    "action": "buy",
    "position_ratio": 0.1,
    "price_min": 1500,
    "price_max": 1600,
    "take_profit_price": 1700,
    "stop_loss_price": 1450,
    "other_conditions": "日线MACD金叉",
    "reason": "技术面向好，估值合理"
}
```

#### 响应示例
```json
{
    "code": 200,
    "message": "成功",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 0.1,
        "price_min": 1500,
        "price_max": 1600,
        "take_profit_price": 1700,
        "stop_loss_price": 1450,
        "other_conditions": "日线MACD金叉",
        "reason": "技术面向好，估值合理",
        "execution_status": "pending",
        "is_active": true,
        "created_at": "2024-02-01 10:00:00",
        "updated_at": "2024-02-01 10:00:00"
    }
}
```

### 4. 更新策略

#### 请求信息
- 路径: `/api/v1/strategies/{id}`
- 方法: PUT
- Content-Type: application/json

#### 请求参数
```json
{
    "position_ratio": 0.2,
    "price_min": 1550,
    "price_max": 1650,
    "take_profit_price": 1750,
    "stop_loss_price": 1500,
    "other_conditions": "日线MACD金叉，成交量放大",
    "reason": "技术面继续向好，估值依然合理"
}
```

#### 响应示例
```json
{
    "code": 200,
    "message": "成功",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 0.2,
        "price_min": 1550,
        "price_max": 1650,
        "take_profit_price": 1750,
        "stop_loss_price": 1500,
        "other_conditions": "日线MACD金叉，成交量放大",
        "reason": "技术面继续向好，估值依然合理",
        "execution_status": "partial",
        "is_active": true,
        "created_at": "2024-02-01 10:00:00",
        "updated_at": "2024-02-01 11:00:00"
    }
}
```

### 5. 检查策略是否存在

#### 请求信息
- 路径: `/api/v1/strategies/check`
- 方法: POST
- Content-Type: application/json

#### 请求参数
```json
{
    "stock_name": "贵州茅台",
    "stock_code": "600519",
    "action": "buy"
}
```

#### 响应示例
```json
{
    "code": 200,
    "message": "成功",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 0.2,
        "price_min": 1550,
        "price_max": 1650,
        "take_profit_price": 1750,
        "stop_loss_price": 1500,
        "other_conditions": "日线MACD金叉，成交量放大",
        "reason": "技术面继续向好，估值依然合理",
        "execution_status": "partial",
        "is_active": true,
        "created_at": "2024-02-01 10:00:00",
        "updated_at": "2024-02-01 11:00:00"
    }
}
```

### 6. 搜索策略列表

#### 请求信息
- 路径: `/api/v1/strategies/search`
- 方法: GET

#### 查询参数
- `start_time`: 开始时间，格式：YYYY-MM-DD HH:mm:ss
- `end_time`: 结束时间，格式：YYYY-MM-DD HH:mm:ss
- `stock_code`: 股票代码
- `stock_name`: 股票名称
- `action`: 交易动作（buy/sell）
- `sort_by`: 排序字段，可选值: updated_at, created_at
- `order`: 排序方式，可选值: desc, asc
- `is_active`: 是否只查询有效策略（true/false）

#### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "id": 1,
            "stock_name": "贵州茅台",
            "stock_code": "600519",
            "action": "buy",
            "position_ratio": 0.2,
            "price_min": 1550,
            "price_max": 1650,
            "take_profit_price": 1750,
            "stop_loss_price": 1500,
            "other_conditions": "日线MACD金叉，成交量放大",
            "reason": "技术面继续向好，估值依然合理",
            "execution_status": "partial",
            "is_active": true,
            "created_at": "2024-02-01 10:00:00",
            "updated_at": "2024-02-01 11:00:00"
        }
    ]
}
```

### 7. 创建执行记录

#### 请求信息
- 路径: `/api/v1/executions`
- 方法: POST
- Content-Type: application/json

#### 请求参数
```json
{
    "strategy_id": 1,
    "execution_price": 1580.5,
    "volume": 100,
    "strategy_status": "partial",  // 可选值：partial（部分执行）, completed（全部完成）
    "remarks": "按计划执行"
}
```

#### 响应示例
```json
{
    "code": 200,
    "message": "成功",
    "data": {
        "id": 1,
        "strategy_id": 1,
        "stock_code": "600519",
        "stock_name": "贵州茅台",
        "action": "buy",
        "execution_price": 1580.5,
        "volume": 100,
        "execution_result": "success",
        "remarks": "按计划执行",
        "execution_time": "2024-02-01 14:30:00",
        "created_at": "2024-02-01 14:30:00",
        "updated_at": "2024-02-01 14:30:00"
    }
}
```

### 8. 获取执行记录列表

#### 请求信息
- 路径: `/api/v1/executions`
- 方法: GET

#### 查询参数
- `strategy_id`: 策略ID
- `stock_code`: 股票代码
- `start_time`: 开始时间
- `end_time`: 结束时间
- `action`: 执行操作（buy/sell）
- `result`: 执行结果（success/failed/partial）
- `sort_by`: 排序字段（execution_time/created_at）
- `order`: 排序方式（desc/asc）
- `limit`: 限制返回数量

#### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "id": 1,
            "strategy_id": 1,
            "stock_code": "600519",
            "stock_name": "贵州茅台",
            "action": "buy",
            "execution_price": 1580.5,
            "volume": 100,
            "execution_result": "success",
            "remarks": "按计划执行",
            "execution_time": "2024-02-01 14:30:00",
            "created_at": "2024-02-01 14:30:00",
            "updated_at": "2024-02-01 14:30:00"
        }
    ]
}
```

### 9. 设置策略状态

#### 请求信息
- 路径: `/api/v1/strategies/{id}/deactivate` 或 `/api/v1/strategies/{id}/activate`
- 方法: POST

#### 响应示例
```json
{
    "code": 200,
    "message": "成功",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 0.2,
        "price_min": 1550,
        "price_max": 1650,
        "take_profit_price": 1750,
        "stop_loss_price": 1500,
        "other_conditions": "日线MACD金叉，成交量放大",
        "reason": "技术面继续向好，估值依然合理",
        "execution_status": "partial",
        "is_active": false,  // 或 true
        "created_at": "2024-02-01 10:00:00",
        "updated_at": "2024-02-01 11:00:00"
    }
}
``` 