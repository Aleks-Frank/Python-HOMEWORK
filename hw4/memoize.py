import time


def memoize(func):
    cache = {}

    def wrapper(*args, **kwargs):
        try:
            key = (args, tuple(sorted(kwargs.items())))
            hash(key)
        except TypeError:
            return func(*args, **kwargs)

        if key in cache:
            wrapper.hits += 1
            return cache[key]

        wrapper.misses += 1
        result = func(*args, **kwargs)
        cache[key] = result
        return result

    wrapper.hits = 0
    wrapper.misses = 0
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    wrapper.__wrapped__ = func

    def cache_clear():
        cache.clear()
        wrapper.hits = 0
        wrapper.misses = 0

    wrapper.cache_clear = cache_clear
    return wrapper


if __name__ == '__main__':
    calls = []

    def slow_square(x, power=2):
        '''Возводит в степень.'''
        calls.append(x)
        return x ** power

    sq = memoize(slow_square)
    assert sq(3) == 9 and sq(3) == 9 and sq(3, power=3) == 27
    assert calls == [3, 3]
    assert (sq.hits, sq.misses) == (1, 2)
    assert sq.__name__ == 'slow_square' and sq.__doc__ == 'Возводит в степень.'
    total = memoize(sum)
    assert total([1, 2, 3]) == 6 and total([1, 2, 3]) == 6
    assert (total.hits, total.misses) == (0, 0)
    sq.cache_clear()
    assert (sq.hits, sq.misses) == (0, 0)
    sq(3)
    assert calls[-1] == 3

    def combine(a, b=0):
        return a + b

    cached_combine = memoize(combine)
    assert cached_combine(1, b=2) == 3
    assert cached_combine(1, b=3) == 4
    assert (cached_combine.hits, cached_combine.misses) == (0, 2)
    assert cached_combine(1, b=2) == 3
    assert (cached_combine.hits, cached_combine.misses) == (1, 2)
    assert cached_combine(b=2, a=1) == 3
    assert (cached_combine.hits, cached_combine.misses) == (1, 3)
    assert cached_combine(a=1, b=2) == 3
    assert (cached_combine.hits, cached_combine.misses) == (2, 3)
    assert cached_combine(1, 2) == 3
    assert (cached_combine.hits, cached_combine.misses) == (2, 4)
    assert cached_combine.__name__ == 'combine'
    assert cached_combine.__wrapped__ is combine

    def first_element(items):
        return items[0]

    cached_first = memoize(first_element)
    assert cached_first([10, 20]) == 10
    assert cached_first([10, 20]) == 10
    assert (cached_first.hits, cached_first.misses) == (0, 0)
    assert cached_first([30]) == 30
    assert (cached_first.hits, cached_first.misses) == (0, 0)
    assert cached_first((1, 2)) == 1
    assert cached_first((1, 2)) == 1
    assert (cached_first.hits, cached_first.misses) == (1, 1)

    def keyword_unhashable(*, data):
        return sum(data)

    cached_kw = memoize(keyword_unhashable)
    assert cached_kw(data=[1, 2]) == 3
    assert cached_kw(data=[1, 2, 3]) == 6
    assert (cached_kw.hits, cached_kw.misses) == (0, 0)

    none_calls = []

    def returns_none(value):
        none_calls.append(value)
        return None

    cached_none = memoize(returns_none)
    assert cached_none(5) is None
    assert cached_none(5) is None
    assert none_calls == [5]
    assert (cached_none.hits, cached_none.misses) == (1, 1)

    no_args_calls = []

    def no_args():
        no_args_calls.append(1)
        return 42

    cached_no_args = memoize(no_args)
    assert cached_no_args() == 42
    assert cached_no_args() == 42
    assert no_args_calls == [1]
    assert (cached_no_args.hits, cached_no_args.misses) == (1, 1)

    error_calls = []

    def sometimes_fails(value):
        error_calls.append(value)
        if value < 0:
            raise ValueError('negative')
        return value

    cached_fails = memoize(sometimes_fails)
    try:
        cached_fails(-1)
        assert False, 'ожидали ValueError'
    except ValueError:
        pass
    assert (cached_fails.hits, cached_fails.misses) == (0, 1)
    try:
        cached_fails(-1)
        assert False, 'ожидали ValueError'
    except ValueError:
        pass
    assert error_calls == [-1, -1]
    assert (cached_fails.hits, cached_fails.misses) == (0, 2)

    cached_combine.cache_clear()
    assert (cached_combine.hits, cached_combine.misses) == (0, 0)
    assert cached_combine(1, b=2) == 3
    assert (cached_combine.hits, cached_combine.misses) == (0, 1)

    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    fast_fib = memoize(fib)
    start = time.perf_counter()
    value_a = fast_fib(30)
    time_a = time.perf_counter() - start
    misses_a = fast_fib.misses

    def fib(n):
        return n if n < 2 else fib(n - 1) + fib(n - 2)

    fib = memoize(fib)
    start = time.perf_counter()
    value_b = fib(30)
    time_b = time.perf_counter() - start
    misses_b = fib.misses

    assert value_a == value_b == 832040
    assert misses_a == 1
    assert misses_b == 31
    print(f'variant A: misses={misses_a}, time={time_a:.6f} s')
    print(f'variant B: misses={misses_b}, time={time_b:.6f} s')

# Сравните два варианта и для каждого выведите misses после вызова с n = 30 и время работы.
# В комментарии объясните почему, используя правило LEGB: какое имя ищет рекурсивный вызов fib(n - 1) внутри функции и в какой момент.
#
#    В варианте A глобальное имя fib остаётся исходной функцией, поэтому
#    рекурсивный вызов fib(n - 1) внутри неё по правилу LEGB находит в глобальной
#    области именно немамоизированную fib. Кэшируется только самый первый вызов,
#    отсюда misses = 1 и экспоненциальное время. В варианте B имя fib после
#    fib = memoize(fib) уже указывает на обёртку, и тот же рекурсивный вызов при
#    каждом исполнении заново ищет fib в globals, находит обёртку и попадает в кэш.
#    Получается misses = 31 (для 0..30) и линейное время.
