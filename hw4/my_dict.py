class MyDict:
    def __init__(self, size=8):
        if size < 1:
            raise ValueError('size must be positive')
        self._buckets = [[] for _ in range(size)]
        self._len = 0

    def _bucket_index(self, key):
        return hash(key) % len(self._buckets)

    def _put(self, key, value):
        bucket = self._buckets[self._bucket_index(key)]
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])
        self._len += 1

    def _resize(self):
        old_buckets = self._buckets
        self._buckets = [[] for _ in range(len(old_buckets) * 2)]
        self._len = 0
        for bucket in old_buckets:
            for key, value in bucket:
                self._put(key, value)

    def __setitem__(self, key, value):
        self._put(key, value)
        if self._len * 3 > len(self._buckets) * 2:
            self._resize()

    def __getitem__(self, key):
        for pair in self._buckets[self._bucket_index(key)]:
            if pair[0] == key:
                return pair[1]
        raise KeyError(key)

    def __delitem__(self, key):
        bucket = self._buckets[self._bucket_index(key)]
        for i, pair in enumerate(bucket):
            if pair[0] == key:
                del bucket[i]
                self._len -= 1
                return
        raise KeyError(key)

    def __contains__(self, key):
        for pair in self._buckets[self._bucket_index(key)]:
            if pair[0] == key:
                return True
        return False

    def __len__(self):
        return self._len

    def get(self, key, default=None):
        for pair in self._buckets[self._bucket_index(key)]:
            if pair[0] == key:
                return pair[1]
        return default

    def stats(self):
        longest = 0
        for bucket in self._buckets:
            if len(bucket) > longest:
                longest = len(bucket)
        return (len(self._buckets), self._len, longest)

    def __repr__(self):
        parts = []
        for bucket in self._buckets:
            for key, value in bucket:
                parts.append(f'{key!r}: {value!r}')
        return 'MyDict({' + ', '.join(parts) + '})'


if __name__ == '__main__':
    d = MyDict()
    for i in range(1000):
        d[f'key{i}'] = i
    assert len(d) == 1000
    assert d['key42'] == 42
    assert 'key7' in d and 'nope' not in d
    d['key42'] = -1
    assert d['key42'] == -1 and len(d) == 1000
    del d['key42']
    assert 'key42' not in d and len(d) == 999
    assert d.get('nope') is None and d.get('nope', 0) == 0
    for bad in (lambda: d['nope'], lambda: d.__delitem__('nope')):
        try:
            bad()
            assert False, 'ожидали KeyError'
        except KeyError:
            pass
    buckets, size, longest = d.stats()
    assert size == 999 and size <= buckets * 2 / 3
    print(d.stats())

    empty = MyDict()
    assert len(empty) == 0
    assert empty.stats() == (8, 0, 0)
    assert repr(empty) == 'MyDict({})'
    assert empty.get('x') is None and empty.get('x', 5) == 5
    assert 'x' not in empty

    single = MyDict(1)
    single['a'] = 1
    assert single.stats()[0] == 2
    assert repr(single) == "MyDict({'a': 1})"
    single['a'] = 2
    assert len(single) == 1 and single['a'] == 2

    for i in range(10):
        single[i] = i
    del single[3]
    assert 3 not in single
    try:
        del single[3]
        assert False, 'ожидали KeyError'
    except KeyError:
        pass
    single[3] = 33
    assert single[3] == 33
    buckets, size, longest = single.stats()
    assert size == 11 and longest >= 1 and size <= buckets * 2 / 3

    class ConstantHash:
        def __init__(self, value):
            self.value = value

        def __hash__(self):
            return 42

        def __eq__(self, other):
            return isinstance(other, ConstantHash) and self.value == other.value

    colliding = MyDict()
    keys = [ConstantHash(i) for i in range(100)]
    for i, key in enumerate(keys):
        colliding[key] = i
    assert len(colliding) == 100
    assert colliding[ConstantHash(50)] == 50
    assert ConstantHash(50) in colliding
    b, s, longest = colliding.stats()
    assert s == 100 and longest == 100
    del colliding[ConstantHash(50)]
    assert ConstantHash(50) not in colliding and len(colliding) == 99

    assert 'key1' in d and 'key10' in d
    assert d.get('key999') == 999

    import time

    def measure_insert(key_factory, n=1000):
        table = MyDict()
        start = time.perf_counter()
        for i in range(n):
            table[key_factory(i)] = i
        return table, time.perf_counter() - start

    string_table, string_time = measure_insert(lambda i: f'key{i}')
    hash_table, hash_time = measure_insert(ConstantHash)
    assert string_table.stats()[0] == 2048 and string_table.stats()[1] == 1000
    assert hash_table.stats() == (2048, 1000, 1000)
    print('1000 string keys:', string_table.stats(), f'{string_time:.6f} s')
    print('1000 keys with __hash__ == 42:', hash_table.stats(), f'{hash_time:.6f} s')

# 1. Почему при увеличении таблицы пары нельзя просто скопировать в корзины с теми же номерами?
#
#    При изменении числа корзин меняется делитель в hash(key) % len(...), поэтому
#    те же номера корзин уже не соответствуют ключам. Пары нужно разложить заново,
#    иначе поиск будет обращаться не в ту корзину, а часть индексов станет недопустимой.
#
# 2. Что показывает stats() для 1000 строковых ключей и что он покажет, если ключами будут объекты,
#    у которых __hash__ всегда возвращает 42? Проверьте экспериментом, замерьте время вставки 1000 таких ключей.
#
#    Для 1000 обычных строковых ключей stats() даёт (2048, 1000, 5). Таблица
#    выросла до 2048 корзин, а пары распределены почти равномерно. Вставка заняла
#    около 0.001 с. Если __hash__ всегда возвращает 42, все 1000 пар попадут в одну
#    корзину, поэтому stats() вернёт (2048, 1000, 1000), а вставка станет
#    квадратичной — в эксперименте около 0.08-0.12 с.
