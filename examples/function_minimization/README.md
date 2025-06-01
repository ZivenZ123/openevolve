# 函数最小化示例

这个示例演示了 OpenEvolve 如何从一个简单的实现开始, 发现复杂的优化算法.

## 问题描述

任务是最小化一个具有多个局部最小值的复杂非凸函数:

```python
f(x, y) = sin(x) * cos(y) + sin(x*y) + (x^2 + y^2)/20
```

全局最小值大约在(-1.704, 0.678)处, 值为-1.519.

## 开始使用

要运行此示例:

```bash
cd examples/function_minimization
python ../../openevolve-run.py initial_program.py evaluator.py --config config.yaml
```

## 算法演化

### 初始算法（随机搜索）

初始实现是一个简单的随机搜索, 在迭代之间没有记忆:

```python
def search_algorithm(iterations=1000, bounds=(-5, 5)):
    """
    一个简单的随机搜索算法, 经常陷入局部最小值.

    参数:
        iterations: 运行的迭代次数
        bounds: 搜索空间的边界 (min, max)

    返回:
        (best_x, best_y, best_value)的元组
    """
    # 用随机点初始化
    best_x = np.random.uniform(bounds[0], bounds[1])
    best_y = np.random.uniform(bounds[0], bounds[1])
    best_value = evaluate_function(best_x, best_y)

    for _ in range(iterations):
        # 简单随机搜索
        x = np.random.uniform(bounds[0], bounds[1])
        y = np.random.uniform(bounds[0], bounds[1])
        value = evaluate_function(x, y)

        if value < best_value:
            best_value = value
            best_x, best_y = x, y

    return best_x, best_y, best_value
```

### 演化后的算法（模拟退火）

运行 OpenEvolve 后, 它发现了一个采用完全不同方法的模拟退火算法:

```python
def search_algorithm(bounds=(-5, 5), iterations=2000, initial_temperature=100, cooling_rate=0.97, step_size_factor=0.2, step_size_increase_threshold=20):
    """
    用于函数最小化的模拟退火算法.

    参数:
        bounds: 搜索空间的边界 (min, max)
        iterations: 运行的迭代次数
        initial_temperature: 模拟退火过程的初始温度
        cooling_rate: 模拟退火过程的冷却率
        step_size_factor: 用范围缩放初始步长的因子
        step_size_increase_threshold: 增加步长前无改进的迭代次数

    返回:
        (best_x, best_y, best_value)的元组
    """
    # 初始化
    best_x = np.random.uniform(bounds[0], bounds[1])
    best_y = np.random.uniform(bounds[0], bounds[1])
    best_value = evaluate_function(best_x, best_y)

    current_x, current_y = best_x, best_y
    current_value = best_value
    temperature = initial_temperature
    step_size = (bounds[1] - bounds[0]) * step_size_factor  # 初始步长
    min_temperature = 1e-6 # 避免过早收敛
    no_improvement_count = 0 # 跟踪停滞的计数器

    for i in range(iterations):
        # 自适应步长和温度控制
        if i > iterations * 0.75:  # 在接近结束时减少步长
            step_size *= 0.5
        if no_improvement_count > step_size_increase_threshold: # 如果卡住就增加步长
            step_size *= 1.1
            no_improvement_count = 0 # 重置计数器

        step_size = min(step_size, (bounds[1] - bounds[0]) * 0.5) # 限制步长

        new_x = current_x + np.random.uniform(-step_size, step_size)
        new_y = current_y + np.random.uniform(-step_size, step_size)

        # 保持新点在边界内
        new_x = max(bounds[0], min(new_x, bounds[1]))
        new_y = max(bounds[0], min(new_y, bounds[1]))

        new_value = evaluate_function(new_x, new_y)

        if new_value < current_value:
            # 如果更好就接受移动
            current_x, current_y = new_x, new_y
            current_value = new_value
            no_improvement_count = 0  # 重置计数器

            if new_value < best_value:
                # 更新找到的最佳解
                best_x, best_y = new_x, new_y
                best_value = new_value
        else:
            # 以一定概率接受（模拟退火）
            probability = np.exp((current_value - new_value) / temperature)
            if np.random.rand() < probability:
                current_x, current_y = new_x, new_y
                current_value = new_value
                no_improvement_count = 0  # 重置计数器
            else:
                no_improvement_count += 1 # 如果没有改进就增加计数器

        temperature = max(temperature * cooling_rate, min_temperature) #冷却

    return best_x, best_y, best_value
```

## 关键改进

通过演化迭代, OpenEvolve 发现了几个关键的算法概念:

1. **通过温度进行探索**: 模拟退火使用`temperature`参数允许在搜索早期进行上坡移动, 帮助逃脱会困住简单方法的局部最小值.

   ```python
   probability = np.exp((current_value - new_value) / temperature)
   ```

2. **自适应步长**: 步长动态调整——随着搜索收敛而缩小, 如果进展停滞则扩大——从而获得更好的覆盖率和更快的收敛速度.

   ```python
   if i > iterations * 0.75:  # 在接近结束时减少步长
       step_size *= 0.5
   if no_improvement_count > step_size_increase_threshold: # 如果卡住就增加步长
       step_size *= 1.1
       no_improvement_count = 0 # 重置计数器
   ```

3. **有界移动**: 算法确保所有候选解都保持在可行域内, 避免浪费评估.

   ```python
   # 保持新点在边界内
   new_x = max(bounds[0], min(new_x, bounds[1]))
   new_y = max(bounds[0], min(new_y, bounds[1]))
   ```

4. **停滞处理**: 通过计算无改进的迭代次数, 算法在进展停滞时通过增强探索来响应.
   ```python
   if no_improvement_count > step_size_increase_threshold: # 如果卡住就增加步长
       step_size *= 1.1
       no_improvement_count = 0 # 重置计数器
   ```

## 结果

演化后的算法在找到更好解决方案方面显示出显著改进:

| 指标       | 值    |
| ---------- | ----- |
| 数值分数   | 0.990 |
| 距离分数   | 0.921 |
| 标准差分数 | 0.900 |
| 速度分数   | 0.466 |
| 可靠性分数 | 1.000 |
| 总体分数   | 0.984 |
| 综合分数   | 0.922 |

模拟退火算法:

- 获得更高质量的解（更接近全局最小值）
- 具有完美的可靠性（100%的完成运行成功率）
- 在性能和可靠性之间保持良好平衡

## 工作原理

这个示例演示了 OpenEvolve 的关键特性:

- **代码演化**: 只有演化块内的代码被修改
- **完整算法重新设计**: 系统将随机搜索转换为完全不同的算法
- **自动发现**: 系统在没有明确编程优化算法知识的情况下发现了模拟退火
- **函数重命名**: 系统甚至认识到算法应该有一个更具描述性的名称

## 下一步

尝试修改 config.yaml 文件来:

- 增加迭代次数
- 更改 LLM 模型配置
- 调整评估器设置以优先考虑不同指标
- 通过修改`evaluate_function()`尝试不同的目标函数
