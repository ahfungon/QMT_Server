-- 创建数据库
CREATE DATABASE IF NOT EXISTS stock_strategy DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE stock_strategy;

-- 创建账户资金表
CREATE TABLE IF NOT EXISTS account_funds (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '账户ID',
    initial_assets DECIMAL(12,2) NOT NULL DEFAULT 300000.00 COMMENT '初始资金',
    total_assets DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '资产总值',
    available_funds DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '可用资金',
    frozen_funds DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '冻结资金',
    total_profit DECIMAL(12,2) NOT NULL DEFAULT 0 COMMENT '总盈亏',
    total_profit_ratio DECIMAL(10,4) NOT NULL DEFAULT 0 COMMENT '总收益率',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='账户资金表';

-- 插入初始资金记录（30万）
INSERT INTO account_funds (initial_assets, total_assets, available_funds, frozen_funds, total_profit, total_profit_ratio)
VALUES (300000.00, 300000.00, 300000.00, 0.00, 0.00, 0.00);

-- 创建股票策略表
CREATE TABLE IF NOT EXISTS stock_strategies (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '策略ID',
    stock_name VARCHAR(100) NOT NULL COMMENT '股票名称',
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    action ENUM('buy', 'sell', 'add', 'trim', 'hold') NOT NULL COMMENT '执行动作',
    position_ratio DECIMAL(5,2) NOT NULL COMMENT '操作比例（0-100整数表示百分比）',
    original_position_ratio DECIMAL(5,2) NULL COMMENT '原始买入仓位比例',
    price_min FLOAT NULL COMMENT '最小执行价',
    price_max FLOAT NULL COMMENT '最大执行价',
    take_profit_price FLOAT NULL COMMENT '止盈价',
    stop_loss_price FLOAT NULL COMMENT '止损价',
    other_conditions TEXT NULL COMMENT '其他操作条件',
    reason TEXT NULL COMMENT '操作理由',
    execution_status ENUM('pending', 'completed', 'partial') NOT NULL DEFAULT 'pending' COMMENT '执行状态：未执行、已全部执行、已部分执行',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '策略是否有效',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '策略制定时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '策略修正时间',
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
    action ENUM('buy', 'sell', 'add', 'trim', 'hold') NOT NULL COMMENT '执行操作',
    execution_price FLOAT NOT NULL COMMENT '执行价格',
    volume INT NOT NULL COMMENT '交易量',
    position_ratio DECIMAL(5,2) NULL COMMENT '仓位比例（0-100整数表示百分比）',
    original_position_ratio DECIMAL(5,2) NULL COMMENT '原始买入仓位比例',
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
    original_position_ratio DECIMAL(5,2) NULL COMMENT '原始仓位比例（0-100整数表示百分比）',
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
-- INSERT INTO stock_strategies (
--     stock_name, stock_code, action, position_ratio,
--     price_min, price_max, take_profit_price, stop_loss_price,
--     other_conditions, reason, execution_status, is_active,
--     created_at, updated_at
-- ) VALUES (
--     '掌趣科技', '300315', 'buy', 20.0,
--     5.9, 6.0, 7.5, 5.1,
--     '日线MACD金叉', '技术面向好，估值合理', 'completed', FALSE,
--     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
-- );

-- -- 加仓策略测试数据
-- INSERT INTO stock_strategies (
--     stock_name, stock_code, action, position_ratio,
--     price_min, price_max, take_profit_price, stop_loss_price,
--     other_conditions, reason, execution_status, is_active,
--     created_at, updated_at
-- ) VALUES (
--     '东方财富', '300059', 'add', 10.0,
--     15.5, 16.0, 19.0, 14.5,
--     '放量突破', '周线站上MA20，趋势良好', 'pending', TRUE,
--     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
-- );

-- -- 减仓策略测试数据
-- INSERT INTO stock_strategies (
--     stock_name, stock_code, action, position_ratio,
--     price_min, price_max, take_profit_price, stop_loss_price,
--     other_conditions, reason, execution_status, is_active,
--     created_at, updated_at
-- ) VALUES (
--     '中国平安', '601318', 'trim', 15.0,
--     40.5, 41.0, NULL, NULL,
--     '减少高估值持仓', '临近阻力位，获利了结部分仓位', 'pending', TRUE,
--     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
-- );

-- -- 持有策略测试数据
-- INSERT INTO stock_strategies (
--     stock_name, stock_code, action, position_ratio,
--     price_min, price_max, take_profit_price, stop_loss_price,
--     other_conditions, reason, execution_status, is_active,
--     created_at, updated_at
-- ) VALUES (
--     '贵州茅台', '600519', 'hold', 20.0,
--     NULL, NULL, 2100.0, 1800.0,
--     '估值合理，业绩稳定', '维持现有仓位，等待业绩释放', 'pending', TRUE,
--     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
-- );

-- -- 卖出策略测试数据
-- INSERT INTO stock_strategies (
--     stock_name, stock_code, action, position_ratio,
--     price_min, price_max, take_profit_price, stop_loss_price,
--     other_conditions, reason, execution_status, is_active,
--     created_at, updated_at
-- ) VALUES (
--     '万科A', '000002', 'sell', 100.0,
--     18.6, 19.0, NULL, NULL,
--     '成交量持续萎缩', '地产股持续承压，规避风险', 'pending', TRUE,
--     CURRENT_TIMESTAMP, CURRENT_TIMESTAMP
-- );

-- INSERT INTO strategy_executions (
--     strategy_id, stock_code, stock_name, action,
--     execution_price, volume, position_ratio, original_position_ratio, execution_result, remarks,
--     execution_time, created_at, updated_at
-- ) VALUES (
--     1, '300315', '掌趣科技', 'buy',
--     5.804, 10100, 20.0, 20.0, 'success', '按计划执行完成',
--     NOW() - INTERVAL 3 DAY, NOW() - INTERVAL 3 DAY, NOW() - INTERVAL 3 DAY
-- );

-- -- 添加持仓记录
-- INSERT INTO stock_positions (
--     stock_code, stock_name, total_volume, original_cost, dynamic_cost,
--     total_amount, latest_price, market_value, floating_profit, floating_profit_ratio,
--     original_position_ratio, created_at, updated_at
-- ) VALUES (
--     '300315', '掌趣科技', 10100, 5.804, 5.804,
--     58620.4, 5.58, 56358.0, -2262.4, -0.0386,
--     20.0, NOW(), NOW()
-- );

-- -- 东方财富持仓记录
-- INSERT INTO stock_positions (
--     stock_code, stock_name, total_volume, original_cost, dynamic_cost,
--     total_amount, latest_price, market_value, floating_profit, floating_profit_ratio,
--     original_position_ratio, created_at, updated_at
-- ) VALUES (
--     '300059', '东方财富', 5000, 15.2, 15.2,
--     76000.0, 15.8, 79000.0, 3000.0, 0.0395,
--     25.0, NOW(), NOW()
-- );

-- -- 中国平安持仓记录
-- INSERT INTO stock_positions (
--     stock_code, stock_name, total_volume, original_cost, dynamic_cost,
--     total_amount, latest_price, market_value, floating_profit, floating_profit_ratio,
--     original_position_ratio, created_at, updated_at
-- ) VALUES (
--     '601318', '中国平安', 2000, 39.5, 39.5,
--     79000.0, 40.2, 80400.0, 1400.0, 0.0177,
--     25.0, NOW(), NOW()
-- );

-- -- 贵州茅台持仓记录
-- INSERT INTO stock_positions (
--     stock_code, stock_name, total_volume, original_cost, dynamic_cost,
--     total_amount, latest_price, market_value, floating_profit, floating_profit_ratio,
--     original_position_ratio, created_at, updated_at
-- ) VALUES (
--     '600519', '贵州茅台', 50, 1850.0, 1850.0,
--     92500.0, 1950.0, 97500.0, 5000.0, 0.0541,
--     30.0, NOW(), NOW()
-- );

-- -- 万科A持仓记录
-- INSERT INTO stock_positions (
--     stock_code, stock_name, total_volume, original_cost, dynamic_cost,
--     total_amount, latest_price, market_value, floating_profit, floating_profit_ratio,
--     original_position_ratio, created_at, updated_at
-- ) VALUES (
--     '000002', '万科A', 2000, 18.0, 18.0,
--     36000.0, 18.5, 37000.0, 1000.0, 0.0278,
--     10.0, NOW(), NOW()
-- );

-- -- 4. 更新账户资金（扣除买入金额）
-- UPDATE account_funds 
-- SET 
--     available_funds = available_funds - 58620.4,
--     total_assets = available_funds + frozen_funds + 58620.4,
--     total_profit = total_assets - initial_assets,
--     total_profit_ratio = ((total_assets - initial_assets) / initial_assets) * 100,
--     updated_at = CURRENT_TIMESTAMP 
-- WHERE id = 1; 