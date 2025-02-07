# QMT Server

QMT Server 是一个基于 Flask 的 API 服务，主要功能是根据传入的策略信息，调用 AI 功能进行加工处理，并确立相应的股票交易策略，存入数据库。

## 功能特点

- 使用 AI 分析自然语言策略文本
- 支持多种 AI 模型（智谱AI、DeepSeek）
- RESTful API 接口设计
- 完整的策略管理功能
- 详细的日志记录
- 支持多环境配置

## 技术栈

- Python 3.10+
- Flask 3.0.0
- SQLAlchemy 2.0.27
- MySQL
- 智谱AI/DeepSeek API

## 项目结构

```
QMT_Server/
├── app/                    # 应用主目录
│   ├── models/            # 数据模型
│   ├── routes/            # 路由定义
│   ├── services/          # 业务逻辑
│   ├── utils/             # 工具函数
│   └── templates/         # 模板文件
├── ai_robot/              # AI处理模块
│   ├── base.py           # 基础处理器
│   ├── zhipu.py          # 智谱AI处理器
│   └── deepseek.py       # DeepSeek处理器
├── config/                # 配置文件
├── docs/                  # 文档
├── logs/                  # 日志文件
├── scripts/              # 脚本文件
├── tests/                # 测试文件
├── .env                  # 环境变量
├── .env.example          # 环境变量示例
├── requirements.txt      # 依赖清单
└── run.py               # 启动文件
```

## 安装部署

1. 克隆项目
```bash
git clone [项目地址]
cd QMT_Server
```

2. 创建虚拟环境
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# 或
.venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置信息
```

5. 初始化数据库
```bash
python scripts/init_db.py
```

6. 启动服务
```bash
python run.py
```

## API 文档

详细的 API 文档请参考 [API_DOCUMENT.md](API_DOCUMENT.md)

## 开发指南

### 代码规范
- 变量名和函数名使用 camelCase 规范
- 组件名使用 PascalCase 规范
- 使用中文注释与描述
- 使用中文错误信息
- 使用中文日志

### 测试
```bash
pytest tests/
pytest --cov=app tests/  # 测试覆盖率
```

### 日志
- 日志文件位于 `logs/` 目录
- 开发环境日志：`dev.log`
- 生产环境日志：`production.log`

## 环境变量说明

- `FLASK_ENV`: 运行环境（development/production）
- `FLASK_DEBUG`: 调试模式（0/1）
- `MYSQL_*`: 数据库相关配置
- `AI_TYPE`: AI模型选择（zhipu/deepseek）
- `ZHIPU_API_KEY`: 智谱AI的API密钥
- `DEEPSEEK_API_KEY`: DeepSeek的API密钥

## 贡献指南

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

[MIT License](LICENSE)

## 联系方式

- 作者：阿房
- 邮箱：[your-email@example.com] 