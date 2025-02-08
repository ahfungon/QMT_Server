"""
应用入口模块

此模块是应用的启动入口
"""

import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    debug = os.getenv('FLASK_DEBUG', '0') == '1'
    port = int(os.getenv('FLASK_RUN_PORT', '5000'))  # 默认使用5000端口
    print("="*50)
    print("正在启动服务...")
    print(f"调试模式: {'开启' if debug else '关闭'}")
    print(f"服务端口: {port}")
    print(f"静态文件路径: {app.static_folder}")
    print(f"模板文件路径: {app.template_folder}")
    print("="*50)
    app.run(debug=debug, port=port) 