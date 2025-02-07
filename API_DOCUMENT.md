# 股票策略管理系统 API 文档

## 基础信息

- 基础路径: `/api/v1`
- 响应格式: JSON
- 时区: Asia/Shanghai (UTC+8)

## 通用响应格式

```json
{
    "code": 200,          // 状态码
    "message": "success", // 响应消息
    "data": null         // 响应数据，可能是对象、数组或null
}
```

## 错误码说明

| 错误码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 接口列表

### 1. AI策略分析

#### 请求信息
- 路径: `/analyze_strategy`
- 方法: `POST`
- 描述: 使用AI分析用户输入的策略文本，提取关键信息

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
        "position_ratio": 0.5,
        "price_min": 1500.0,
        "price_max": 1600.0,
        "take_profit_price": 1800.0,
        "stop_loss_price": 1400.0,
        "other_conditions": "日线MACD金叉时买入",
        "reason": "基本面良好，技术面触发买点"
    }
}
```

### 2. 获取策略列表

#### 请求信息
- 路径: `/strategies`
- 方法: `GET`
- 描述: 获取所有策略列表

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
            "position_ratio": 0.5,
            "price_min": 1500.0,
            "price_max": 1600.0,
            "take_profit_price": 1800.0,
            "stop_loss_price": 1400.0,
            "other_conditions": "日线MACD金叉时买入",
            "reason": "基本面良好，技术面触发买点",
            "created_at": "2024-01-20 10:00:00",
            "updated_at": "2024-01-20 10:00:00",
            "is_active": true
        }
    ]
}
```

### 3. 创建策略

#### 请求信息
- 路径: `/strategies`
- 方法: `POST`
- 描述: 创建新的策略

#### 请求参数
```json
{
    "stock_name": "贵州茅台",
    "stock_code": "600519",
    "action": "buy",
    "position_ratio": 0.5,
    "price_min": 1500.0,
    "price_max": 1600.0,
    "take_profit_price": 1800.0,
    "stop_loss_price": 1400.0,
    "other_conditions": "日线MACD金叉时买入",
    "reason": "基本面良好，技术面触发买点"
}
```

#### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 0.5,
        "price_min": 1500.0,
        "price_max": 1600.0,
        "take_profit_price": 1800.0,
        "stop_loss_price": 1400.0,
        "other_conditions": "日线MACD金叉时买入",
        "reason": "基本面良好，技术面触发买点",
        "created_at": "2024-01-20 10:00:00",
        "updated_at": "2024-01-20 10:00:00",
        "is_active": true
    }
}
```

### 4. 更新策略

#### 请求信息
- 路径: `/strategies/<id>`
- 方法: `PUT`
- 描述: 更新指定ID的策略

#### 请求参数
```json
{
    "stock_name": "贵州茅台",
    "stock_code": "600519",
    "action": "buy",
    "position_ratio": 0.5,
    "price_min": 1500.0,
    "price_max": 1600.0,
    "take_profit_price": 1800.0,
    "stop_loss_price": 1400.0,
    "other_conditions": "日线MACD金叉时买入",
    "reason": "基本面良好，技术面触发买点"
}
```

#### 响应示例
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 0.5,
        "price_min": 1500.0,
        "price_max": 1600.0,
        "take_profit_price": 1800.0,
        "stop_loss_price": 1400.0,
        "other_conditions": "日线MACD金叉时买入",
        "reason": "基本面良好，技术面触发买点",
        "created_at": "2024-01-20 10:00:00",
        "updated_at": "2024-01-20 10:30:00",
        "is_active": true
    }
}
```

### 5. 检查策略是否存在

#### 请求信息
- 路径: `/strategies/check`
- 方法: `POST`
- 描述: 检查指定的策略是否已存在

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
    "message": "success",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 0.5,
        "price_min": 1500.0,
        "price_max": 1600.0,
        "take_profit_price": 1800.0,
        "stop_loss_price": 1400.0,
        "other_conditions": "日线MACD金叉时买入",
        "reason": "基本面良好，技术面触发买点",
        "created_at": "2024-01-20 10:00:00",
        "updated_at": "2024-01-20 10:00:00",
        "is_active": true
    }
}
```

### 6. 根据关键字段更新策略

#### 请求信息
- 路径: `/strategies/update`
- 方法: `POST`
- 描述: 根据股票名称、代码和操作类型更新策略

#### 请求参数
```json
{
    "stock_name": "贵州茅台",
    "stock_code": "600519",
    "action": "buy",
    "position_ratio": 0.5,
    "price_min": 1500.0,
    "price_max": 1600.0,
    "take_profit_price": 1800.0,
    "stop_loss_price": 1400.0,
    "other_conditions": "日线MACD金叉时买入",
    "reason": "基本面良好，技术面触发买点"
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
        "position_ratio": 0.5,
        "price_min": 1500.0,
        "price_max": 1600.0,
        "take_profit_price": 1800.0,
        "stop_loss_price": 1400.0,
        "other_conditions": "日线MACD金叉时买入",
        "reason": "基本面良好，技术面触发买点",
        "created_at": "2024-01-20 10:00:00",
        "updated_at": "2024-01-20 10:30:00",
        "is_active": true
    }
}
```

### 7. 设置策略为失效

#### 请求信息
- 路径: `/strategies/<id>/deactivate`
- 方法: `POST`
- 描述: 将指定ID的策略设置为失效状态

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
        "position_ratio": 0.5,
        "price_min": 1500.0,
        "price_max": 1600.0,
        "take_profit_price": 1800.0,
        "stop_loss_price": 1400.0,
        "other_conditions": "日线MACD金叉时买入",
        "reason": "基本面良好，技术面触发买点",
        "created_at": "2024-01-20 10:00:00",
        "updated_at": "2024-01-20 11:00:00",
        "is_active": false
    }
}
``` 