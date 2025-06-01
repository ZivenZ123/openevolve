"""
函数最小化示例的评估器
"""

import importlib.util
import multiprocessing
import time
import traceback
from typing import Any, Callable

import numpy as np


def run_with_timeout(
    func: Callable,
    args: tuple = (),
    kwargs: dict = {},
    timeout_seconds: int = 5,
) -> Any:
    """
    使用concurrent.futures运行带超时的函数

    Args:
        func: 要运行的函数
        args: 传递给函数的参数
        kwargs: 传递给函数的关键字参数
        timeout_seconds: 超时时间(秒)

    Returns:
        函数结果或抛出TimeoutError
    """

    def wrapper(
        queue: multiprocessing.Queue,
        func: Callable,
        args: tuple,
        kwargs: dict,
    ) -> None:
        try:
            result = func(*args, **kwargs)
            queue.put(("success", result))
        except Exception as e:
            queue.put(("error", e))

    queue: multiprocessing.Queue = multiprocessing.Queue()
    process = multiprocessing.Process(
        target=wrapper, args=(queue, func, args, kwargs)
    )
    process.start()
    process.join(timeout=timeout_seconds)

    if process.is_alive():
        process.terminate()
        process.join()
        raise TimeoutError(f"函数在{timeout_seconds}秒后超时")

    if queue.empty():
        raise TimeoutError("函数结束但未返回结果")

    status, result = queue.get()
    if status == "error":
        raise result
    return result


def safe_float(value: Any) -> float:
    """安全地将值转换为float类型"""
    try:
        return float(value)
    except (TypeError, ValueError):
        print(f"警告: 无法将类型为{type(value)}的值{value}转换为float")
        return 0.0


def evaluate(program_path: str) -> dict[str, Any]:
    """
    通过多次运行程序并检查其接近已知全局最小值的程度来评估程序

    Args:
        program_path: 程序文件路径

    Returns:
        包含各项指标的字典
    """
    # 已知的全局最小值(近似值)
    GLOBAL_MIN_X = -1.704
    GLOBAL_MIN_Y = 0.678
    GLOBAL_MIN_VALUE = -1.519

    try:
        # 加载程序
        spec = importlib.util.spec_from_file_location("program", program_path)
        program = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(program)

        # 检查必需函数是否存在
        if not hasattr(program, "run_search"):
            print("错误: 程序缺少'run_search'函数")
            return {
                "value_score": 0.0,
                "distance_score": 0.0,
                "speed_score": 0.0,
                "combined_score": 0.0,
                "error": "缺少run_search函数",
            }

        # 运行多次试验
        num_trials = 10
        x_values = []
        y_values = []
        values = []
        distances = []
        times = []
        success_count = 0

        for trial in range(num_trials):
            try:
                start_time = time.time()

                # 带超时运行
                result = run_with_timeout(
                    program.run_search, timeout_seconds=5
                )

                # 检查是否得到3个值的元组
                if not isinstance(result, tuple) or len(result) != 3:
                    print(
                        f"试验{trial}: 结果格式无效, 期望3个值的元组但得到{type(result)}"
                    )
                    continue

                x, y, value = result

                end_time = time.time()

                # 确保所有值都是float类型
                x = safe_float(x)
                y = safe_float(y)
                value = safe_float(value)

                # 检查结果是否有效(非NaN或无限大)
                if (
                    np.isnan(x)
                    or np.isnan(y)
                    or np.isnan(value)
                    or np.isinf(x)
                    or np.isinf(y)
                    or np.isinf(value)
                ):
                    print(
                        f"试验{trial}: 无效结果, 得到x={x}, y={y}, value={value}"
                    )
                    continue

                # 计算指标
                x_diff = x - GLOBAL_MIN_X
                y_diff = y - GLOBAL_MIN_Y
                distance_to_global = np.sqrt(x_diff**2 + y_diff**2)

                x_values.append(x)
                y_values.append(y)
                values.append(value)
                distances.append(distance_to_global)
                times.append(end_time - start_time)
                success_count += 1

            except TimeoutError as e:
                print(f"试验{trial}: {str(e)}")
                continue
            except IndexError as e:
                # 特别处理通常在早期终止检查中发生的IndexError
                print(f"试验{trial}: IndexError - {str(e)}")
                print("这可能是由于在列表完全填充之前检查了列表索引")
                continue
            except Exception as e:
                print(f"试验{trial}: 错误 - {str(e)}")
                print(traceback.format_exc())
                continue

        # 如果所有试验都失败,返回零分
        if success_count == 0:
            return {
                "value_score": 0.0,
                "distance_score": 0.0,
                "speed_score": 0.0,
                "combined_score": 0.0,
                "error": "所有试验都失败",
            }

        # 计算指标
        avg_value = float(np.mean(values))
        avg_distance = float(np.mean(distances))
        avg_time = float(np.mean(times)) if times else 1.0

        # 转换为分数(越高越好)
        value_score = float(
            1.0 / (1.0 + abs(avg_value - GLOBAL_MIN_VALUE))
        )  # 归一化并反转
        distance_score = float(1.0 / (1.0 + avg_distance))
        speed_score = float(1.0 / avg_time) if avg_time > 0 else 0.0

        # 计算标准差分数
        x_std_score = float(1.0 / (1.0 + np.std(x_values)))
        y_std_score = float(1.0 / (1.0 + np.std(x_values)))
        standard_deviation_score = (x_std_score + y_std_score) / 2.0

        # 标准化速度分数(避免主导)
        speed_score = float(min(speed_score, 10.0) / 10.0)

        # 基于成功率添加可靠性分数
        reliability_score = float(success_count / num_trials)

        # 计算综合分数,优先考虑找到好的解决方案
        # 而不是速度和可靠性等次要指标
        # 值和距离分数(解决方案质量)占90%权重
        # 速度和可靠性仅占10%
        combined_score = float(
            0.35 * value_score
            + 0.35 * distance_score
            + standard_deviation_score * 0.20
            + 0.05 * speed_score
            + 0.05 * reliability_score
        )

        # 同时计算"总体"分数,将作为主要选择指标
        # 这为接近全局最小值的解决方案添加了奖励
        # 并对未找到正确区域的解决方案进行重罚
        if distance_to_global < 1.0:  # 非常接近正确解
            solution_quality = 1.0
        elif distance_to_global < 3.0:  # 在正确区域
            solution_quality = 0.5
        else:  # 未找到正确区域
            solution_quality = 0.1

        # 总体分数主要由解决方案质量决定,但也考虑综合分数
        overall_score = 0.8 * solution_quality + 0.2 * combined_score

        return {
            "value_score": value_score,
            "distance_score": distance_score,
            "standard_deviation_score": standard_deviation_score,
            "speed_score": speed_score,
            "reliability_score": reliability_score,
            "combined_score": combined_score,
            "overall_score": overall_score,  # 这将作为主要选择指标
            "success_rate": reliability_score,
        }
    except Exception as e:
        print(f"评估完全失败: {str(e)}")
        print(traceback.format_exc())
        return {
            "value_score": 0.0,
            "distance_score": 0.0,
            "speed_score": 0.0,
            "combined_score": 0.0,
            "error": str(e),
        }


# 基于阶段的级联评估
def evaluate_stage1(program_path: str) -> dict[str, Any]:
    """第一阶段评估, 使用较少试验次数"""
    # 已知的全局最小值(近似值)
    GLOBAL_MIN_X = float(-1.704)
    GLOBAL_MIN_Y = float(0.678)
    GLOBAL_MIN_VALUE = float(-1.519)

    # 快速检查程序是否能无错误运行
    try:
        # 加载程序
        spec = importlib.util.spec_from_file_location("program", program_path)
        program = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(program)

        # 检查必需函数是否存在
        if not hasattr(program, "run_search"):
            print(f"阶段1验证: 程序缺少'run_search'函数")
            return {
                "runs_successfully": 0.0,
                "error": "缺少run_search函数",
            }

        try:
            # 运行单次试验(带超时)
            result = run_with_timeout(program.run_search, timeout_seconds=5)

            # 检查是否返回3个值的元组
            if not isinstance(result, tuple) or len(result) != 3:
                print(
                    f"阶段1: 无效结果格式, 期望3个值的元组但得到{type(result)}"
                )
                return {
                    "runs_successfully": 0.0,
                    "error": "无效结果格式",
                }

            x, y, value = result

            # 确保所有值都是float类型
            x = safe_float(x)
            y = safe_float(y)
            value = safe_float(value)

            # 检查结果是否有效
            if (
                np.isnan(x)
                or np.isnan(y)
                or np.isnan(value)
                or np.isinf(x)
                or np.isinf(y)
                or np.isinf(value)
            ):
                print(f"阶段1验证: 无效结果, 得到x={x}, y={y}, value={value}")
                return {
                    "runs_successfully": 0.5,
                    "error": "无效结果值",
                }

            # 安全计算距离
            x_diff = float(x) - GLOBAL_MIN_X
            y_diff = float(y) - GLOBAL_MIN_Y
            distance = float(np.sqrt(x_diff**2 + y_diff**2))

            # 计算基于值的分数
            value_score = float(1.0 / (1.0 + abs(value - GLOBAL_MIN_VALUE)))
            distance_score = float(1.0 / (1.0 + distance))

            # 计算解决方案质量指标
            if distance < 1.0:  # 非常接近正确解
                solution_quality = 1.0
            elif distance < 3.0:  # 在正确区域
                solution_quality = 0.5
            else:  # 未找到正确区域
                solution_quality = 0.1

            # 包含总体分数的基本指标
            return {
                "runs_successfully": 1.0,
                "value_score": value_score,
                "distance_score": distance_score,
                "overall_score": solution_quality,  # 这将作为强指导指标
            }
        except TimeoutError as e:
            print(f"阶段1评估超时: {e}")
            return {"runs_successfully": 0.0, "error": "超时"}
        except IndexError as e:
            # 特别处理通常在提前终止检查时发生的IndexError
            print(f"阶段1评估因IndexError失败: {e}")
            print("这可能是由于在列表完全填充前检查了列表索引.")
            return {"runs_successfully": 0.0, "error": f"IndexError: {str(e)}"}
        except Exception as e:
            print(f"阶段1评估失败: {e}")
            print(traceback.format_exc())
            return {"runs_successfully": 0.0, "error": str(e)}

    except Exception as e:
        print(f"阶段1评估失败: {e}")
        print(traceback.format_exc())
        return {"runs_successfully": 0.0, "error": str(e)}


def evaluate_stage2(program_path: str) -> dict[str, Any]:
    """第二阶段评估, 进行更全面的测试"""
    # 完整评估, 同主评估函数
    return evaluate(program_path)
