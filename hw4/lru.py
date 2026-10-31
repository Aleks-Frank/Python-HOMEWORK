class LRUCache:
    def __init__(self, capacity):
        if not isinstance(capacity, int):
            raise TypeError('capacity must be an integer')
        if capacity < 0:
            raise ValueError('capacity must not be negative')
        self._capacity = capacity
        self._data = {}

    def get(self, key, default=None):
        if key not in self._data:
            return default
        value = self._data.pop(key)
        self._data[key] = value
        return value

    def put(self, key, value):
        if self._capacity == 0:
            return
        if key in self._data:
            self._data.pop(key)
        elif len(self._data) >= self._capacity:
            oldest = next(iter(self._data))
            del self._data[oldest]
        self._data[key] = value

    def __contains__(self, key):
        return key in self._data

    def __len__(self):
        return len(self._data)


if __name__ == '__main__':
    c = LRUCache(2)
    c.put('a', 1)
    c.put('b', 2)
    assert c.get('a') == 1
    c.put('c', 3)
    assert 'b' not in c and c.get('a') == 1 and c.get('c') == 3
    c.put('a', 10)
    c.put('d', 4)
    assert c.get('c') is None and c.get('a') == 10 and len(c) == 2

    c = LRUCache(2)
    c.put('a', 1)
    c.put('b', 2)
    assert 'a' in c
    c.put('c', 3)
    assert 'a' not in c and 'b' in c and 'c' in c

    c = LRUCache(2)
    c.put('a', 1)
    c.put('b', 2)
    c.put('a', 10)
    assert len(c) == 2
    assert c.get('b') == 2
    c.put('c', 3)
    assert 'a' not in c and 'b' in c and 'c' in c

    c = LRUCache(1)
    c.put('x', 1)
    c.put('y', 2)
    assert 'x' not in c and c.get('y') == 2 and len(c) == 1

    c = LRUCache(3)
    c.put(1, 'one')
    c.put(2, 'two')
    c.put(3, 'three')
    assert c.get(1) == 'one'
    assert c.get(2) == 'two'
    c.put(4, 'four')
    assert 3 not in c
    assert c.get(3, 'missing') == 'missing'
    assert c.get(1) == 'one'
    assert c.get(4) == 'four'
    assert len(c) == 3

    c = LRUCache(2)
    c.put('none', None)
    assert 'none' in c
    assert c.get('none') is None
    assert c.get('absent') is None
    assert c.get('absent', 0) == 0

    c = LRUCache(0)
    c.put('a', 1)
    assert len(c) == 0 and 'a' not in c and c.get('a') is None

    try:
        LRUCache(-1)
        assert False, 'ожидали ValueError'
    except ValueError:
        pass

    try:
        LRUCache(1.5)
        assert False, 'ожидали TypeError'
    except TypeError:
        pass

    c = LRUCache(1000)
    for i in range(1000):
        c.put(i, i * 2)
    assert len(c) == 1000
    for i in range(1000):
        assert c.get(i) == i * 2
    c.put(1000, 2000)
    assert 0 not in c and len(c) == 1000 and c.get(1000) == 2000

# В комментарии объясните, почему удаление самого старого элемента работает за O(1) и какую конструкцию вы для этого использовали.
#
#    Удаление самого старого элемента выполняется за O(1), потому что обычный dict
#    сохраняет порядок вставки. Cамый старый ключ является первый ключ словаря, который
#    получается через next(iter(self._data)). При обращении или перезаписи ключ
#    удаляется и вставляется заново, переезжая в конец, а новая пара и так попадает
#    в конец. Используется встроенный порядок dict.
