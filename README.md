# QMT Server

这是一个基于 Flask 的 API 接口服务，主要功能是根据传入的策略信息，进调用 AI 功能进行加工处理，并确立相应的股票交易策略，存入数据库。

## 项目依赖
- Python 3.10 及以上版本
- Flask 框架
- SQLAlchemy 进行数据库操作
- Pytest 进行单元测试
- Pytest-cov 进行测试覆盖率统计
- Pytest-mock 进行测试模拟

## 文件结构
```
QMT_Server/
├── app/                    # 主应用目录
│   ├── __init__.py        # 应用初始化
│   ├── models/            # 数据模型
│   ├── routes/            # 路由定义
│   ├── templates/         # 模板文件
│   ├── static/            # 静态文件
│   └── utils/             # 工具函数
├── ai_robot/              # AI 机器人模块
│   ├── __init__.py        # AI 处理器工厂
│   ├── base.py           # 基础 AI 处理器
│   ├── zhipu.py          # 智谱 AI 实现
│   └── deepseek.py       # DeepSeek AI 实现
├── config/                # 配置文件目录
│   ├── __init__.py       # 配置加载
│   └── settings.py       # 配置定义
├── docs/                  # 文档目录
├── logs/                  # 日志目录
├── scripts/               # 脚本目录
├── tests/                 # 测试目录
├── .env                   # 环境变量
├── .env.example          # 环境变量示例
├── .gitignore            # Git 忽略文件
├── requirements.txt      # 项目依赖
└── run.py                # 应用启动文件
```

## 快速开始

1. 克隆项目
```bash
git clone https://github.com/yourusername/QMT_Server.git
cd QMT_Server
```

2. 创建并激活虚拟环境
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

5. 运行应用
```bash
python run.py
```

## API 文档

详细的 API 文档请参考 `docs/` 目录。

## 测试

运行测试：
```bash
pytest
```

生成测试覆盖率报告：
```bash
pytest --cov=app tests/
```

## 许可证

[MIT](LICENSE) 