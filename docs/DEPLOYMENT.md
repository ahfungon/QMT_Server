## 系统更新记录

### 2024-02-15 更新
1. **浮动盈亏比例显示优化**
   - 当动态成本小于等于0时，数据库中记录为999999
   - 前端页面显示为 ♾️ 符号
   - 优化了总盈亏比例的计算逻辑

2. **持仓卖出安全机制**
   - 增加了双重验证机制，防止超量卖出
   - 在服务层和模型层都增加了数量验证
   - 添加了友好的错误提示

3. **前端展示优化**
   - 优化了持仓列表的总计行显示
   - 修复了重复显示总计行的问题
   - 统一了数值的格式化显示 

# 部署文档

## 系统要求

- Python 3.10+
- MySQL 8.0+
- 操作系统：Linux/macOS/Windows

## 环境准备

### 1. 安装 Python 依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Linux/macOS
source venv/bin/activate
# Windows
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置数据库

```bash
# 创建数据库
mysql -u root -p
```

```sql
CREATE DATABASE stock_strategy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'qmt_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON stock_strategy.* TO 'qmt_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 3. 配置环境变量

创建 `.env` 文件，配置以下环境变量：

```
# 数据库配置
DB_HOST=localhost
DB_PORT=3306
DB_NAME=stock_strategy
DB_USER=qmt_user
DB_PASSWORD=your_password

# 应用配置
FLASK_APP=app.py
FLASK_ENV=production
SECRET_KEY=your_secret_key

# 智谱AI配置
ZHIPU_API_KEY=your_zhipu_api_key

# DeepSeek AI配置
DEEPSEEK_API_KEY=your_deepseek_api_key
```

## 数据库初始化

### 1. 初始化数据库

```bash
# 初始化数据库
python scripts/init_db.py
```

### 2. 生成测试数据（可选）

```bash
# 生成测试数据
python scripts/test_data.py
```

### 3. 数据库迁移

当需要更新数据库结构时，可以使用以下两种方式之一：

#### 方式一：使用 Python 脚本（推荐）

```bash
# 更新数据库以支持新的操作类型
python scripts/update_db_for_new_actions.py
```

#### 方式二：直接执行 SQL 脚本

```bash
# 使用 MySQL 客户端执行更新脚本
mysql -u qmt_user -p < scripts/update_db_schema.sql
```

**注意**：如果您是首次安装系统，则不需要执行上述迁移步骤，因为初始化数据库时已经包含了最新的结构。

## 应用部署

### 方式一：直接运行

```bash
# 启动应用
python run.py
```

### 方式二：使用 Gunicorn（推荐用于生产环境）

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动应用
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### 方式三：使用 Docker

```bash
# 构建镜像
docker build -t qmt-server .

# 运行容器
docker run -d -p 5000:5000 --name qmt-server --env-file .env qmt-server
```

## 部署后验证

访问以下接口验证部署是否成功：

```
GET http://localhost:5000/api/v1/health
```

预期返回：

```json
{
  "code": 200,
  "message": "服务正常运行",
  "data": {
    "status": "ok",
    "version": "1.0.0",
    "timestamp": "2023-06-01T12:00:00Z"
  }
}
```

## 日志管理

日志文件存储在 `logs` 目录下，按日期分割：

- `app.log` - 当前日志
- `app.log.YYYY-MM-DD` - 历史日志

查看日志：

```bash
# 查看最新日志
tail -f logs/app.log

# 查看错误日志
grep ERROR logs/app.log
```

## 备份与恢复

### 数据库备份

```bash
# 备份数据库
mysqldump -u qmt_user -p stock_strategy > backup/stock_strategy_$(date +%Y%m%d).sql
```

### 数据库恢复

```bash
# 恢复数据库
mysql -u qmt_user -p stock_strategy < backup/stock_strategy_20230601.sql
```

## 常见问题

### 1. 数据库连接失败

检查 `.env` 文件中的数据库配置是否正确，确保数据库服务正在运行。

### 2. API 调用失败

检查 `.env` 文件中的 API 密钥配置是否正确，确保网络连接正常。

### 3. 服务无法启动

检查日志文件 `logs/app.log` 中的错误信息，确保所有依赖已正确安装。

## 联系支持

如有任何问题，请联系技术支持团队：

- 邮箱：support@example.com
- 电话：123-456-7890 