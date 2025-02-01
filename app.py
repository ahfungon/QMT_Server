from flask import Flask, request, jsonify, render_template
from models import db, StockStrategy
from ai_processor import AIStrategyProcessor
import os
from dotenv import load_dotenv
import json
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('api.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 配置数据库
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///stock_strategy.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.ensure_ascii = False  # 确保JSON响应中的中文正常显示

# 初始化数据库
db.init_app(app)
with app.app_context():
    db.create_all()

# 创建AI处理器实例
ai_processor = AIStrategyProcessor()

def log_request_info(request):
    """记录请求信息"""
    logger.info("="*50)
    logger.info(f"请求时间: {datetime.now()}")
    logger.info(f"请求路径: {request.path}")
    logger.info(f"请求方法: {request.method}")
    logger.info(f"请求头: {dict(request.headers)}")
    if request.is_json:
        logger.info(f"请求体: {json.dumps(request.get_json(), ensure_ascii=False, indent=2)}")
    logger.info("-"*50)

def log_response_info(response_data):
    """记录响应信息"""
    logger.info(f"响应数据: {json.dumps(response_data, ensure_ascii=False, indent=2)}")
    logger.info("="*50)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/analyze_strategy', methods=['POST'])
def analyze_strategy():
    """AI分析策略"""
    try:
        log_request_info(request)
        
        data = request.get_json()
        strategy_text = data.get('strategy_text', '')
        
        logger.info(f"开始AI分析，输入文本: {strategy_text}")
        result = ai_processor.process_strategy(strategy_text)
        logger.info(f"AI分析完成")
        
        response_data = {
            'code': 200,
            'message': 'success',
            'data': result
        }
        log_response_info(response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            'code': 400,
            'message': str(e),
            'data': None
        }
        logger.error(f"处理失败: {str(e)}", exc_info=True)
        log_response_info(error_response)
        return jsonify(error_response)

@app.route('/api/v1/strategies', methods=['GET'])
def get_strategies():
    """获取策略列表"""
    try:
        log_request_info(request)
        
        strategies = StockStrategy.query.all()
        result = [strategy.to_dict() for strategy in strategies]
        
        response_data = {
            'code': 200,
            'message': 'success',
            'data': result
        }
        log_response_info(response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            'code': 400,
            'message': str(e),
            'data': None
        }
        logger.error(f"获取策略列表失败: {str(e)}", exc_info=True)
        log_response_info(error_response)
        return jsonify(error_response)

@app.route('/api/v1/strategies', methods=['POST'])
def create_strategy():
    """创建策略"""
    try:
        log_request_info(request)
        
        data = request.get_json()
        strategy = StockStrategy(**data)
        db.session.add(strategy)
        db.session.commit()
        
        response_data = {
            'code': 200,
            'message': 'success',
            'data': strategy.to_dict()
        }
        log_response_info(response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            'code': 400,
            'message': str(e),
            'data': None
        }
        logger.error(f"创建策略失败: {str(e)}", exc_info=True)
        log_response_info(error_response)
        return jsonify(error_response)

@app.route('/api/v1/strategies/<int:id>', methods=['PUT'])
def update_strategy(id):
    """更新策略"""
    try:
        log_request_info(request)
        
        strategy = StockStrategy.query.get_or_404(id)
        data = request.get_json()
        for key, value in data.items():
            setattr(strategy, key, value)
        db.session.commit()
        
        response_data = {
            'code': 200,
            'message': 'success',
            'data': strategy.to_dict()
        }
        log_response_info(response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            'code': 400,
            'message': str(e),
            'data': None
        }
        logger.error(f"更新策略失败: {str(e)}", exc_info=True)
        log_response_info(error_response)
        return jsonify(error_response)

@app.route('/api/v1/strategies/<int:id>', methods=['DELETE'])
def delete_strategy(id):
    """删除策略"""
    try:
        log_request_info(request)
        
        strategy = StockStrategy.query.get_or_404(id)
        db.session.delete(strategy)
        db.session.commit()
        
        response_data = {
            'code': 200,
            'message': 'success',
            'data': None
        }
        log_response_info(response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            'code': 400,
            'message': str(e),
            'data': None
        }
        logger.error(f"删除策略失败: {str(e)}", exc_info=True)
        log_response_info(error_response)
        return jsonify(error_response)

if __name__ == '__main__':
    app.run(debug=True) 