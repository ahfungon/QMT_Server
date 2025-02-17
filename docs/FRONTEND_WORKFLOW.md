# 策略管理前端工作流程文档

## 目录
1. [自然语言输入阶段](#1-自然语言输入阶段)
2. [策略解析阶段](#2-策略解析阶段)
3. [查重验证阶段](#3-查重验证阶段)
4. [策略确认阶段](#4-策略确认阶段)
5. [策略提交阶段](#5-策略提交阶段)
6. [完整流程示例](#6-完整流程示例)

## 1. 自然语言输入阶段

### 1.1 用户输入界面
```typescript
interface StrategyInput {
    strategyText: string;  // 自然语言策略描述
}
```
**示例输入：**
- "我想在比亚迪股票价格低于15元时买入10%仓位"
- "当比亚迪股价达到18元时卖出所有仓位"

### 1.2 前端输入验证
```typescript
function validateStrategyInput(text: string): boolean {
    // 1. 检查输入是否为空
    if (!text.trim()) {
        showError("策略描述不能为空喵~");
        return false;
    }
    
    // 2. 检查输入长度
    if (text.length > 200) {
        showError("策略描述不能超过200个字符喵~");
        return false;
    }
    
    return true;
}
```

## 2. 策略解析阶段

### 2.1 调用策略分析接口
```typescript
async function analyzeStrategy(text: string): Promise<StrategyAnalysisResult> {
    try {
        const response = await axios.post('/api/strategy/analyze', {
            strategy_text: text
        });
        
        if (response.data.code === 200) {
            return response.data.data;
        }
    } catch (error) {
        showError("策略解析失败，请检查输入是否正确喵~");
        throw error;
    }
}
```

### 2.2 解析结果展示
```typescript
interface StrategyAnalysisResult {
    stock_name: string;     // 股票名称
    stock_code: string;     // 股票代码
    action: 'buy' | 'sell'; // 操作类型
    price_min?: number;     // 最小价格
    price_max?: number;     // 最大价格
    position_ratio: number; // 仓位比例
    reason?: string;        // 操作理由
}
```

## 3. 查重验证阶段

### 3.1 调用查重接口
```typescript
async function checkDuplicate(strategy: StrategyAnalysisResult): Promise<DuplicateCheckResult> {
    try {
        const response = await axios.post('/api/strategy/check-duplicate', {
            stock_code: strategy.stock_code,    // 股票代码
            action: strategy.action,            // 操作类型（买/卖）
            is_active: true                     // 策略是否有效
        });
        
        return response.data.data;
    } catch (error) {
        showError("查重验证失败喵~");
        throw error;
    }
}
```

### 3.2 查重结果处理
```typescript
interface DuplicateCheckResult {
    has_duplicate: boolean;
    duplicate_strategies?: Array<{
        id: number;
        stock_name: string;
        stock_code: string;
        action: string;
        price_min: number;
        price_max: number;
        position_ratio: number;
        is_active: boolean;
        execution_status: string;
    }>;
}

function handleDuplicateCheck(result: DuplicateCheckResult): void {
    if (result.has_duplicate) {
        // 显示重复策略弹窗
        showDuplicateDialog({
            title: "发现重复策略喵~",
            content: "已存在相同股票的相似策略，是否要更新现有策略？",
            strategies: result.duplicate_strategies,
            onUpdate: () => handleStrategyUpdate(result.duplicate_strategies[0].id),
            onCreateNew: () => handleCreateNewStrategy()
        });
    } else {
        // 直接进入创建流程
        handleCreateNewStrategy();
    }
}
```

## 4. 策略确认阶段

### 4.1 策略表单展示
```typescript
interface StrategyForm {
    stock_name: string;
    stock_code: string;
    action: 'buy' | 'sell';
    position_ratio: number;
    price_min?: number;
    price_max?: number;
    take_profit_price?: number;  // 止盈价
    stop_loss_price?: number;    // 止损价
    other_conditions?: string;   // 其他条件
    reason?: string;            // 操作理由
}

function showStrategyConfirmDialog(strategy: StrategyAnalysisResult): void {
    const form = new StrategyForm({
        ...strategy,
        // 允许用户修改或补充信息
        take_profit_price: null,
        stop_loss_price: null
    });
    
    // 显示确认对话框
    showDialog({
        title: "请确认策略信息喵~",
        form: form,
        onConfirm: (formData) => handleStrategySubmit(formData),
        onCancel: () => handleCancel()
    });
}
```

## 5. 策略提交阶段

### 5.1 创建新策略
```typescript
async function handleCreateNewStrategy(formData: StrategyForm): Promise<void> {
    try {
        const response = await axios.post('/api/strategy/create', formData);
        
        if (response.data.code === 200) {
            showSuccess("策略创建成功喵~");
            refreshStrategyList();
        }
    } catch (error) {
        showError("策略创建失败喵~");
        throw error;
    }
}
```

### 5.2 更新现有策略
```typescript
async function handleStrategyUpdate(strategyId: number, formData: StrategyForm): Promise<void> {
    try {
        const response = await axios.put(`/api/strategy/${strategyId}`, formData);
        
        if (response.data.code === 200) {
            showSuccess("策略更新成功喵~");
            refreshStrategyList();
        }
    } catch (error) {
        showError("策略更新失败喵~");
        throw error;
    }
}
```

## 6. 完整流程示例

```typescript
async function handleStrategySubmission(strategyText: string): Promise<void> {
    try {
        // 1. 输入验证
        if (!validateStrategyInput(strategyText)) {
            return;
        }
        
        // 2. 策略解析
        const analysisResult = await analyzeStrategy(strategyText);
        
        // 3. 查重验证
        const duplicateResult = await checkDuplicate(analysisResult);
        
        if (duplicateResult.has_duplicate) {
            // 4a. 显示重复策略处理对话框
            showDuplicateDialog({
                strategies: duplicateResult.duplicate_strategies,
                onUpdate: async () => {
                    // 显示确认对话框，预填充现有策略数据
                    const existingStrategy = duplicateResult.duplicate_strategies[0];
                    const formData = await showStrategyConfirmDialog({
                        ...analysisResult,
                        ...existingStrategy
                    });
                    
                    // 更新策略
                    await handleStrategyUpdate(existingStrategy.id, formData);
                },
                onCreateNew: async () => {
                    // 4b. 显示新策略确认对话框
                    const formData = await showStrategyConfirmDialog(analysisResult);
                    
                    // 创建新策略
                    await handleCreateNewStrategy(formData);
                }
            });
        } else {
            // 4b. 直接显示新策略确认对话框
            const formData = await showStrategyConfirmDialog(analysisResult);
            
            // 5. 创建新策略
            await handleCreateNewStrategy(formData);
        }
        
    } catch (error) {
        handleError(error);
    }
}
```

## 注意事项

1. 所有的用户输入都需要进行验证
2. 查重逻辑需要考虑：
   - 股票代码
   - 操作类型（买/卖）
   - 价格区间重叠
   - 策略是否有效（is_active）
   - 执行状态
3. 错误处理需要友好提示
4. 成功操作后需要刷新策略列表
5. 表单数据需要进行类型检查和数值范围验证

## 开发建议

1. 使用 TypeScript 进行开发，提供更好的类型检查
2. 使用 Vue3 + Element Plus 构建界面
3. 使用 Axios 进行 HTTP 请求
4. 使用 Vuex/Pinia 管理状态
5. 使用 Vue Router 管理路由
6. 使用 ESLint + Prettier 规范代码风格 