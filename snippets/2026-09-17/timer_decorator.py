# -*- coding: utf-8 -*-
"""
每日一技 demo：Python 计时装饰器
运行：python timer_decorator.py
"""
import time
import functools


def timer(func):
    """打印函数耗时的装饰器"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0 = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - t0
        print(f"[{func.__name__}] 耗时 {elapsed:.4f}s")
        return result
    return wrapper


def memoize(func):
    """简易缓存装饰器：演示装饰器叠加"""
    cache = {}

    @functools.wraps(func)
    def wrapper(n):
        if n not in cache:
            cache[n] = func(n)
        return cache[n]
    return wrapper


# 注意叠加顺序：timer 在最外层，只统计一次总耗时
@timer
@memoize
def slow_square(n: int) -> int:
    """模拟耗时计算"""
    time.sleep(0.5)
    return n * n


@memoize
def fib(n: int) -> int:
    """朴素递归斐波那契（配缓存后瞬间出结果）"""
    return n if n < 2 else fib(n - 1) + fib(n - 2)


if __name__ == "__main__":
    print("第一次调用 slow_square(10)：")
    slow_square(10)

    print("\n第二次调用（命中缓存，连 sleep 都跳过）：")
    slow_square(10)

    t0 = time.perf_counter()
    print(f"\n缓存版 fib(300) = {str(fib(300))[:40]}...（共 {len(str(fib(300)))} 位数字）")
    print(f"fib(300) 总耗时 {time.perf_counter() - t0:.4f}s")

    print("\n要点：")
    print("1. functools.wraps 保留原函数签名，slow_square.__name__ =", slow_square.__name__)
    print("2. @timer 在 @memoize 外层 → 只计时一次整体调用")
    print("3. 生产环境直接用 functools.lru_cache 代替手写 memoize")
