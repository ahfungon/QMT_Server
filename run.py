"""
应用入口模块

此模块是应用的启动入口
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, port=5000) 