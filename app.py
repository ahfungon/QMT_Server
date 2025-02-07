from flask import Flask, request, jsonify, render_template
from models import db, StockStrategy
from ai_robot import create_ai_processor
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
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@"
    f"{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.ensure_ascii = False  # 确保JSON响应中的中文正常显示

# 初始化数据库
db.init_app(app)
with app.app_context():
    db.create_all()

logger.info("="*50)
logger.info("正在启动服务...")

# 创建AI处理器
ai_processor = create_ai_processor()

logger.info("服务启动完成")
logger.info("="*50)

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
    # 如果是获取列表的接口，只记录数量
    if isinstance(response_data.get('data'), list):
        log_data = {
            'code': response_data['code'],
            'message': response_data['message'],
            'data_count': len(response_data['data'])
        }
        logger.info(f"响应数据: 状态码={log_data['code']}, 消息={log_data['message']}, 数据条数={log_data['data_count']}")
    else:
        # 其他接口记录完整信息，但不包含具体数据
        log_data = {
            'code': response_data['code'],
            'message': response_data['message'],
            'has_data': response_data.get('data') is not None
        }
        logger.info(f"响应数据: {json.dumps(log_data, ensure_ascii=False)}")
    logger.info("="*50)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/v1/analyze_strategy', methods=['POST'])
def analyze_strategy():
    """分析策略接口"""
    try:
        log_request_info(request)
        
        data = request.get_json()
        if not data or 'strategy_text' not in data:
            return jsonify({
                'code': 400,
                'message': '缺少策略文本',
                'data': None
            }), 400

        strategy_text = data['strategy_text']
        
        # 处理策略
        result = ai_processor.process_strategy(strategy_text)
        
        # 如果返回错误信息，直接返回
        if 'error' in result:
            return jsonify({
                'code': 400,
                'message': result['error'],
                'data': None
            }), 400
            
        response_data = {
            'code': 200,
            'message': '策略分析成功',
            'data': result
        }
        log_response_info(response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            'code': 500,
            'message': f'策略分析失败: {str(e)}',
            'data': None
        }
        logger.error(f"策略分析失败: {str(e)}", exc_info=True)
        log_response_info(error_response)
        return jsonify(error_response), 500

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

@app.route('/api/v1/strategies/check', methods=['POST'])
def check_strategy():
    """检查策略是否存在"""
    try:
        log_request_info(request)
        
        data = request.get_json()
        if not all(k in data for k in ['stock_name', 'stock_code', 'action']):
            return jsonify({
                'code': 400,
                'message': '缺少必要参数',
                'data': None
            }), 400

        # 查询有效的策略
        strategy = StockStrategy.query.filter_by(
            stock_name=data['stock_name'],
            stock_code=data['stock_code'],
            action=data['action'],
            is_active=True
        ).first()

        response_data = {
            'code': 200,
            'message': 'success',
            'data': strategy.to_dict() if strategy else None
        }
        log_response_info(response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            'code': 500,
            'message': f'检查策略失败: {str(e)}',
            'data': None
        }
        logger.error(f"检查策略失败: {str(e)}", exc_info=True)
        log_response_info(error_response)
        return jsonify(error_response), 500

@app.route('/api/v1/strategies/update', methods=['POST'])
def update_strategy_by_key():
    """根据关键字段更新策略"""
    try:
        log_request_info(request)
        
        data = request.get_json()
        if not all(k in data for k in ['stock_name', 'stock_code', 'action']):
            return jsonify({
                'code': 400,
                'message': '缺少必要参数',
                'data': None
            }), 400

        # 查询有效的策略
        strategy = StockStrategy.query.filter_by(
            stock_name=data['stock_name'],
            stock_code=data['stock_code'],
            action=data['action'],
            is_active=True
        ).first()

        if not strategy:
            return jsonify({
                'code': 404,
                'message': '未找到匹配的策略',
                'data': None
            }), 404

        # 更新策略字段
        has_updates = False
        update_fields = [
            'position_ratio', 'price_min', 'price_max',
            'take_profit_price', 'stop_loss_price',
            'other_conditions', 'reason'
        ]
        
        for field in update_fields:
            if field in data and getattr(strategy, field) != data[field]:
                setattr(strategy, field, data[field])
                has_updates = True

        if has_updates:
            db.session.commit()
            response_data = {
                'code': 200,
                'message': '策略更新成功',
                'data': strategy.to_dict()
            }
        else:
            response_data = {
                'code': 200,
                'message': '策略无需更新',
                'data': strategy.to_dict()
            }
            
        log_response_info(response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            'code': 500,
            'message': f'更新策略失败: {str(e)}',
            'data': None
        }
        logger.error(f"更新策略失败: {str(e)}", exc_info=True)
        log_response_info(error_response)
        return jsonify(error_response), 500

@app.route('/api/v1/strategies/<int:id>/deactivate', methods=['POST'])
def deactivate_strategy(id):
    """软删除策略（设置为失效）"""
    try:
        log_request_info(request)
        
        strategy = StockStrategy.query.get_or_404(id)
        strategy.is_active = False
        db.session.commit()
        
        response_data = {
            'code': 200,
            'message': '策略已设置为失效',
            'data': strategy.to_dict()
        }
        log_response_info(response_data)
        return jsonify(response_data)
        
    except Exception as e:
        error_response = {
            'code': 500,
            'message': f'设置策略失效失败: {str(e)}',
            'data': None
        }
        logger.error(f"设置策略失效失败: {str(e)}", exc_info=True)
        log_response_info(error_response)
        return jsonify(error_response), 500

if __name__ == '__main__':
    app.run(debug=True) 