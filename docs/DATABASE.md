# QMT Server 数据库设计文档

## 数据库信息
- 数据库名称：stock_strategy
- 字符集：utf8mb4
- 排序规则：utf8mb4_unicode_ci

## 表结构说明

### 策略表（strategies）

#### 字段说明
| 字段名 | 类型 | 是否必填 | 默认值 | 说明 |
|--------|------|----------|---------|------|
| id | INTEGER | 是 | 自增 | 主键 |
| stock_name | VARCHAR(32) | 是 | - | 股票名称 |
| stock_code | VARCHAR(16) | 是 | - | 股票代码 |
| action | VARCHAR(8) | 是 | - | 交易动作（buy/sell） |
| position_ratio | DECIMAL(5,4) | 是 | - | 仓位比例（0-1） |
| price_min | DECIMAL(10,2) | 否 | NULL | 最低价格 |
| price_max | DECIMAL(10,2) | 否 | NULL | 最高价格 |
| take_profit_price | DECIMAL(10,2) | 否 | NULL | 止盈价格 |
| stop_loss_price | DECIMAL(10,2) | 否 | NULL | 止损价格 |
| other_conditions | TEXT | 否 | NULL | 其他条件 |
| reason | TEXT | 否 | NULL | 操作理由 |
| execution_status | VARCHAR(16) | 是 | 'pending' | 执行状态（pending/partial/completed） |
| is_active | BOOLEAN | 是 | TRUE | 是否有效 |
| created_at | TIMESTAMP | 是 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 是 | CURRENT_TIMESTAMP | 更新时间 |

#### 索引说明
- PRIMARY KEY (id)
- INDEX idx_stock_code (stock_code)
- INDEX idx_created_at (created_at)
- INDEX idx_updated_at (updated_at)
- INDEX idx_execution_status (execution_status)

### 策略执行记录表（executions）

#### 字段说明
| 字段名 | 类型 | 是否必填 | 默认值 | 说明 |
|--------|------|----------|---------|------|
| id | INTEGER | 是 | 自增 | 主键 |
| strategy_id | INTEGER | 是 | - | 策略ID |
| stock_code | VARCHAR(16) | 是 | - | 股票代码 |
| stock_name | VARCHAR(32) | 是 | - | 股票名称 |
| action | VARCHAR(8) | 是 | - | 交易动作（buy/sell） |
| execution_price | DECIMAL(10,2) | 是 | - | 执行价格 |
| volume | INTEGER | 是 | - | 交易量 |
| execution_time | TIMESTAMP | 是 | CURRENT_TIMESTAMP | 执行时间 |
| execution_result | VARCHAR(16) | 是 | - | 执行结果（success/failed/partial） |
| remarks | TEXT | 否 | NULL | 备注说明 |
| created_at | TIMESTAMP | 是 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 是 | CURRENT_TIMESTAMP | 更新时间 |

#### 索引说明
- PRIMARY KEY (id)
- FOREIGN KEY (strategy_id) REFERENCES strategies(id)
- INDEX idx_stock_code (stock_code)
- INDEX idx_execution_time (execution_time)
- INDEX idx_created_at (created_at)

### 持仓表（positions）

#### 字段说明
| 字段名 | 类型 | 是否必填 | 默认值 | 说明 |
|--------|------|----------|---------|------|
| id | INTEGER | 是 | 自增 | 主键 |
| stock_code | VARCHAR(16) | 是 | - | 股票代码 |
| stock_name | VARCHAR(32) | 是 | - | 股票名称 |
| total_volume | INTEGER | 是 | 0 | 总持仓量 |
| original_cost | DECIMAL(10,2) | 是 | 0 | 原始成本 |
| dynamic_cost | DECIMAL(10,2) | 是 | 0 | 动态成本 |
| total_amount | DECIMAL(12,2) | 是 | 0 | 总金额 |
| latest_price | DECIMAL(10,2) | 是 | 0 | 最新价格 |
| market_value | DECIMAL(12,2) | 是 | 0 | 市值 |
| floating_profit | DECIMAL(12,2) | 是 | 0 | 浮动盈亏 |
| floating_profit_ratio | DECIMAL(10,4) | 是 | 0 | 盈亏比例 |
| created_at | TIMESTAMP | 是 | CURRENT_TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 是 | CURRENT_TIMESTAMP | 更新时间 |

#### 索引说明
- PRIMARY KEY (id)
- UNIQUE INDEX idx_stock_code (stock_code)
- INDEX idx_created_at (created_at)
- INDEX idx_updated_at (updated_at)

#### 特殊值说明
1. **浮动盈亏比例（floating_profit_ratio）**
   - 正常情况：实际的盈亏比例值
   - 特殊情况：当 dynamic_cost <= 0 时，该字段值为 999999
   - 前端显示：当值为 999999 时显示为 ♾️ 符号

2. **卖出限制**
   - 卖出数量不能超过当前持仓量
   - 违反限制时会抛出业务异常

## 数据库关系图
```mermaid
erDiagram
    strategies ||--o{ executions : "has"
    strategies {
        int id PK
        string stock_name
        string stock_code
        string action
        decimal position_ratio
        decimal price_min
        decimal price_max
        decimal take_profit_price
        decimal stop_loss_price
        text other_conditions
        text reason
        string execution_status
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    executions {
        int id PK
        int strategy_id FK
        string stock_code
        string stock_name
        string action
        decimal execution_price
        int volume
        timestamp execution_time
        string execution_result
        text remarks
        timestamp created_at
        timestamp updated_at
    }
    positions {
        int id PK
        string stock_code
        string stock_name
        int total_volume
        decimal original_cost
        decimal dynamic_cost
        decimal total_amount
        decimal latest_price
        decimal market_value
        decimal floating_profit
        decimal floating_profit_ratio
        timestamp created_at
        timestamp updated_at
    }
``` 