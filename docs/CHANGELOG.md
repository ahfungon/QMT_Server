# 更新日志

## 2024-03-02

### 性能优化
- **股票价格获取优化**
  - 添加价格缓存机制，减少重复API请求
  - 设置60秒的缓存过期时间，平衡实时性和性能
  - 优化批量更新逻辑，减少数据库操作次数

### 前端稳定性提升
- **资源加载可靠性**
  - 添加Bootstrap和Axios资源加载错误处理
  - 实现资源加载超时检测机制
  - 添加备用CDN资源自动切换功能
  
- **模态框操作安全性**
  - 重构模态框显示和隐藏逻辑，增加错误处理
  - 添加Bootstrap库加载检查，防止JS错误
  - 统一模态框操作接口，提高代码可维护性

### 用户体验改进
- **刷新按钮交互优化**
  - 为策略卡片和执行记录页面的刷新按钮添加旋转加载效果
  - 统一所有页面的刷新按钮交互体验
  - 添加按钮禁用状态，防止重复点击

- **错误提示优化**
  - 添加友好的错误提示模态框
  - 在资源加载失败时提供明确的错误信息
  - 提供页面刷新选项，方便用户快速恢复

### 问题修复
- **仓位比例显示修复**
  - 修复策略卡片中仓位比例显示异常的问题
  - 更新策略编辑表单，支持0-100的百分比输入
  - 调整仓位比例验证逻辑，确保数据一致性

- **买入操作资金扣除修复**
  - 修复买入/加仓操作时未从账户资金中扣除相应金额的问题
  - 实现卖出/减仓操作时自动向账户资金中增加交易金额的功能
  - 添加资金不足时的错误处理和提示
  - 更新API文档，补充资金处理相关说明

## 2024-03-01

### 新增功能
- 添加支持多种操作类型：buy(买入)、sell(卖出)、add(加仓)、trim(减仓)和hold(持有)
- 为持仓添加原始仓位比例记录，用于减仓操作的计算
- 将仓位比例从小数形式(0-1)转换为整数百分比形式(0-100)，更直观易用

### 数据库更新
- 修改 `stock_strategies` 和 `strategy_executions` 表的 `action` 字段，支持五种操作类型
- 调整 `position_ratio` 字段类型为 DECIMAL(5,2)，并更新注释
- 在 `stock_positions` 表中添加 `original_position_ratio` 字段
- 在 `strategy_executions` 表中添加 `position_ratio` 字段
- 自动将现有数据中的仓位比例从小数形式转换为百分比形式

### 文档更新
- 更新 API 文档，添加新操作类型的说明
- 更新数据库设计文档，反映最新的数据库结构
- 更新部署文档，添加数据库迁移的说明

## 2024-02-15

### 新增功能
- **浮动盈亏比例显示优化**
  - 当动态成本小于等于0时，数据库中记录为999999
  - 前端页面显示为 ♾️ 符号
  - 优化了总盈亏比例的计算逻辑

### 安全性改进
- **持仓卖出安全机制**
  - 增加了双重验证机制，防止超量卖出
  - 在服务层和模型层都增加了数量验证
  - 添加了友好的错误提示

### 用户体验优化
- **前端展示优化**
  - 优化了持仓列表的总计行显示
  - 修复了重复显示总计行的问题
  - 统一了数值的格式化显示 