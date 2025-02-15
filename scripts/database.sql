-- 创建数据库
CREATE DATABASE IF NOT EXISTS stock_strategy DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE stock_strategy;

-- 创建股票策略表
CREATE TABLE IF NOT EXISTS stock_strategies (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '策略ID',
    stock_name VARCHAR(100) NOT NULL COMMENT '股票名称',
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    action ENUM('buy', 'sell') NOT NULL COMMENT '执行动作',
    position_ratio FLOAT NOT NULL COMMENT '操作比例',
    price_min FLOAT NULL COMMENT '最小执行价',
    price_max FLOAT NULL COMMENT '最大执行价',
    take_profit_price FLOAT NULL COMMENT '止盈价',
    stop_loss_price FLOAT NULL COMMENT '止损价',
    other_conditions TEXT NULL COMMENT '其他操作条件',
    reason TEXT NULL COMMENT '操作理由',
    execution_status ENUM('pending', 'completed', 'partial') NOT NULL DEFAULT 'pending' COMMENT '执行状态：未执行、已全部执行、已部分执行',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '策略制定时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '策略修正时间',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '策略是否有效',
    INDEX idx_stock_code (stock_code),
    INDEX idx_created_at (created_at),
    INDEX idx_updated_at (updated_at),
    INDEX idx_is_active (is_active),
    INDEX idx_execution_status (execution_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票策略表';

-- 创建策略执行记录表
CREATE TABLE IF NOT EXISTS strategy_executions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '执行记录ID',
    strategy_id INT NOT NULL COMMENT '策略ID',
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(100) NOT NULL COMMENT '股票名称',
    action ENUM('buy', 'sell') NOT NULL COMMENT '执行操作',
    execution_price FLOAT NOT NULL COMMENT '执行价格',
    volume INT NOT NULL COMMENT '交易量',
    execution_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '执行时间',
    execution_result ENUM('success', 'failed', 'partial') NOT NULL COMMENT '执行结果',
    remarks TEXT NULL COMMENT '备注说明',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_strategy_id (strategy_id),
    INDEX idx_stock_code (stock_code),
    INDEX idx_execution_time (execution_time),
    INDEX idx_execution_result (execution_result),
    FOREIGN KEY (strategy_id) REFERENCES stock_strategies(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='策略执行记录表';

-- 创建持仓表
CREATE TABLE IF NOT EXISTS stock_positions (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '持仓ID',
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    stock_name VARCHAR(100) NOT NULL COMMENT '股票名称',
    total_volume INT NOT NULL DEFAULT 0 COMMENT '持仓数量',
    original_cost FLOAT NOT NULL DEFAULT 0 COMMENT '原始平均成本',
    dynamic_cost FLOAT NOT NULL DEFAULT 0 COMMENT '动态成本价（股票软件风格）',
    total_amount FLOAT NOT NULL DEFAULT 0 COMMENT '持仓金额',
    latest_price FLOAT NULL COMMENT '最新价格',
    market_value FLOAT NULL COMMENT '市值',
    floating_profit FLOAT NULL COMMENT '浮动盈亏',
    floating_profit_ratio FLOAT NULL COMMENT '浮动盈亏比例',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_stock_code (stock_code),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票持仓表';

-- 创建数据库用户并授权（如果需要）
-- CREATE USER IF NOT EXISTS 'qmt_user'@'localhost' IDENTIFIED BY 'your_password';
-- GRANT ALL PRIVILEGES ON stock_strategy.* TO 'qmt_user'@'localhost';
-- FLUSH PRIVILEGES;

-- 添加一些测试数据（可选）
INSERT INTO stock_strategies (
    stock_name, stock_code, action, position_ratio,
    price_min, price_max, take_profit_price, stop_loss_price,
    other_conditions, reason,
    created_at, updated_at
) VALUES (
    '贵州茅台', '600519', 'buy', 0.1,
    1500, 1600, 1700, 1450,
    '日线MACD金叉', '技术面向好，估值合理',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

INSERT INTO strategy_executions (
    strategy_id, stock_code, stock_name, action,
    execution_price, volume, execution_result, remarks,
    execution_time, created_at, updated_at
) VALUES (
    1, '600519', '贵州茅台', 'buy',
    1550, 100, 'success', '按计划执行完成',
    CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
);

INSERT INTO stock_positions (
    stock_code, stock_name, total_volume, original_cost, dynamic_cost, total_amount
) VALUES (
    '600519', '贵州茅台', 100, 1550.5, 1550.5, 155050
); 