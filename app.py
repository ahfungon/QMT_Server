from flask import Flask, request, jsonify
from models import db, StockStrategy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

@app.before_first_request
def create_tables():
    """首次请求前创建所有数据表"""
    db.create_all()

@app.route(f'{Config.API_PREFIX}/strategies', methods=['POST'])
def create_strategy():
    """创建新的股票策略"""
    try:
        data = request.get_json()
        strategy = StockStrategy(
            stock_name=data['stock_name'],
            stock_code=data['stock_code'],
            action=data['action'],
            position_ratio=data['position_ratio'],
            price_min=data.get('price_min'),
            price_max=data.get('price_max'),
            take_profit_price=data.get('take_profit_price'),
            stop_loss_price=data.get('stop_loss_price'),
            other_conditions=data.get('other_conditions'),
            reason=data.get('reason')
        )
        db.session.add(strategy)
        db.session.commit()
        return jsonify({'message': '策略创建成功', 'data': strategy.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route(f'{Config.API_PREFIX}/strategies/<int:strategy_id>', methods=['PUT'])
def update_strategy(strategy_id):
    """更新现有的股票策略"""
    try:
        strategy = StockStrategy.query.get_or_404(strategy_id)
        data = request.get_json()
        
        for key, value in data.items():
            if hasattr(strategy, key):
                setattr(strategy, key, value)
        
        db.session.commit()
        return jsonify({'message': '策略更新成功', 'data': strategy.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

@app.route(f'{Config.API_PREFIX}/strategies', methods=['GET'])
def get_strategies():
    """获取所有股票策略或特定股票的策略"""
    stock_code = request.args.get('stock_code')
    is_active = request.args.get('is_active', 'true').lower() == 'true'
    
    query = StockStrategy.query.filter_by(is_active=is_active)
    
    if stock_code:
        query = query.filter_by(stock_code=stock_code)
    
    strategies = query.all()
    return jsonify({
        'message': '获取策略成功',
        'data': [strategy.to_dict() for strategy in strategies]
    })

@app.route(f'{Config.API_PREFIX}/strategies/<int:strategy_id>', methods=['DELETE'])
def delete_strategy(strategy_id):
    """删除（软删除）股票策略"""
    try:
        strategy = StockStrategy.query.get_or_404(strategy_id)
        strategy.is_active = False
        db.session.commit()
        return jsonify({'message': '策略已删除'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True) 