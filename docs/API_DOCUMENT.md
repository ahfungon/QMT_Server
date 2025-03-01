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

#### 1.1 分析策略文本

**接口**：`POST /api/v1/strategy/analyze`

**描述**：分析用户输入的策略文本，提取关键信息

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| text | string | 是 | 用户输入的策略文本 |
| ai_provider | string | 否 | AI 提供商，可选值：zhipu, deepseek，默认为 zhipu |

**响应示例**：

```json
{
  "code": 200,
  "message": "分析成功",
  "data": {
    "stock_name": "贵州茅台",
    "stock_code": "600519",
    "action": "buy",
    "position_ratio": 20,
    "price_min": 1500.0,
    "price_max": 1550.0,
    "take_profit_price": 1700.0,
    "stop_loss_price": 1450.0,
    "other_conditions": "日线MACD金叉时买入",
    "reason": "基本面良好，技术面呈现上升趋势"
  }
}
```

**注意**：
- `action` 字段可能的值包括：
  - `buy`: 买入/建仓
  - `sell`: 卖出/清仓
  - `add`: 加仓
  - `trim`: 减仓
  - `hold`: 持有/观望
- `position_ratio` 为整数，表示百分比（0-100）

### 2. 策略管理

#### 2.1 创建策略

**接口**：`POST /api/v1/strategy`

**描述**：创建新的交易策略

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| stock_name | string | 是 | 股票名称 |
| stock_code | string | 是 | 股票代码 |
| action | string | 是 | 交易动作，可选值：buy, sell, add, trim, hold |
| position_ratio | number | 是 | 仓位比例，整数，表示百分比（0-100） |
| price_min | number | 否 | 最低买入价格 |
| price_max | number | 否 | 最高买入价格 |
| take_profit_price | number | 否 | 止盈价格 |
| stop_loss_price | number | 否 | 止损价格 |
| other_conditions | string | 否 | 其他交易条件 |
| reason | string | 否 | 交易理由 |

**响应示例**：

```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 1,
    "stock_name": "贵州茅台",
    "stock_code": "600519",
    "action": "buy",
    "position_ratio": 20,
    "price_min": 1500.0,
    "price_max": 1550.0,
    "take_profit_price": 1700.0,
    "stop_loss_price": 1450.0,
    "other_conditions": "日线MACD金叉时买入",
    "reason": "基本面良好，技术面呈现上升趋势",
    "execution_status": "pending",
    "created_at": "2023-06-01T12:00:00Z",
    "updated_at": "2023-06-01T12:00:00Z"
  }
}
```

#### 2.2 获取策略列表

**接口**：`GET /api/v1/strategies`

**描述**：获取所有策略列表

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| page | number | 否 | 页码，默认为 1 |
| size | number | 否 | 每页数量，默认为 10 |
| stock_code | string | 否 | 按股票代码筛选 |
| action | string | 否 | 按交易动作筛选 |
| execution_status | string | 否 | 按执行状态筛选 |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 100,
    "page": 1,
    "size": 10,
    "items": [
      {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 20,
        "price_min": 1500.0,
        "price_max": 1550.0,
        "take_profit_price": 1700.0,
        "stop_loss_price": 1450.0,
        "other_conditions": "日线MACD金叉时买入",
        "reason": "基本面良好，技术面呈现上升趋势",
        "execution_status": "pending",
        "created_at": "2023-06-01T12:00:00Z",
        "updated_at": "2023-06-01T12:00:00Z"
      },
      // ... 更多策略
    ]
  }
}
```

### 3. 执行管理

#### 3.1 创建执行记录

**接口**：`POST /api/v1/execution`

**描述**：创建策略执行记录

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| strategy_id | number | 是 | 策略ID |
| price | number | 是 | 执行价格 |
| volume | number | 否 | 执行数量，如不提供则根据策略自动计算 |
| execution_time | string | 否 | 执行时间，格式为ISO8601，默认为当前时间 |
| remarks | string | 否 | 备注信息 |

**响应示例**：

```json
{
  "code": 200,
  "message": "创建成功",
  "data": {
    "id": 1,
    "strategy_id": 1,
    "stock_code": "600519",
    "stock_name": "贵州茅台",
    "action": "buy",
    "price": 1520.5,
    "volume": 100,
    "position_ratio": 20,
    "execution_time": "2023-06-01T14:30:00Z",
    "remarks": "按计划执行",
    "created_at": "2023-06-01T14:30:00Z",
    "updated_at": "2023-06-01T14:30:00Z"
  }
}
```

**注意**：
- 当 `action` 为 `hold` 时，不会产生实际交易，`volume` 将被设置为 0
- 当不提供 `volume` 参数时，系统会根据不同的操作类型自动计算交易量：
  - `buy`/`add`: 根据总资产和仓位比例计算
  - `sell`: 根据当前持股量和卖出比例计算
  - `trim`: 根据当前持股量、原始仓位比例和目标减仓比例计算
  - `hold`: 交易量为 0
- 执行操作会自动更新账户资金：
  - `buy`/`add`: 从可用资金中扣除交易金额（交易量×价格）
  - `sell`/`trim`: 向可用资金中增加交易金额（交易量×价格）
  - `hold`: 不影响账户资金

### 4. 获取执行记录列表

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

### 5. 设置策略状态

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

## 持仓相关接口

### 获取所有持仓

获取系统中所有的股票持仓信息。

- **URL**: `/api/positions`
- **方法**: `GET`
- **参数**: 无
- **响应**:
  ```json
  {
    "code": 0,
    "message": "success",
    "data": {
      "positions": [
        {
          "id": 1,
          "stock_code": "600519",
          "stock_name": "贵州茅台",
          "total_volume": 100,
          "original_cost": 1500.00,
          "dynamic_cost": 1450.00,
          "total_amount": 150000.00,
          "latest_price": 1600.00,
          "market_value": 160000.00,
          "floating_profit": 10000.00,
          "floating_profit_ratio": 6.67,
          "created_at": "2024-02-15 10:00:00",
          "updated_at": "2024-02-15 15:30:00"
        }
      ]
    }
  }
  ```
- **响应说明**:
  - `floating_profit_ratio`: 浮动盈亏比例
    - 正常情况：实际的盈亏比例值
    - 特殊情况：当 dynamic_cost <= 0 时，值为 999999
    - 前端显示：当值为 999999 时显示为 ♾️ 符号

### 获取单个股票持仓

获取指定股票代码的持仓信息。

- **URL**: `/api/v1/positions/{stock_code}`
- **方法**: `GET`
- **URL参数**:
  - `stock_code`: 股票代码

**响应示例**:
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "stock_code": "600519",
        "stock_name": "贵州茅台",
        "total_volume": 100,
        "average_cost": 1550.5,
        "total_amount": 155050.0,
        "latest_price": 1600.0,
        "market_value": 160000.0,
        "floating_profit": 4950.0,
        "floating_profit_ratio": 0.0319,
        "created_at": "2025-02-14 19:42:44",
        "updated_at": "2025-02-15 17:09:32"
    }
}
```

### 更新股票市值

更新指定股票的最新价格和市值信息。

- **URL**: `/api/v1/positions/{stock_code}/market_value`
- **方法**: `PUT`
- **URL参数**:
  - `stock_code`: 股票代码
- **请求体**:
```json
{
    "latest_price": 1600.0
}
```

**响应示例**:
```json
{
    "code": 200,
    "message": "更新市值成功",
    "data": {
        "id": 1,
        "stock_code": "600519",
        "stock_name": "贵州茅台",
        "total_volume": 100,
        "original_cost": 1580,
        "dynamic_cost": 1580,
        "total_amount": 158000,
        "latest_price": 1600,
        "market_value": 160000,
        "floating_profit": 2000,
        "floating_profit_ratio": 0.0127,
        "created_at": "2024-02-01 10:35:00",
        "updated_at": "2024-02-01 10:40:00"
    }
}
```

**错误响应**:
```json
{
    "code": 404,
    "message": "股票 600519 没有持仓记录",
    "data": null
}
```

### 更新持仓（卖出）
- **URL**: `/api/positions/{id}/sell`
- **方法**: `POST`
- **参数**:
  ```json
  {
    "volume": 50,
    "price": 1600.00
  }
  ```
- **响应**:
  ```json
  {
    "code": 0,
    "message": "success",
    "data": {
      "position": {
        "id": 1,
        "stock_code": "600519",
        "stock_name": "贵州茅台",
        "total_volume": 50,
        "original_cost": 1500.00,
        "dynamic_cost": 1450.00,
        "total_amount": 75000.00,
        "latest_price": 1600.00,
        "market_value": 80000.00,
        "floating_profit": 5000.00,
        "floating_profit_ratio": 6.67,
        "created_at": "2024-02-15 10:00:00",
        "updated_at": "2024-02-15 15:30:00"
      }
    }
  }
  ```
- **错误响应**:
  ```json
  {
    "code": 400,
    "message": "卖出数量 200 超过持仓数量 100",
    "data": null
  }
  ```

### 4. 持仓管理

#### 4.1 获取持仓列表

**接口**：`GET /api/v1/position`

**描述**：获取当前所有持仓信息

**请求参数**：

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| page | number | 否 | 页码，默认为 1 |
| size | number | 否 | 每页数量，默认为 10 |

**响应示例**：

```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 5,
    "page": 1,
    "size": 10,
    "items": [
      {
        "id": 1,
        "stock_code": "600519",
        "stock_name": "贵州茅台",
        "total_volume": 100,
        "average_cost": 1520.5,
        "current_price": 1550.0,
        "profit_amount": 2950.0,
        "profit_percentage": 1.94,
        "original_position_ratio": 20,
        "created_at": "2023-06-01T14:30:00Z",
        "updated_at": "2023-06-01T16:00:00Z"
      },
      // ... 更多持仓
    ]
  }
}
```

**注意**：
- `original_position_ratio` 字段表示初始买入时的仓位比例，用于减仓操作的计算
- 持仓记录会根据不同的操作类型进行更新：
  - `buy`: 创建新的持仓记录
  - `add`: 增加持仓数量并更新平均成本
  - `sell`: 减少持仓数量，如果卖出全部则删除持仓记录
  - `trim`: 减少持仓数量，但保持平均成本不变
  - `hold`: 不影响持仓记录

## 1. 账户资金接口

### 1.1 获取账户资金信息
- **接口**：`GET /api/v1/account/funds`
- **描述**：获取账户的资金信息，包括总资产、可用资金、冻结资金、总盈亏和收益率
- **参数**：无
- **返回示例**：
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "initial_assets": 300000.00,
        "total_assets": 300000.00,
        "available_funds": 241379.60,
        "frozen_funds": 0.00,
        "total_profit": 0.00,
        "total_profit_ratio": 0.00,
        "created_at": "2024-02-15 10:00:00",
        "updated_at": "2024-02-15 10:30:00"
    }
}
```

### 1.2 冻结资金
- **接口**：`POST /api/v1/account/funds/freeze`
- **描述**：冻结指定金额的资金
- **参数**：
```json
{
    "amount": 50000.00  // 要冻结的金额
}
```
- **返回示例**：
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "initial_assets": 300000.00,
        "total_assets": 300000.00,
        "available_funds": 191379.60,
        "frozen_funds": 50000.00,
        "total_profit": 0.00,
        "total_profit_ratio": 0.00,
        "created_at": "2024-02-15 10:00:00",
        "updated_at": "2024-02-15 10:35:00"
    }
}
```

### 1.3 解冻资金
- **接口**：`POST /api/v1/account/funds/unfreeze`
- **描述**：解冻指定金额的资金
- **参数**：
```json
{
    "amount": 50000.00  // 要解冻的金额
}
```
- **返回示例**：
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "initial_assets": 300000.00,
        "total_assets": 300000.00,
        "available_funds": 241379.60,
        "frozen_funds": 0.00,
        "total_profit": 0.00,
        "total_profit_ratio": 0.00,
        "created_at": "2024-02-15 10:00:00",
        "updated_at": "2024-02-15 10:40:00"
    }
}
```

### 1.4 更新账户资金
- **接口**：`PUT /api/v1/account/funds`
- **描述**：更新账户的可用资金和冻结资金
- **参数**：
```json
{
    "available_funds": 241379.60,  // 可用资金
    "frozen_funds": 0.00          // 冻结资金
}
```
- **返回示例**：
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "initial_assets": 300000.00,
        "total_assets": 300000.00,
        "available_funds": 241379.60,
        "frozen_funds": 0.00,
        "total_profit": 0.00,
        "total_profit_ratio": 0.00,
        "created_at": "2024-02-15 10:00:00",
        "updated_at": "2024-02-15 10:45:00"
    }
}
```

### 1.5 错误码说明
| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 参数错误 |
| 500 | 服务器内部错误 |

### 1.6 注意事项
1. 所有金额相关的字段都使用浮点数表示
2. 冻结资金时会自动从可用资金中扣除
3. 解冻资金时会自动加到可用资金中
4. 总资产会自动计算：可用资金 + 冻结资金 + 持仓市值
5. 总盈亏 = 总资产 - 初始资金
6. 总收益率 = (总资产 - 初始资金) / 初始资金 * 100%
7. 时间字段使用北京时间，格式为 "YYYY-MM-DD HH:mm:ss" 

## 操作类型说明

系统支持以下五种操作类型：

1. **买入(buy)**：初始建仓操作，会创建新的持仓记录。
   - 交易量计算：总资产 × 仓位比例 ÷ 价格
   - 会记录原始仓位比例

2. **卖出(sell)**：减少或清空持仓的操作。
   - 交易量计算：当前持股量 × 卖出比例
   - 如果卖出比例为100%，则清空持仓

3. **加仓(add)**：在现有持仓基础上增加的操作。
   - 交易量计算：总资产 × 仓位比例 ÷ 价格
   - 会更新持仓的平均成本

4. **减仓(trim)**：部分减少持仓的特殊操作。
   - 交易量计算：当前持股量 × (减仓比例 ÷ 原始买入仓位比例)
   - 不会改变持仓的平均成本

5. **持有(hold)**：不进行实际交易，仅记录策略的操作。
   - 不会产生实际交易
   - 仓位比例设置为0

## 仓位比例说明

系统中的仓位比例均使用整数表示百分比（0-100），例如：
- 10 表示 10% 的仓位
- 50 表示 50% 的仓位
- 100 表示 100% 的仓位 