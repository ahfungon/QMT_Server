"""
主页路由模块

此模块定义了主页相关的路由
"""

from flask import Blueprint, render_template

# 创建蓝图
home_bp = Blueprint('home', __name__)

@home_bp.route('/')
def index():
    """主页"""
    return render_template('index.html') 