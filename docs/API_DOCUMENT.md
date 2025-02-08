# QMT Server API 文档

## 基础信息

- 基础URL: `http://localhost:5000/api/v1`
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
- 路径: `/analyze_strategy`
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
        "reason": "技术面向好，估值合理"
    }
}
```

### 2. 获取策略列表

#### 请求信息
- 路径: `/strategies`
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
            "is_active": true,
            "created_at": "2024-02-01 10:00:00",
            "updated_at": "2024-02-01 10:00:00"
        }
    ]
}
```

### 3. 创建策略

#### 请求信息
- 路径: `/strategies`
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
        "is_active": true,
        "created_at": "2024-02-01 10:00:00",
        "updated_at": "2024-02-01 10:00:00"
    }
}
```

### 4. 更新策略

#### 请求信息
- 路径: `/strategies/{id}`
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
        "is_active": true,
        "created_at": "2024-02-01 10:00:00",
        "updated_at": "2024-02-01 11:00:00"
    }
}
```

### 5. 检查策略是否存在

#### 请求信息
- 路径: `/strategies/check`
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
        "is_active": true,
        "created_at": "2024-02-01 10:00:00",
        "updated_at": "2024-02-01 11:00:00"
    }
}
```

### 6. 根据关键字段更新策略

#### 请求信息
- 路径: `/strategies/update`
- 方法: POST
- Content-Type: application/json

#### 请求参数
```json
{
    "stock_name": "贵州茅台",
    "stock_code": "600519",
    "action": "buy",
    "position_ratio": 0.3,
    "price_min": 1600,
    "price_max": 1700,
    "take_profit_price": 1800,
    "stop_loss_price": 1550,
    "other_conditions": "日线MACD金叉，成交量放大，KDJ金叉",
    "reason": "技术面持续向好，估值仍然合理"
}
```

#### 响应示例
```json
{
    "code": 200,
    "message": "策略更新成功",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 0.3,
        "price_min": 1600,
        "price_max": 1700,
        "take_profit_price": 1800,
        "stop_loss_price": 1550,
        "other_conditions": "日线MACD金叉，成交量放大，KDJ金叉",
        "reason": "技术面持续向好，估值仍然合理",
        "is_active": true,
        "created_at": "2024-02-01 10:00:00",
        "updated_at": "2024-02-01 12:00:00"
    }
}
```

### 7. 设置策略为失效

#### 请求信息
- 路径: `/strategies/{id}/deactivate`
- 方法: POST

#### 响应示例
```json
{
    "code": 200,
    "message": "策略已设置为失效",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 0.3,
        "price_min": 1600,
        "price_max": 1700,
        "take_profit_price": 1800,
        "stop_loss_price": 1550,
        "other_conditions": "日线MACD金叉，成交量放大，KDJ金叉",
        "reason": "技术面持续向好，估值仍然合理",
        "is_active": false,
        "created_at": "2024-02-01 10:00:00",
        "updated_at": "2024-02-01 13:00:00"
    }
}
```

### 8. 高级查询策略列表

#### 请求信息
- 路径: `/strategies/search`
- 方法: GET

#### 查询参数
- `start_time`: 开始时间，格式：YYYY-MM-DD HH:mm:ss
- `end_time`: 结束时间，格式：YYYY-MM-DD HH:mm:ss
- `stock_code`: 股票代码（支持模糊查询）
- `stock_name`: 股票名称（支持模糊查询）
- `sort_by`: 排序字段，可选值：updated_at, created_at，默认 updated_at
- `order`: 排序方式，可选值：desc, asc，默认 desc
- `is_active`: 是否只查询有效策略，可选值：true, false，默认 true

#### 请求示例
```
GET /strategies/search?stock_code=600519&start_time=2024-02-01 00:00:00&end_time=2024-02-07 23:59:59&sort_by=created_at&order=desc
```

#### 响应示例
```json
{
    "code": 200,
    "message": "成功",
    "data": [
        {
            "id": 1,
            "stock_name": "贵州茅台",
            "stock_code": "600519",
            "action": "buy",
            "position_ratio": 0.3,
            "price_min": 1600,
            "price_max": 1700,
            "take_profit_price": 1800,
            "stop_loss_price": 1550,
            "other_conditions": "日线MACD金叉，成交量放大，KDJ金叉",
            "reason": "技术面持续向好，估值仍然合理",
            "is_active": true,
            "created_at": "2024-02-01 10:00:00",
            "updated_at": "2024-02-01 13:00:00"
        }
    ]
}
``` 