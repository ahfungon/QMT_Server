# 股票策略管理系统 API 文档

## 基础信息
- 基础URL：`http://localhost:5000`
- 响应格式：JSON
- 编码方式：UTF-8

## 1. AI 策略分析接口

### 请求信息
- 接口路径：`/api/v1/analyze_strategy`
- 请求方法：POST
- Content-Type：`application/json`

### 请求参数
```json
{
    "strategy_text": "策略文本内容"
}
```

### 响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "stock_name": "股票名称",
        "stock_code": "股票代码（6位数字）",
        "action": "buy或sell",
        "position_ratio": 0.5,  // 0-1之间的小数
        "price_min": 10.5,      // 可选
        "price_max": 11.0,      // 可选
        "take_profit_price": 12.0,  // 可选
        "stop_loss_price": 9.5,     // 可选
        "other_conditions": "其他交易条件",  // 可选
        "reason": "操作理由"    // 可选
    }
}
```

### 错误响应
```json
{
    "code": 200,
    "message": "success",
    "data": {
        "error": "与股票交易无关，暂不处理"
    }
}
```

### 示例
```python
import requests

url = "http://localhost:5000/api/v1/analyze_strategy"
data = {
    "strategy_text": "以30元买入平安银行，仓位30%"
}

response = requests.post(url, json=data)
print(response.json())
```

## 2. 获取策略列表

### 请求信息
- 接口路径：`/api/v1/strategies`
- 请求方法：GET

### 响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": [
        {
            "id": 1,
            "stock_name": "股票名称",
            "stock_code": "股票代码",
            "action": "buy或sell",
            "position_ratio": 0.5,
            "price_min": 10.5,
            "price_max": 11.0,
            "take_profit_price": 12.0,
            "stop_loss_price": 9.5,
            "other_conditions": "其他交易条件",
            "reason": "操作理由"
        }
    ]
}
```

## 3. 创建策略

### 请求信息
- 接口路径：`/api/v1/strategies`
- 请求方法：POST
- Content-Type：`application/json`

### 请求参数
```json
{
    "stock_name": "股票名称",
    "stock_code": "股票代码（6位数字）",
    "action": "buy或sell",
    "position_ratio": 0.5,
    "price_min": 10.5,      // 可选
    "price_max": 11.0,      // 可选
    "take_profit_price": 12.0,  // 可选
    "stop_loss_price": 9.5,     // 可选
    "other_conditions": "其他交易条件",  // 可选
    "reason": "操作理由"    // 可选
}
```

## 4. 更新策略

### 请求信息
- 接口路径：`/api/v1/strategies/{id}`
- 请求方法：PUT
- Content-Type：`application/json`

### 请求参数
```json
{
    "stock_name": "股票名称",
    "stock_code": "股票代码",
    "action": "buy或sell",
    "position_ratio": 0.5,
    "price_min": 10.5,
    "price_max": 11.0,
    "take_profit_price": 12.0,
    "stop_loss_price": 9.5,
    "other_conditions": "其他交易条件",
    "reason": "操作理由"
}
```

## 5. 删除策略

### 请求信息
- 接口路径：`/api/v1/strategies/{id}`
- 请求方法：DELETE

### 响应格式
```json
{
    "code": 200,
    "message": "success",
    "data": null
}
```

## 注意事项

1. 字段说明：
   - `stock_name`：必填，字符串类型
   - `stock_code`：必填，6位数字字符串
   - `action`：必填，只能是 "buy" 或 "sell"
   - `position_ratio`：必填，0到1之间的小数
   - 其他字段为可选

2. 错误处理：
   - 所有接口在发生错误时会返回统一格式的错误信息
   ```json
   {
       "code": 400,
       "message": "错误信息",
       "data": null
   }
   ```

## Python SDK 示例

```python
import requests

class StockStrategyAPI:
    def __init__(self, base_url="http://localhost:5000"):
        self.base_url = base_url

    def analyze_strategy(self, strategy_text):
        """AI分析策略文本"""
        url = f"{self.base_url}/api/v1/analyze_strategy"
        data = {"strategy_text": strategy_text}
        return requests.post(url, json=data).json()

    def get_strategies(self):
        """获取策略列表"""
        url = f"{self.base_url}/api/v1/strategies"
        return requests.get(url).json()

    def create_strategy(self, strategy_data):
        """创建新策略"""
        url = f"{self.base_url}/api/v1/strategies"
        return requests.post(url, json=strategy_data).json()

    def update_strategy(self, strategy_id, strategy_data):
        """更新策略"""
        url = f"{self.base_url}/api/v1/strategies/{strategy_id}"
        return requests.put(url, json=strategy_data).json()

    def delete_strategy(self, strategy_id):
        """删除策略"""
        url = f"{self.base_url}/api/v1/strategies/{strategy_id}"
        return requests.delete(url).json()

# 使用示例
if __name__ == "__main__":
    api = StockStrategyAPI()

    # AI分析策略
    result = api.analyze_strategy("以30元买入平安银行，仓位30%")
    print("AI分析结果:", result)

    # 获取策略列表
    strategies = api.get_strategies()
    print("策略列表:", strategies)

    # 创建策略
    new_strategy = {
        "stock_name": "平安银行",
        "stock_code": "000001",
        "action": "buy",
        "position_ratio": 0.3,
        "price_min": 30.0,
        "price_max": 31.0,
        "take_profit_price": 33.0,
        "stop_loss_price": 29.0,
        "other_conditions": "日线MACD金叉",
        "reason": "技术面看好"
    }
    create_result = api.create_strategy(new_strategy)
    print("创建策略结果:", create_result)
``` 