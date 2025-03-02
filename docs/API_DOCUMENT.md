# QMT Server API 文档

## 目录
1. [健康检查接口](#健康检查接口)
2. [账户资金接口](#账户资金接口)
3. [策略管理接口](#策略管理接口)
4. [策略执行记录接口](#策略执行记录接口)
5. [持仓管理接口](#持仓管理接口)

## 通用说明

### 基础URL
- 开发环境：`http://localhost:5000`
- 生产环境：根据实际部署情况配置

### 响应格式
所有API响应均采用JSON格式，基本结构如下：
```json
{
    "code": 200,          // 状态码
    "message": "success", // 响应消息
    "data": null         // 响应数据
}
```

### 状态码说明
- 200: 请求成功
- 400: 请求参数错误
- 401: 未授权
- 403: 禁止访问
- 404: 资源不存在
- 500: 服务器内部错误

## 健康检查接口

### 1. 健康状态检查
```http
GET /api/v1/health
```

**响应示例：**
```json
{
    "status": "ok",
    "version": "1.0.0",
    "uptime": "24h 13m 45s",
    "timestamp": "2024-03-21T08:00:00Z",
    "system_info": {
        "python_version": "3.10.0",
        "platform": "Windows-10-10.0.19041-SP0",
        "process_id": 12345
    }
}
```

### 2. Ping检查
```http
GET /api/v1/ping
```

**响应示例：**
```json
{
    "message": "pong",
    "timestamp": "2024-03-21T08:00:00Z"
}
```

## 账户资金接口

### 1. 获取账户资金信息
```http
GET /api/v1/account/funds
```

**响应示例：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "initial_assets": 300000.00,    // 初始资金
        "total_assets": 350000.00,      // 资产总值
        "available_funds": 100000.00,   // 可用资金
        "frozen_funds": 50000.00,       // 冻结资金
        "total_profit": 50000.00,       // 总盈亏
        "total_profit_ratio": 16.67,    // 总收益率（%）
        "updated_at": "2024-03-21 16:00:00"
    }
}
```

**字段说明：**
1. **资产总值计算**
   - 总资产 = 可用资金 + 冻结资金 + 所有持仓市值
   - 持仓市值 = 持仓数量 × 最新价格
   - 每次查询时会自动更新所有持仓的最新价格和市值

2. **盈亏计算**
   - 总盈亏 = 当前总资产 - 初始资金
   - 总收益率 = (总盈亏 ÷ 初始资金) × 100%
   - 收益率保留两位小数，以百分比形式显示

3. **资金冻结规则**
   - 买入委托时，冻结所需资金
   - 委托成交后，冻结资金转为持仓成本
   - 委托失败或撤单时，解冻资金返回可用资金
   - 卖出不需要冻结资金

### 2. 更新账户资金
```http
PUT /api/v1/account/funds
```

**请求参数：**
```json
{
    "available_funds": 1000000.00,  // 可用资金
    "frozen_funds": 50000.00,       // 冻结资金
    "operation_type": "freeze",     // 操作类型：freeze/unfreeze/update
    "amount": 50000.00,            // 操作金额
    "remarks": "买入委托冻结"       // 操作说明
}
```

**响应示例：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "initial_assets": 300000.00,
        "total_assets": 1050000.00,
        "available_funds": 1000000.00,
        "frozen_funds": 50000.00,
        "total_profit": 750000.00,
        "total_profit_ratio": 250.00,
        "updated_at": "2024-03-21 16:00:00"
    }
}
```

**操作类型说明：**
1. **freeze（冻结）**
   - 从可用资金中扣除指定金额
   - 将该金额添加到冻结资金
   - 总资产保持不变
   - 常用于买入委托

2. **unfreeze（解冻）**
   - 从冻结资金中扣除指定金额
   - 将该金额返回到可用资金
   - 总资产保持不变
   - 常用于撤单或委托失败

3. **update（更新）**
   - 直接更新可用资金和冻结资金
   - 用于特殊情况下的资金调整
   - 需要管理员权限

**注意事项：**
1. 冻结资金时，可用资金必须大于等于冻结金额
2. 解冻资金时，冻结资金必须大于等于解冻金额
3. 资金更新后会自动重新计算总资产和收益率
4. 所有资金操作都会记录详细的日志

## 策略管理接口

### 1. 分析策略
```http
POST /api/v1/analyze_strategy
```

**请求参数：**
```json
{
    "strategy_text": "买入贵州茅台（600519）100股"
}
```

**响应示例：**
```json
{
    "code": 200,
    "message": "策略分析成功",
    "data": {
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "volume": 100,
        "analysis_result": "...",
        "confidence": 0.95,           // AI分析置信度
        "suggested_position": 0.1,    // AI建议仓位
        "market_analysis": {          // 市场分析
            "current_price": 1688.00,
            "pe_ratio": 28.5,
            "pb_ratio": 8.2,
            "market_trend": "上升"
        }
    }
}
```

### 2. 获取策略列表
```http
GET /api/v1/strategies
```

**查询参数：**
- sort_by: 排序字段（updated_at/created_at），默认 updated_at
- order: 排序方式（desc/asc），默认 desc
- status: 执行状态（pending/partial/completed），可选
- is_active: 是否有效（true/false），可选

**响应示例：**
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
            "position_ratio": 10.0,        // 仓位比例（%）
            "price_min": 1650.00,          // 最低买入价
            "price_max": 1700.00,          // 最高买入价
            "take_profit_price": 1800.00,  // 止盈价
            "stop_loss_price": 1600.00,    // 止损价
            "execution_status": "partial",  // 执行状态
            "is_active": true,             // 是否有效
            "created_at": "2024-03-21 15:00:00",
            "updated_at": "2024-03-21 16:00:00"
        }
    ]
}
```

**执行状态说明：**
1. **pending（未执行）**
   - 新创建的策略默认状态
   - 等待满足执行条件
   - 可以修改策略参数

2. **partial（部分执行）**
   - 策略已开始执行但未完成
   - 可能是因为分批执行
   - 可能是因为资金或股票不足
   - 仍然可以继续执行

3. **completed（已完成）**
   - 策略目标已完全达成
   - 不再继续执行
   - 如需继续操作需创建新策略

**策略有效性说明：**
1. **有效（is_active = true）**
   - 策略正常监控和执行
   - 可以被系统自动执行
   - 可以手动执行或修改

2. **无效（is_active = false）**
   - 策略停止监控和执行
   - 不会被系统自动执行
   - 仅用于历史记录查询
   - 可以手动重新激活

### 3. 创建策略
```http
POST /api/v1/strategies
```

**请求参数：**
```json
{
    "stock_name": "贵州茅台",
    "stock_code": "600519",
    "action": "buy",           // buy/sell/add/trim/hold
    "position_ratio": 10.0,    // 仓位比例（%）
    "price_min": 1650.00,      // 最低价格
    "price_max": 1700.00,      // 最高价格
    "take_profit_price": 1800.00,  // 止盈价
    "stop_loss_price": 1600.00,    // 止损价
    "other_conditions": "日线MACD金叉",  // 其他条件
    "reason": "基本面向好，技术面突破"    // 操作理由
}
```

**响应示例：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 10.0,
        "price_min": 1650.00,
        "price_max": 1700.00,
        "take_profit_price": 1800.00,
        "stop_loss_price": 1600.00,
        "other_conditions": "日线MACD金叉",
        "reason": "基本面向好，技术面突破",
        "execution_status": "pending",
        "is_active": true,
        "created_at": "2024-03-21 16:00:00",
        "updated_at": "2024-03-21 16:00:00"
    }
}
```

### 4. 更新策略
```http
PUT /api/v1/strategies/{id}
```

**请求参数：**
```json
{
    "position_ratio": 15.0,    // 新的仓位比例
    "price_min": 1660.00,      // 新的最低价格
    "price_max": 1710.00,      // 新的最高价格
    "take_profit_price": 1850.00,  // 新的止盈价
    "stop_loss_price": 1610.00,    // 新的止损价
    "other_conditions": "更新后的条件",  // 新的条件
    "reason": "更新后的理由"    // 新的理由
}
```

**响应示例：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 15.0,
        "price_min": 1660.00,
        "price_max": 1710.00,
        "take_profit_price": 1850.00,
        "stop_loss_price": 1610.00,
        "other_conditions": "更新后的条件",
        "reason": "更新后的理由",
        "execution_status": "pending",
        "is_active": true,
        "updated_at": "2024-03-21 16:30:00"
    }
}
```

**更新规则说明：**
1. **可更新字段**
   - 仓位比例（position_ratio）
   - 价格区间（price_min/price_max）
   - 止盈止损价（take_profit_price/stop_loss_price）
   - 其他条件（other_conditions）
   - 操作理由（reason）

2. **不可更新字段**
   - 股票代码（stock_code）
   - 股票名称（stock_name）
   - 操作类型（action）

3. **特殊情况处理**
   - 已完成策略增加仓位比例时，状态变更为部分执行
   - 部分执行的策略减少仓位比例时，可能变更为已完成
   - 无效策略不能更新参数

### 5. 检查策略是否存在
```http
POST /api/v1/strategies/check
```

**请求参数：**
```json
{
    "stock_name": "贵州茅台",
    "stock_code": "600519",
    "action": "buy"
}
```

**响应示例：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "exists": true,
        "strategy": {
            "id": 1,
            "stock_name": "贵州茅台",
            "stock_code": "600519",
            "action": "buy"
        }
    }
}
```

### 6. 设置策略状态
```http
POST /api/v1/strategies/{id}/deactivate  # 设置为失效
POST /api/v1/strategies/{id}/activate    # 设置为有效
```

**响应示例：**
```json
{
    "code": 200,
    "message": "策略已设置为失效/有效",
    "data": {
        "id": 1,
        "is_active": false/true,
        "updated_at": "2024-03-21 16:00:00"
    }
}
```

### 7. 高级查询策略
```http
GET /api/v1/strategies/search
```

**查询参数：**
- start_time: 开始时间
- end_time: 结束时间
- stock_code: 股票代码
- stock_name: 股票名称
- action: 交易动作
- sort_by: 排序字段
- order: 排序方式
- is_active: 是否有效

**响应示例：**
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
            "is_active": true,
            "created_at": "2024-03-21 15:00:00",
            "updated_at": "2024-03-21 16:00:00"
        }
    ]
}
```

### 8. 获取单个策略
```http
GET /api/v1/strategies/{id}
```

**响应示例：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "stock_name": "贵州茅台",
        "stock_code": "600519",
        "action": "buy",
        "position_ratio": 10.0,
        "price_min": 1650.00,
        "price_max": 1700.00,
        "take_profit_price": 1800.00,
        "stop_loss_price": 1600.00,
        "other_conditions": "日线MACD金叉",
        "reason": "基本面向好，技术面突破",
        "execution_status": "pending",
        "is_active": true,
        "created_at": "2024-03-21 16:00:00",
        "updated_at": "2024-03-21 16:00:00"
    }
}
```

## 策略执行记录接口

### 1. 创建执行记录
```http
POST /api/v1/executions
```

**请求参数：**
```json
{
    "strategy_id": 1,
    "stock_code": "600519",
    "stock_name": "贵州茅台",
    "action": "buy",
    "execution_price": 1800.00,
    "volume": 100,
    "position_ratio": 10.0,
    "original_position_ratio": 10.0,
    "remarks": "按计划执行"
}
```

**响应示例：**
```json
{
    "code": 200,
    "message": "创建执行记录成功",
    "data": {
        "id": 1,
        "strategy_id": 1,
        "stock_code": "600519",
        "stock_name": "贵州茅台",
        "action": "buy",
        "execution_price": 1800.00,
        "volume": 100,
        "position_ratio": 10.0,
        "original_position_ratio": 10.0,
        "execution_time": "2024-03-21 16:00:00",
        "execution_result": "success",
        "remarks": "按计划执行",
        "created_at": "2024-03-21 16:00:00"
    }
}
```

**执行结果说明：**
1. **success（成功）**
   - 交易完全按计划执行
   - 成交数量等于计划数量
   - 成交价格在预期范围内
   - 持仓和资金已正确更新
   - 原始仓位比例已更新（加仓/减仓时）

2. **partial（部分成功）**
   - 交易部分完成
   - 成交数量小于计划数量
   - 可能是因为资金不足
   - 可能是因为股票不足
   - 需要后续继续执行
   - 原始仓位比例按实际成交比例更新

3. **failed（失败）**
   - 交易完全未执行
   - 可能是因为价格超出范围
   - 可能是因为资金完全不足
   - 可能是因为股票完全不足
   - 可能是因为市场原因
   - 需要人工检查原因
   - 原始仓位比例不变

**原始仓位比例更新规则：**
1. **首次买入**
   - 设置初始的原始仓位比例
   - 例如：买入一成，original_position_ratio = 10.0

2. **加仓操作**
   - 执行成功时，累加原始仓位比例
   - 例如：原有一成，加仓一成
   - 新的原始仓位比例 = 10.0 + 10.0 = 20.0
   - 部分执行时按实际成交比例累加

3. **减仓操作**
   - 执行成功时，减少原始仓位比例
   - 例如：原有两成，减仓一成
   - 新的原始仓位比例 = 20.0 - 10.0 = 10.0
   - 部分执行时按实际成交比例减少

4. **清仓操作**
   - 完全卖出时，原始仓位比例清零
   - 后续重新买入时重新设置

5. **特殊情况处理**
   - 原始仓位比例不能超过100%
   - 原始仓位比例不能为负数
   - 执行失败时保持原值不变
   - 需要同步更新策略表中的记录

### 2. 查询执行记录列表
```http
GET /api/v1/executions
```

**查询参数：**
- strategy_id: 策略ID
- stock_code: 股票代码
- start_time: 开始时间（YYYY-MM-DD HH:mm:ss）
- end_time: 结束时间（YYYY-MM-DD HH:mm:ss）
- action: 交易动作（buy/sell/add/trim/hold）
- result: 执行结果（success/failed/partial）
- sort_by: 排序字段（execution_time/created_at）
- order: 排序方式（desc/asc）
- page: 页码，从1开始
- page_size: 每页记录数，默认20，最大100

**响应示例：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "total": 100,
        "page": 1,
        "page_size": 20,
        "items": [
            {
                "id": 1,
                "strategy_id": 1,
                "stock_code": "600519",
                "stock_name": "贵州茅台",
                "action": "buy",
                "execution_price": 1800.00,
                "volume": 100,
                "position_ratio": 10.0,
                "original_position_ratio": 10.0,
                "execution_time": "2024-03-21 16:00:00",
                "execution_result": "success",
                "remarks": "按计划执行",
                "created_at": "2024-03-21 16:00:00"
            }
        ]
    }
}
```

### 3. 批量获取执行记录
```http
POST /api/v1/executions/batch
```

**请求参数：**
```json
{
    "strategy_ids": [1, 2, 3],
    "start_time": "2024-03-21 00:00:00",
    "end_time": "2024-03-21 23:59:59",
    "page": 1,
    "page_size": 20
}
```

**响应示例：**
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "total": 100,
        "page": 1,
        "page_size": 20,
        "items": {
            "1": [
                {
                    "execution_id": 1,
                    "strategy_id": 1,
                    "execution_time": "2024-03-21 16:00:00",
                    "execution_price": 1800.00,
                    "volume": 100,
                    "execution_result": "success",
                    "created_at": "2024-03-21 16:00:00"
                }
            ]
        }
    }
}
```

**执行记录与策略状态关系：**
1. **策略状态更新规则**
   - 首次执行成功：pending -> partial/completed
   - 部分执行成功：partial -> partial/completed
   - 执行失败：状态不变
   - 全部完成：partial -> completed

2. **执行记录影响**
   - 影响策略的执行状态
   - 影响策略的剩余可执行数量
   - 影响持仓的数量和成本
   - 影响账户的资金状态

3. **特殊情况处理**
   - 策略无效时不能创建执行记录
   - 策略完成时不能创建执行记录
   - 执行记录不能删除或修改
   - 失败的执行记录可以重试

## 持仓管理接口

### 1. 获取持仓列表
```http
GET /api/v1/positions
```

**响应示例：**
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "id": 1,                           // 持仓记录ID
            "stock_code": "002953",            // 股票代码
            "stock_name": "日丰股份",          // 股票名称
            "total_volume": 3000,              // 持仓数量
            "original_cost": 10.50,            // 原始成本价
            "dynamic_cost": 10.50,             // 动态成本价
            "total_amount": 31500.00,          // 持仓金额
            "latest_price": 11.08,             // 最新价格
            "market_value": 33240.00,          // 市值
            "floating_profit": 1740.00,        // 浮动盈亏
            "floating_profit_ratio": 5.52381,  // 浮动盈亏比例(%)
            "original_position_ratio": 10.0,    // 原始仓位比例(%)
            "created_at": "2025-03-02 10:04:22", // 创建时间
            "updated_at": "2025-03-02 10:04:51"  // 更新时间
        }
    ]
}
```

**成本计算说明：**
1. **原始成本（original_cost）**
   - 首次买入时的成交均价
   - 不会因为后续操作而改变
   - 用于计算整体收益情况
   - 清仓后重新买入会更新

2. **动态成本（dynamic_cost）**
   - 考虑所有买入卖出后的均价
   - 买入时：新成本 = (原持仓量 × 原成本 + 买入量 × 买入价) ÷ 新持仓量
   - 卖出时：新成本 = (原持仓量 × 原成本 - 卖出量 × 卖出价) ÷ 新持仓量
   - 减仓时保持不变
   - 清仓后重置为0

3. **特殊情况处理**
   - 当动态成本 ≤ 0 时，浮动盈亏比例显示为 ♾️
   - 当持仓量为 0 时，所有成本重置为 0
   - 当市值为 0 时，浮动盈亏比例为 0

### 2. 获取持仓详情
```http
GET /api/v1/positions/{stock_code}
```

**响应示例：**
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "id": 1,
        "stock_code": "002953",
        "stock_name": "日丰股份",
        "total_volume": 3000,
        "original_cost": 10.50,
        "dynamic_cost": 10.50,
        "total_amount": 31500.00,
        "latest_price": 11.08,
        "market_value": 33240.00,
        "floating_profit": 1740.00,
        "floating_profit_ratio": 5.52381,
        "original_position_ratio": 10.0,
        "price_update_time": "2025-03-02 10:04:51",  // 价格更新时间
        "created_at": "2025-03-02 10:04:22",
        "updated_at": "2025-03-02 10:04:51",
        "trade_history": [                           // 交易历史
            {
                "action": "buy",
                "price": 10.50,
                "volume": 3000,
                "time": "2025-03-02 10:04:22"
            }
        ]
    }
}
```

### 3. 更新持仓市值
```http
PUT /api/v1/positions/{stock_code}/market_value
```

**请求参数：**
```json
{
    "latest_price": 11.08,            // 最新价格
    "update_time": "2025-03-02 10:04:51"  // 价格时间
}
```

**响应示例：**
```json
{
    "code": 200,
    "message": "更新市值成功",
    "data": {
        "stock_code": "002953",
        "latest_price": 11.08,
        "market_value": 33240.00,
        "floating_profit": 1740.00,
        "floating_profit_ratio": 5.52381,
        "price_update_time": "2025-03-02 10:04:51"
    }
}
```

**市值更新机制：**
1. **自动更新**
   - 每60秒自动获取最新价格
   - 交易时段内实时更新
   - 非交易时段停止更新
   - 价格变化超过0.1%才更新

2. **手动更新**
   - 通过API手动触发更新
   - 用于特殊情况处理
   - 需要提供价格时间戳
   - 会验证价格合理性

3. **数据验证**
   - 价格不能为负数或0
   - 价格变化不能超过20%
   - 时间戳必须合法
   - 非交易时段拒绝更新

### 4. 持仓操作说明

1. **买入操作**
   ```http
   POST /api/v1/positions/buy
   ```
   **请求参数：**
   ```json
   {
       "action": "buy",
       "stock_code": "002953",
       "stock_name": "日丰股份",
       "volume": 3000,
       "price": 10.50,
       "position_ratio": 10.0
   }
   ```
   **响应示例：**
   ```json
   {
       "code": 200,
       "message": "买入成功",
       "data": {
           "stock_code": "002953",
           "stock_name": "日丰股份",
           "total_volume": 3000,
           "original_cost": 10.50,
           "dynamic_cost": 10.50,
           "total_amount": 31500.00,
           "original_position_ratio": 10.0,
           "execution_time": "2025-03-02 10:04:22"
       }
   }
   ```
   - 创建新持仓记录
   - 记录原始成本和仓位
   - 冻结所需资金
   - 更新动态成本

2. **加仓操作**
   ```http
   POST /api/v1/positions/add
   ```
   **请求参数：**
   ```json
   {
       "action": "add",
       "stock_code": "002953",
       "volume": 2000,
       "price": 10.80,
       "position_ratio": 5.0
   }
   ```
   **响应示例：**
   ```json
   {
       "code": 200,
       "message": "加仓成功",
       "data": {
           "stock_code": "002953",
           "before_volume": 3000,
           "after_volume": 5000,
           "dynamic_cost": 10.62,
           "total_amount": 53100.00,
           "before_position_ratio": 10.0,
           "after_position_ratio": 15.0,  // 更新后的原始仓位比例
           "execution_time": "2025-03-02 10:04:22"
       }
   }
   ```
   - 增加持仓数量
   - 更新动态成本
   - 冻结所需资金
   - 更新原始仓位比例（累加）
   - 记录交易历史

3. **减仓操作**
   ```http
   POST /api/v1/positions/trim
   ```
   **请求参数：**
   ```json
   {
       "action": "trim",
       "stock_code": "002953",
       "volume": 1000,
       "price": 11.00,
       "position_ratio": 3.0
   }
   ```
   **响应示例：**
   ```json
   {
       "code": 200,
       "message": "减仓成功",
       "data": {
           "stock_code": "002953",
           "before_volume": 5000,
           "after_volume": 4000,
           "dynamic_cost": 10.62,
           "total_amount": 42480.00,
           "before_position_ratio": 15.0,
           "after_position_ratio": 12.0,  // 更新后的原始仓位比例
           "execution_time": "2025-03-02 10:04:22"
       }
   }
   ```
   - 减少持仓数量
   - 保持动态成本不变
   - 增加可用资金
   - 更新原始仓位比例（减少）
   - 记录交易历史

4. **卖出操作**
   ```http
   POST /api/v1/positions/sell
   ```
   **请求参数：**
   ```json
   {
       "action": "sell",
       "stock_code": "002953",
       "volume": 4000,
       "price": 11.20,
       "position_ratio": 100.0
   }
   ```
   **响应示例：**
   ```json
   {
       "code": 200,
       "message": "卖出成功",
       "data": {
           "stock_code": "002953",
           "before_volume": 4000,
           "after_volume": 0,
           "sell_amount": 44800.00,
           "total_profit": 2320.00,
           "profit_ratio": 5.45,
           "before_position_ratio": 12.0,
           "after_position_ratio": 0.0,  // 清仓后原始仓位比例清零
           "execution_time": "2025-03-02 10:04:22"
       }
   }
   ```
   - 减少或清空持仓
   - 更新动态成本
   - 增加可用资金
   - 清空原始仓位比例
   - 完全卖出时删除记录
   - 记录交易历史

**原始仓位比例更新规则：**
1. **加仓时更新**
   - 原始仓位比例 = 原比例 + 本次操作比例
   - 例如：原比例10% + 加仓5% = 新比例15%
   - 需要同步更新持仓记录和策略记录

2. **减仓时更新**
   - 原始仓位比例 = 原比例 - 本次操作比例
   - 例如：原比例15% - 减仓3% = 新比例12%
   - 需要同步更新持仓记录和策略记录

3. **清仓时处理**
   - 原始仓位比例清零
   - 删除持仓记录
   - 策略状态设为已完成

4. **数据验证**
   - 加仓后总仓位不超过100%
   - 减仓后仓位不小于0%
   - 仓位变更必须同步到相关表

5. **异常处理**
   - 操作失败时回滚仓位变更
   - 部分成交按比例调整
   - 记录详细的变更日志

### 5. 持仓数据验证规则

1. **数量验证**
   - 买入数量必须大于0
   - 卖出数量不能超过持仓
   - 减仓数量必须合理
   - 总量必须为整数

2. **价格验证**
   - 价格必须大于0
   - 价格不能偏离市场价过大
   - 价格精度不超过2位小数
   - 需要在合理范围内

3. **仓位验证**
   - 仓位比例在0-100之间
   - 总仓位不能超过100%
   - 减仓比例不能过大
   - 必须考虑其他持仓

4. **资金验证**
   - 买入时资金必须足够
   - 需要考虑交易费用
   - 预留安全余额
   - 防止资金占用过大

### 6. 批量获取持仓记录
```http
POST /api/v1/positions/batch
```

**请求参数：**
```json
{
    "stock_codes": ["002953", "600519"],
    "limit": 10
}
```

**响应示例：**
```json
{
    "code": 200,
    "message": "获取成功",
    "data": {
        "002953": {
            "id": 1,
            "stock_code": "002953",
            "stock_name": "日丰股份",
            "total_volume": 3000,
            "original_cost": 10.50,
            "dynamic_cost": 10.50,
            "total_amount": 31500.00,
            "latest_price": 11.08,
            "market_value": 33240.00,
            "floating_profit": 1740.00,
            "floating_profit_ratio": 5.52381,
            "original_position_ratio": 10.0,
            "created_at": "2025-03-02 10:04:22",
            "updated_at": "2025-03-02 10:04:51"
        },
        "600519": {
            "id": 2,
            "stock_code": "600519",
            "stock_name": "贵州茅台",
            "total_volume": 100,
            "original_cost": 1800.00,
            "dynamic_cost": 1800.00,
            "total_amount": 180000.00,
            "latest_price": 1850.00,
            "market_value": 185000.00,
            "floating_profit": 5000.00,
            "floating_profit_ratio": 0.0277,
            "original_position_ratio": 0.1,
            "created_at": "2024-03-21 16:00:00",
            "updated_at": "2024-03-21 16:00:00"
        }
    }
}
``` 