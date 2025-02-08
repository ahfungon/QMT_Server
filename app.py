"""
应用入口模块

此模块是应用的启动入口
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True) 