"""
接口测试模块

此模块包含所有API接口的测试用例
"""

import os
import sys
import json
import pytest
from datetime import datetime
from pathlib import Path
import logging

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from app import create_app
from app.models import db
from app.utils.logger import setup_logger

# 设置日志
logger = setup_logger('test_api')

app = create_app()

@pytest.fixture
def app():
    """创建测试应用"""
    os.environ['FLASK_CONFIG'] = 'testing'  # 确保使用测试配置
    app = create_app('testing')
    
    # 创建测试数据库表
    with app.app_context():
        db.drop_all()  # 先删除所有表
        db.create_all()  # 重新创建表
        
    yield app
    
    # 清理测试数据
    with app.app_context():
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """创建测试命令运行器"""
    return app.test_cli_runner()

def log_test_case(name: str, url: str, method: str, data: dict = None, expected: dict = None, response: dict = None):
    """记录测试用例信息"""
    logger.info("="*50)
    logger.info(f"测试用例: {name}")
    logger.info(f"请求URL: {url}")
    logger.info(f"请求方法: {method}")
    if data:
        logger.info(f"请求数据: {json.dumps(data, ensure_ascii=False, indent=2)}")
    if expected:
        logger.info(f"预期结果: {json.dumps(expected, ensure_ascii=False, indent=2)}")
    if response:
        logger.info(f"实际结果: {json.dumps(response, ensure_ascii=False, indent=2)}")
    logger.info("="*50)

class TestStrategyAPI:
    """策略相关接口测试"""
    
    def setup_method(self, method):
        """每个测试方法执行前清理数据库"""
        self.app = create_app()
        with self.app.app_context():
            db.drop_all()  # 先删除所有表
            db.create_all()  # 重新创建表
            db.session.commit()  # 提交事务

    def test_analyze_strategy(self, client):
        """测试策略分析接口"""
        url = '/api/v1/analyze_strategy'
        data = {
            "strategy_text": "我想买入贵州茅台，价格在1500到1600之间，止盈价1700，止损价1450，使用10%的仓位，原因是技术面向好，估值合理，其他条件是日线MACD金叉"
        }
        
        response = client.post(url, json=data)
        result = response.get_json()
        
        log_test_case("策略分析", url, "POST", data, None, result)
        assert response.status_code == 200
        assert result['code'] == 200
        assert 'data' in result
        assert result['data']['stock_name'] == "贵州茅台"
        assert result['data']['stock_code'] == "600519"
        
    def test_get_strategies_empty(self, client):
        """测试获取空策略列表"""
        url = '/api/v1/strategies'
        
        response = client.get(url)
        result = response.get_json()
        
        log_test_case("获取空策略列表", url, "GET")
        assert response.status_code == 200
        assert result['code'] == 200
        assert len(result['data']) == 0
        
    def test_create_and_get_strategy(self, client):
        """测试创建并获取策略"""
        # 1. 创建策略
        create_url = '/api/v1/strategies'
        create_data = {
            "stock_name": "贵州茅台",
            "stock_code": "600519",
            "action": "buy",
            "position_ratio": 0.1,
            "price_min": 1500,
            "price_max": 1600,
            "take_profit_price": 1700,
            "stop_loss_price": 1450,
            "other_conditions": "日线MACD金叉",
            "reason": "技术面向好，估值合理"
        }
        
        create_response = client.post(create_url, json=create_data)
        create_result = create_response.get_json()
        
        log_test_case("创建策略", create_url, "POST", create_data, None, create_result)
        assert create_response.status_code == 200
        assert create_result['code'] == 200
        assert 'data' in create_result
        strategy_id = create_result['data']['id']
        
        # 2. 获取策略列表
        get_url = '/api/v1/strategies'
        get_response = client.get(get_url)
        get_result = get_response.get_json()
        
        log_test_case("获取策略列表", get_url, "GET")
        assert get_response.status_code == 200
        assert get_result['code'] == 200
        assert len(get_result['data']) == 1
        assert get_result['data'][0]['id'] == strategy_id
        
        return strategy_id
        
    def test_update_strategy(self, client, strategy_id=None):
        """测试更新策略"""
        if strategy_id is None:
            # 1. 创建策略
            create_url = '/api/v1/strategies'
            create_data = {
                "stock_name": "贵州茅台",
                "stock_code": "600519",
                "action": "buy",
                "position_ratio": 0.1,
                "price_min": 1500,
                "price_max": 1600,
                "take_profit_price": 1700,
                "stop_loss_price": 1450,
                "other_conditions": "日线MACD金叉",
                "reason": "技术面向好，估值合理"
            }

            create_response = client.post(create_url, json=create_data)
            create_result = create_response.get_json()

            log_test_case("创建策略", create_url, "POST", create_data, None, create_result)
            assert create_response.status_code == 200
            assert create_result['code'] == 200
            assert 'data' in create_result
            strategy_id = create_result['data']['id']

        # 2. 更新策略
        update_url = f'/api/v1/strategies/{strategy_id}'
        update_data = {
            "stock_name": "贵州茅台",
            "stock_code": "600519",
            "action": "buy",
            "position_ratio": 0.2,  # 修改仓位比例
            "price_min": 1550,  # 修改最低价
            "price_max": 1650,  # 修改最高价
            "take_profit_price": 1750,  # 修改止盈价
            "stop_loss_price": 1500,  # 修改止损价
            "other_conditions": "日线MACD金叉，KDJ金叉",  # 修改其他条件
            "reason": "技术面向好，估值合理，市场情绪乐观"  # 修改原因
        }

        update_response = client.put(update_url, json=update_data)
        update_result = update_response.get_json()

        log_test_case("更新策略", update_url, "PUT", update_data, None, update_result)
        assert update_response.status_code == 200
        assert update_result['code'] == 200
        assert 'data' in update_result
        assert update_result['data']['position_ratio'] == 0.2
        assert update_result['data']['price_min'] == 1550
        assert update_result['data']['price_max'] == 1650
        assert update_result['data']['take_profit_price'] == 1750
        assert update_result['data']['stop_loss_price'] == 1500
        assert update_result['data']['other_conditions'] == "日线MACD金叉，KDJ金叉"
        assert update_result['data']['reason'] == "技术面向好，估值合理，市场情绪乐观"

        return strategy_id
        
    def test_deactivate_strategy(self, client):
        """测试设置策略失效"""
        # 1. 先创建策略
        strategy_id = self.test_create_and_get_strategy(client)
        
        # 2. 设置策略失效
        url = f'/api/v1/strategies/{strategy_id}/deactivate'
        
        response = client.post(url)
        result = response.get_json()
        
        log_test_case("设置策略失效", url, "POST")
        assert response.status_code == 200
        assert result['code'] == 200
        assert result['data']['is_active'] == False
        
        # 3. 再次激活策略
        url = f'/api/v1/strategies/{strategy_id}/activate'
        
        response = client.post(url)
        result = response.get_json()
        
        log_test_case("重新激活策略", url, "POST")
        assert response.status_code == 200
        assert result['code'] == 200
        assert result['data']['is_active'] == True

class TestExecutionAPI:
    """执行记录相关接口测试"""
    
    def setup_method(self, method):
        """每个测试方法执行前清理数据库"""
        self.app = create_app()
        with self.app.app_context():
            db.drop_all()  # 先删除所有表
            db.create_all()  # 重新创建表
            db.session.commit()  # 提交事务

    def test_create_execution(self, client):
        """测试创建执行记录"""
        # 1. 先创建策略
        strategy_id = TestStrategyAPI().test_create_and_get_strategy(client)
        
        # 2. 创建执行记录
        url = '/api/v1/executions'
        data = {
            "strategy_id": strategy_id,
            "stock_code": "600519",
            "stock_name": "贵州茅台",
            "action": "buy",
            "execution_price": 1580.5,
            "volume": 100,
            "strategy_status": "partial",
            "remarks": "按计划执行"
        }
        
        response = client.post(url, json=data)
        result = response.get_json()
        
        log_test_case("创建执行记录", url, "POST", data, None, result)
        assert response.status_code == 200
        assert result['code'] == 200
        assert result['data']['strategy_id'] == strategy_id
        assert result['data']['execution_price'] == 1580.5
        assert result['data']['volume'] == 100
        
        return result['data']['id']
        
    def test_get_executions(self, client):
        """测试获取执行记录列表"""
        # 1. 先创建执行记录
        execution_id = self.test_create_execution(client)
        
        # 2. 获取执行记录列表
        url = '/api/v1/executions'
        
        response = client.get(url)
        result = response.get_json()
        
        log_test_case("获取执行记录列表", url, "GET")
        assert response.status_code == 200
        assert result['code'] == 200
        assert len(result['data']) > 0
        assert result['data'][0]['id'] == execution_id

class TestPositionAPI:
    """持仓相关接口测试"""
    
    def setup_method(self, method):
        """每个测试方法执行前清理数据库"""
        self.app = create_app()
        with self.app.app_context():
            db.drop_all()  # 先删除所有表
            db.create_all()  # 重新创建表
            db.session.commit()  # 提交事务

    def test_position_workflow(self, client):
        """测试完整的持仓工作流程"""
        # 1. 创建策略并执行，这会创建持仓
        execution_id = TestExecutionAPI().test_create_execution(client)
        
        # 2. 获取所有持仓
        url = '/api/v1/positions'
        response = client.get(url)
        result = response.get_json()
        
        log_test_case("获取所有持仓", url, "GET")
        assert response.status_code == 200
        assert result['code'] == 200
        assert len(result['data']) > 0
        
        # 3. 获取单个持仓
        url = '/api/v1/positions/600519'
        response = client.get(url)
        result = response.get_json()
        
        log_test_case("获取单个持仓", url, "GET")
        assert response.status_code == 200
        assert result['code'] == 200
        assert result['data']['stock_code'] == "600519"
        
        # 4. 更新市值
        url = '/api/v1/positions/600519/market_value'
        data = {
            "latest_price": 1600.0
        }
        
        response = client.put(url, json=data)
        result = response.get_json()
        
        log_test_case("更新市值", url, "PUT", data, None, result)
        assert response.status_code == 200
        assert result['code'] == 200
        assert result['data']['latest_price'] == 1600.0

def test_complete_workflow(client):
    """测试完整的业务流程"""
    logger.info("开始测试完整业务流程...")
    
    # 1. 策略相关测试
    strategy_api = TestStrategyAPI()
    strategy_api.setup_method(None)  # 先清理数据库
    strategy_api.test_analyze_strategy(client)
    strategy_api.test_get_strategies_empty(client)
    strategy_id = strategy_api.test_create_and_get_strategy(client)
    strategy_api.test_update_strategy(client, strategy_id)
    strategy_api.test_deactivate_strategy(client)
    
    # 2. 执行记录相关测试
    execution_api = TestExecutionAPI()
    execution_api.setup_method(None)  # 先清理数据库
    execution_id = execution_api.test_create_execution(client)
    execution_api.test_get_executions(client)
    
    # 3. 持仓相关测试
    position_api = TestPositionAPI()
    position_api.setup_method(None)  # 先清理数据库
    position_api.test_position_workflow(client)
    
    logger.info("完整业务流程测试完成！")

if __name__ == '__main__':
    pytest.main(['-v', __file__])
