# QMT Server API 文档

## 基本信息

- 基础URL: `http://localhost:5000`
- 所有请求和响应均使用 JSON 格式
- 所有响应都包含以下基本结构：
  ```json
  {
    "code": 200,      // 状态码
    "message": "...",  // 响应消息
    "data": {}        // 响应数据
  }
  ```

## 接口列表

### 1. 策略分析接口

- **URL**: `/api/v1/analyze_strategy`
- **方法**: POST
- **描述**: 分析用户输入的策略文本，提取关键信息
- **请求参数**:
  ```json
  {
    "strategy_text": "以30元买入平安银行，仓位30%"
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "策略分析成功",
    "data": {
      "stock_name": "平安银行",
      "stock_code": "000001",
      "action": "buy",
      "position_ratio": 0.3,
      "price_min": 30.0,
      "price_max": 30.0,
      "take_profit_price": null,
      "stop_loss_price": null,
      "other_conditions": null,
      "reason": null
    }
  }
  ```

### 2. 获取策略列表

- **URL**: `/api/v1/strategies`
- **方法**: GET
- **描述**: 获取所有策略列表
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": [
      {
        "id": 1,
        "stock_name": "平安银行",
        "stock_code": "000001",
        "action": "buy",
        "position_ratio": 0.3,
        "price_min": 30.0,
        "price_max": 30.0,
        "take_profit_price": null,
        "stop_loss_price": null,
        "other_conditions": null,
        "reason": null,
        "created_at": "2025-02-07 15:10:51",
        "updated_at": "2025-02-07 15:10:51",
        "is_active": true
      }
    ]
  }
  ```

### 3. 创建策略

- **URL**: `/api/v1/strategies`
- **方法**: POST
- **描述**: 创建新的交易策略
- **请求参数**:
  ```json
  {
    "stock_name": "平安银行",
    "stock_code": "000001",
    "action": "buy",
    "position_ratio": 0.3,
    "price_min": 30.0,
    "price_max": 30.0,
    "take_profit_price": null,
    "stop_loss_price": null,
    "other_conditions": null,
    "reason": null
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "id": 1,
      "stock_name": "平安银行",
      "stock_code": "000001",
      "action": "buy",
      "position_ratio": 0.3,
      "price_min": 30.0,
      "price_max": 30.0,
      "take_profit_price": null,
      "stop_loss_price": null,
      "other_conditions": null,
      "reason": null,
      "created_at": "2025-02-07 15:10:51",
      "updated_at": "2025-02-07 15:10:51",
      "is_active": true
    }
  }
  ```

### 4. 更新策略

- **URL**: `/api/v1/strategies/<id>`
- **方法**: PUT
- **描述**: 更新指定ID的策略
- **请求参数**: 同创建策略
- **响应示例**: 同创建策略

### 5. 检查策略是否存在

- **URL**: `/api/v1/strategies/check`
- **方法**: POST
- **描述**: 检查指定的策略是否存在
- **请求参数**:
  ```json
  {
    "stock_name": "平安银行",
    "stock_code": "000001",
    "action": "buy"
  }
  ```
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "success",
    "data": {
      "id": 1,
      "stock_name": "平安银行",
      "stock_code": "000001",
      "action": "buy",
      "position_ratio": 0.3,
      "price_min": 30.0,
      "price_max": 30.0,
      "take_profit_price": null,
      "stop_loss_price": null,
      "other_conditions": null,
      "reason": null,
      "created_at": "2025-02-07 15:10:51",
      "updated_at": "2025-02-07 15:10:51",
      "is_active": true
    }
  }
  ```

### 6. 根据关键字段更新策略

- **URL**: `/api/v1/strategies/update`
- **方法**: POST
- **描述**: 根据股票名称、代码和操作类型更新策略
- **请求参数**:
  ```json
  {
    "stock_name": "平安银行",
    "stock_code": "000001",
    "action": "buy",
    "position_ratio": 0.5,
    "price_min": 31.0,
    "price_max": 32.0
  }
  ```
- **响应示例**: 同创建策略

### 7. 设置策略为失效

- **URL**: `/api/v1/strategies/<id>/deactivate`
- **方法**: POST
- **描述**: 将指定ID的策略设置为失效状态
- **响应示例**:
  ```json
  {
    "code": 200,
    "message": "策略已设置为失效",
    "data": {
      "id": 1,
      "stock_name": "平安银行",
      "stock_code": "000001",
      "action": "buy",
      "position_ratio": 0.3,
      "price_min": 30.0,
      "price_max": 30.0,
      "take_profit_price": null,
      "stop_loss_price": null,
      "other_conditions": null,
      "reason": null,
      "created_at": "2025-02-07 15:10:51",
      "updated_at": "2025-02-07 15:10:51",
      "is_active": false
    }
  }
  ```

## 错误码说明

- 200: 请求成功
- 400: 请求参数错误
- 404: 资源不存在
- 500: 服务器内部错误

## 数据字段说明

- `stock_name`: 股票名称
- `stock_code`: 股票代码（6位数字）
- `action`: 交易动作（buy/sell）
- `position_ratio`: 仓位比例（0-1之间的小数）
- `price_min`: 最小执行价
- `price_max`: 最大执行价
- `take_profit_price`: 止盈价
- `stop_loss_price`: 止损价
- `other_conditions`: 其他交易条件
- `reason`: 交易理由
- `created_at`: 创建时间
- `updated_at`: 更新时间
- `is_active`: 策略是否有效 