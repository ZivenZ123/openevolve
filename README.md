# OpenEvolve

Google DeepMind 论文"AlphaEvolve: A coding agent for scientific and algorithmic discovery" (2025) 中描述的 AlphaEvolve 系统的开源实现.

![OpenEvolve Logo](openevolve-logo.png)

## 概述

OpenEvolve 是一个进化编程代理, 它使用大型语言模型通过迭代过程来优化代码. 它编排了一个基于 LLM 的代码生成、评估和选择的流水线, 以持续改进各种任务的程序.

主要特性:

- 进化整个代码文件, 而不仅仅是单个函数
- 支持多种编程语言
- 支持任何 LLM 的 OpenAI 兼容 API
- 多目标优化
- 灵活的提示工程
- 分布式评估

## 工作原理

OpenEvolve 遵循进化方法, 包含以下组件:

![OpenEvolve Architecture](openevolve-architecture.png)

1. **提示采样器**: 创建包含过去程序、其分数和问题描述的上下文丰富的提示
2. **LLM 集群**: 通过语言模型集群生成代码修改
3. **评估器池**: 测试生成的程序并分配分数
4. **程序数据库**: 存储程序及其评估指标, 指导未来的进化

控制器在异步流水线中编排这些组件之间的交互, 最大化吞吐量以评估尽可能多的候选解决方案.

## 快速开始

### 安装

本地安装使用:

```bash
git clone https://github.com/codelion/openevolve.git
cd openevolve
pip install -e .
```

### 快速开始

我们使用 OpenAI SDK, 因此您可以使用任何支持 OpenAI 兼容 API 的 LLM 或提供商. 只需设置`OPENAI_API_KEY`环境变量, 如果您使用 OpenAI 以外的提供商, 请更新 config.yaml 中的`api_base`. 对于本地模型, 您可以使用推理服务器如[optillm](https://github.com/codelion/optillm).

```python
from openevolve import OpenEvolve

# 初始化系统
evolve = OpenEvolve(
    initial_program_path="path/to/initial_program.py",
    evaluation_file="path/to/evaluator.py",
    config_path="path/to/config.yaml"
)

# Run the evolution
best_program = await evolve.run(iterations=1000)
print(f"最佳程序指标:")
for name, value in best_program.metrics.items():
    print(f"  {name}: {value:.4f}")
```

### 命令行使用

OpenEvolve 也可以从命令行运行:

```bash
python openevolve-run.py path/to/initial_program.py path/to/evaluator.py --config path/to/config.yaml --iterations 1000
```

### 从检查点恢复

OpenEvolve 会按照`checkpoint_interval`配置参数指定的间隔自动保存检查点(默认为 10 次迭代). 您可以从保存的检查点恢复进化运行:

```bash
python openevolve-run.py path/to/initial_program.py path/to/evaluator.py \
  --config path/to/config.yaml \
  --checkpoint path/to/checkpoint_directory \
  --iterations 50
```

从检查点恢复时:

- 系统加载所有先前进化的程序及其指标
- 检查点编号从停止的地方继续(例如, 如果从 checkpoint_50 加载, 下一个检查点将是 checkpoint_60)
- 所有进化状态都会保留(最佳程序、特征映射、档案等)
- 每个检查点目录都包含当时最佳程序的副本

检查点工作流示例:

```bash
# 运行50次迭代(在第10、20、30、40、50次迭代创建检查点)
python openevolve-run.py examples/function_minimization/initial_program.py \
  examples/function_minimization/evaluator.py \
  --iterations 50

# 从检查点50恢复再运行50次迭代(在第60、70、80、90、100次迭代创建检查点)
python openevolve-run.py examples/function_minimization/initial_program.py \
  examples/function_minimization/evaluator.py \
  --checkpoint examples/function_minimization/openevolve_output/checkpoints/checkpoint_50 \
  --iterations 50
```

### 跨检查点比较结果

每个检查点目录都包含到该点为止找到的最佳程序, 这使得比较随时间变化的解决方案变得容易:

```
checkpoints/
  checkpoint_10/
    best_program.py         # 第10次迭代的最佳程序
    best_program_info.json  # 指标和详细信息
    programs/               # 到目前为止评估的所有程序
    metadata.json           # 数据库状态
  checkpoint_20/
    best_program.py         # 第20次迭代的最佳程序
    ...
```

您可以通过检查不同检查点的最佳程序来比较解决方案的进化:

```bash
# 比较不同检查点的最佳程序
diff -u checkpoints/checkpoint_10/best_program.py checkpoints/checkpoint_20/best_program.py

# 比较指标
cat checkpoints/checkpoint_*/best_program_info.json | grep -A 10 metrics
```

### Docker

您也可以通过 Docker 安装和执行:

```bash
docker build -t openevolve .
docker run --rm -v $(pwd):/app openevolve examples/function_minimization/initial_program.py examples/function_minimization/evaluator.py --config examples/function_minimization/config.yaml --iterations 1000
```

## 配置

OpenEvolve 是高度可配置的. 您可以在 YAML 文件中指定配置选项:

```yaml
# 示例配置
max_iterations: 1000
llm:
  primary_model: "gemini-2.0-flash-lite"
  secondary_model: "gemini-2.0-flash"
  temperature: 0.7
database:
  population_size: 500
  num_islands: 5
```

示例配置文件在`configs/`目录中可用:

- `default_config.yaml`: 包含所有可用选项的综合配置

有关选项的完整列表, 请参阅[配置指南](configs/default_config.yaml).

## 示例

请参阅`examples/`目录, 了解在各种问题上使用 OpenEvolve 的完整示例:

### 符号回归

一个全面的示例, 演示了 OpenEvolve 在使用 LLM-SRBench 基准的符号回归任务中的应用. 此示例展示了 OpenEvolve 如何将简单的数学表达式(如线性模型)进化为准确拟合科学数据集的复杂符号公式.

[探索符号回归示例](examples/symbolic_regression/)

主要特性:

- 从基准任务自动生成初始程序
- 从简单线性模型进化为复杂数学表达式
- 在物理、化学、生物和材料科学数据集上评估
- 与最先进的符号回归方法相比具有竞争力的结果

### 圆圈装箱

我们对 AlphaEvolve 论文中圆圈装箱问题的实现. 对于 n=26 的情况, 即需要在单位正方形中装入 26 个圆圈, 我们也获得了最先进的结果.

[探索圆圈装箱示例](examples/circle_packing/)

我们成功复制了 AlphaEvolve 论文的结果, 下面是 OpenEvolve 在 800 次迭代后找到的装箱方案

![alpha-evolve-replication](https://github.com/user-attachments/assets/00100f9e-2ac3-445b-9266-0398b7174193)

这正是 AlphaEvolve 在他们的论文中报告的装箱方案(图 14):

![alpha-evolve-results](https://github.com/user-attachments/assets/0c9affa5-053d-404e-bb2d-11479ab248c9)

### 函数最小化

一个示例, 展示了 OpenEvolve 如何将简单的随机搜索算法转换为复杂的模拟退火方法.

[探索函数最小化示例](examples/function_minimization/)

## 准备您自己的问题

要在您自己的问题上使用 OpenEvolve:

1. **标记代码段**以使用`# EVOLVE-BLOCK-START`和`# EVOLVE-BLOCK-END`注释进行进化
2. **创建评估函数**返回指标字典
3. **配置 OpenEvolve**使用适当的参数
4. **运行进化**过程

## 引用

如果您在研究中使用 OpenEvolve, 请引用:

```
@software{openevolve,
  title = {OpenEvolve: Open-source implementation of AlphaEvolve},
  author = {Asankhaya Sharma},
  year = {2025},
  publisher = {GitHub},
  url = {https://github.com/codelion/openevolve}
}
```
