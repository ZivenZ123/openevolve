# 贡献 OpenEvolve

感谢您对贡献 OpenEvolve 感兴趣! 本文档提供了贡献项目的指南和说明.

## 入门

1. Fork 仓库
2. 克隆您的 fork: `git clone https://github.com/你的github用户名/openevolve.git`
3. 设置开发环境 (见下方详细说明)
4. 运行测试以确保一切正常: `python -m unittest discover tests`

## 开发环境设置

我们推荐使用 **uv** 进行现代化的 Python 项目管理. uv 提供了更快的包管理和更好的依赖解析.

### 方法一: 使用 uv 原生命令 (强烈推荐)

这是最现代化和高效的方式:

```bash
# 安装 uv (如果尚未安装)
# macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh
# Windows: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 进入项目目录
cd openevolve

# 同步项目环境 (自动安装依赖并以可编辑模式安装项目)
uv sync

# 激活虚拟环境
source .venv/bin/activate  # 在 Windows 上: .venv\Scripts\activate
```

**`uv sync` 的作用:**

- 🚀 自动创建虚拟环境
- 📦 安装所有项目依赖
- ✏️ **自动以可编辑模式安装当前项目**
- 🔒 确保环境与 `uv.lock` 保持一致

### 方法二: 使用 uv pip 接口 (兼容 pip)

如果您更熟悉 pip 的工作方式:

```bash
# 以开发模式安装包及其开发依赖
uv pip install -e ".[dev]"
```

### 方法三: 使用传统 pip

我们仍然支持传统的 pip 方式:

```bash
python -m venv env
source env/bin/activate  # 在 Windows 上: env\Scripts\activate
pip install -e ".[dev]"
```

## 项目配置说明

为了确保 `uv sync` 能够正确以可编辑模式安装项目, 我们的 `pyproject.toml` 包含了必要的构建系统配置:

```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"
```

## 代码风格

我们遵循 [Black](https://black.readthedocs.io/) 代码风格. 请在提交 pull request 前格式化您的代码:

```bash
black openevolve tests examples
```

## Pull Request 流程

1. 为您的功能或 bug 修复创建一个新分支: `git checkout -b feature/your-feature-name`
2. 进行您的修改
3. 为您的修改添加测试
4. 运行测试以确保一切通过: `python -m unittest discover tests`
5. 提交您的修改: `git commit -m "Add your descriptive commit message"`
6. Push 到您的 fork: `git push origin feature/your-feature-name`
7. 提交 pull request 到主仓库

## 添加示例

我们鼓励添加新的示例来展示 OpenEvolve 的功能. 要添加新示例:

1. 在 `examples` 文件夹中创建一个新目录
2. 包含所有必要的文件 (初始程序, 评估代码等)
3. 添加一个 README.md 说明示例
4. 确保示例可以以最少的设置运行

## 报告问题

报告问题时, 请包括:

1. 问题的清晰描述
2. 重现步骤
3. 预期行为
4. 实际行为
5. 环境详情 (操作系统, Python 版本等)

## 功能请求

欢迎功能请求. 请提供:

1. 功能的清晰描述
2. 添加此功能的动机
3. 可能的实现想法 (如果有)

## 行为准则

在为项目做贡献时, 请尊重和体谅他人. 我们的目标是为所有贡献者创造一个受欢迎和包容的环境.
