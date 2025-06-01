# EVOLVE-BLOCK-START
"""OpenEvolve的函数最小化示例"""
import numpy as np


def search_algorithm(
    iterations: int = 1000, bounds: tuple[float, float] = (-5, 5)
) -> tuple[float, float, float]:
    """
    一个简单的随机搜索算法, 经常陷入局部最小值.

    Args:
        iterations: 运行的迭代次数
        bounds: 搜索空间的边界(min, max)

    Returns:
        返回元组(best_x, best_y, best_value)
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


# EVOLVE-BLOCK-END


# 这部分保持固定(不进化)
def evaluate_function(x: float, y: float) -> float:
    """我们要最小化的复杂函数"""
    return float(np.sin(x) * np.cos(y) + np.sin(x * y) + (x**2 + y**2) / 20)


def run_search() -> tuple[float, float, float]:
    """运行搜索算法并返回找到的最佳解.

    Returns:
        返回包含(best_x, best_y, best_value)的元组, 其中:
            best_x: 最佳解的x坐标.
            best_y: 最佳解的y坐标.
            best_value: 最佳解处的函数值.
    """
    x, y, value = search_algorithm()
    return x, y, value


if __name__ == "__main__":
    result_x, result_y, result_value = run_search()
    print(f"在点({result_x}, {result_y})找到最小值, 值为{result_value}")
