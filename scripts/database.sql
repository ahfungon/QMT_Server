-- 创建数据库
CREATE DATABASE IF NOT EXISTS stock_strategy DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE stock_strategy;

-- 创建股票策略表
CREATE TABLE IF NOT EXISTS stock_strategies (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_name VARCHAR(100) NOT NULL COMMENT '股票名称',
    stock_code VARCHAR(20) NOT NULL COMMENT '股票代码',
    action ENUM('buy', 'sell') NOT NULL COMMENT '执行动作',
    position_ratio FLOAT NOT NULL COMMENT '操作比例',
    price_min FLOAT COMMENT '最小执行价',
    price_max FLOAT COMMENT '最大执行价',
    take_profit_price FLOAT COMMENT '止盈价',
    stop_loss_price FLOAT COMMENT '止损价',
    other_conditions TEXT COMMENT '其他操作条件',
    reason TEXT COMMENT '操作理由',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '策略制定时间',
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '策略修正时间',
    is_active BOOLEAN NOT NULL DEFAULT TRUE COMMENT '策略是否有效',
    
    INDEX idx_stock_code (stock_code),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='股票策略表';

-- 添加一些示例数据（可选）
INSERT INTO stock_strategies (
    stock_name, stock_code, action, position_ratio,
    price_min, price_max, take_profit_price, stop_loss_price,
    other_conditions, reason
) VALUES (
    '贵州茅台', '600519', 'buy', 0.3,
    2000.00, 2100.00, 2300.00, 1900.00,
    'MACD金叉，成交量放大', '技术面突破，看好未来发展'
), (
    '腾讯控股', '00700', 'sell', 0.5,
    380.00, 400.00, 420.00, 360.00,
    'KDJ超买，股价创新高', '获利了结，降低仓位'
); 