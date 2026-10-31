class Money:
    __slots__ = ('amount', 'currency')

    def __init__(self, amount, currency):
        if not isinstance(amount, int):
            raise TypeError('amount must be an integer')
        if not isinstance(currency, str):
            raise TypeError('currency must be a string')
        object.__setattr__(self, 'amount', amount)
        object.__setattr__(self, 'currency', currency)

    def __setattr__(self, name, value):
        raise AttributeError('Money is immutable')

    def __delattr__(self, name):
        raise AttributeError('Money is immutable')

    def __eq__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        return self.amount == other.amount and self.currency == other.currency

    def __hash__(self):
        return hash((self.amount, self.currency))

    def __add__(self, other):
        if not isinstance(other, Money):
            return NotImplemented
        if self.currency != other.currency:
            raise ValueError(f'cannot add {self.currency} and {other.currency}')
        return Money(self.amount + other.amount, self.currency)

    def __repr__(self):
        return f'Money({self.amount}, {self.currency!r})'


def total_by_currency(payments):
    result = {}
    for payment in payments:
        if not isinstance(payment, Money):
            raise TypeError('payments must contain only Money objects')
        current = result.get(payment.currency)
        if current is None:
            result[payment.currency] = payment
        else:
            result[payment.currency] = current + payment
    return result


if __name__ == '__main__':
    assert len({Money(100, 'RUB'), Money(100, 'RUB'), Money(100, 'USD')}) == 2
    prices = {Money(100, 'RUB'): 'сто рублей'}
    assert prices[Money(100, 'RUB')] == 'сто рублей'
    assert Money(100, 'RUB') + Money(50, 'RUB') == Money(150, 'RUB')
    for action in (lambda m: setattr(m, 'amount', 5), lambda m: setattr(m, 'extra', 1)):
        try:
            action(Money(1, 'RUB'))
            assert False, 'ожидали AttributeError'
        except AttributeError:
            pass
    try:
        Money(1, 'RUB') + Money(1, 'USD')
        assert False, 'ожидали ValueError'
    except ValueError:
        pass
    pays = [Money(100, 'RUB'), Money(5, 'USD'), Money(250, 'RUB')]
    assert total_by_currency(pays) == {'RUB': Money(350, 'RUB'), 'USD': Money(5, 'USD')}

    rub = Money(100, 'RUB')
    assert rub == Money(100, 'RUB')
    assert rub != Money(100, 'USD')
    assert rub.__eq__(100) is NotImplemented
    assert rub.__eq__('100 RUB') is NotImplemented
    assert hash(rub) == hash(Money(100, 'RUB'))
    assert hash(rub) != hash(Money(100, 'USD'))
    assert repr(rub) == "Money(100, 'RUB')"
    assert repr(Money(0, 'EUR')) == "Money(0, 'EUR')"

    assert Money(0, 'RUB') + Money(0, 'RUB') == Money(0, 'RUB')
    assert Money(-5, 'RUB') + Money(5, 'RUB') == Money(0, 'RUB')
    assert Money(1, 'RUB').__add__(1) is NotImplemented
    try:
        Money(1, 'RUB') + 1
        assert False, 'ожидали TypeError'
    except TypeError:
        pass
    try:
        setattr(rub, 'currency', 'USD')
        assert False, 'ожидали AttributeError'
    except AttributeError:
        pass
    try:
        del rub.amount
        assert False, 'ожидали AttributeError'
    except AttributeError:
        pass
    assert not hasattr(rub, '__dict__')

    try:
        Money(1.5, 'RUB')
        assert False, 'ожидали TypeError'
    except TypeError:
        pass
    try:
        Money(1, 123)
        assert False, 'ожидали TypeError'
    except TypeError:
        pass

    assert total_by_currency([]) == {}
    one = [Money(10, 'RUB')]
    assert total_by_currency(one) == {'RUB': Money(10, 'RUB')}
    assert one == [Money(10, 'RUB')]
    all_same = [Money(1, 'USD'), Money(2, 'USD'), Money(3, 'USD')]
    assert total_by_currency(all_same) == {'USD': Money(6, 'USD')}
    mixed = [Money(2, 'EUR'), Money(3, 'RUB'), Money(4, 'EUR')]
    assert total_by_currency(mixed) == {'EUR': Money(6, 'EUR'), 'RUB': Money(3, 'RUB')}
    assert mixed == [Money(2, 'EUR'), Money(3, 'RUB'), Money(4, 'EUR')]

    try:
        total_by_currency([Money(1, 'RUB'), 100])
        assert False, 'ожидали TypeError'
    except TypeError:
        pass

# В комментарии (3-4 предложения) объясните, что сломалось бы, если бы поля можно было менять после того,
# как объект положили в множество или использовали как ключ. Сошлитесь на пример с Point из лекции.
#
#    Если бы поля Money можно было менять после помещения объекта в множество или
#    словарь, его хеш изменился бы, и объект остался бы в корзине, соответствующей
#    старому хешу. Тогда проверка membership и поиск по тому же ключу перестали бы
#    находить объект, а в множество можно было бы добавить «дубликат» с новым хешем.
#    В лекции Point без __hash__ вообще не кладётся в set, а после добавления
#    __hash__ по (x, y) изменение p.x уже ломает поиск в множестве visited.
