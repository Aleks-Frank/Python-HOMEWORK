class Config:
    def __init__(self, data):
        object.__setattr__(self, '_data', data)

    def __getattr__(self, name):
        data = object.__getattribute__(self, '_data')
        try:
            value = data[name]
        except KeyError:
            raise AttributeError(name) from None
        if isinstance(value, dict):
            return Config(value)
        return value

    def __setattr__(self, name, value):
        data = object.__getattribute__(self, '_data')
        data[name] = value

    def to_dict(self):
        return object.__getattribute__(self, '_data')

    def __dir__(self):
        data = object.__getattribute__(self, '_data')
        return sorted(set(object.__dir__(self)) | set(data))


if __name__ == '__main__':
    raw = {'db': {'host': 'localhost', 'port': 5432}, 'debug': True}
    cfg = Config(raw)
    assert cfg.debug is True
    assert cfg.db.host == 'localhost' and cfg.db.port == 5432
    assert getattr(cfg, 'timeout', 30) == 30
    assert hasattr(cfg.db, 'user') is False
    cfg.db.port = 6543
    assert raw['db']['port'] == 6543
    cfg.timeout = 10
    assert raw['timeout'] == 10
    assert cfg.to_dict() is raw
    assert 'db' in dir(cfg)

    assert isinstance(cfg.db, Config)
    assert cfg.db.to_dict() is raw['db']
    assert cfg.db.host == 'localhost'

    try:
        cfg.missing
        assert False, 'ожидали AttributeError'
    except AttributeError:
        pass
    try:
        cfg.db.missing
        assert False, 'ожидали AttributeError'
    except AttributeError:
        pass
    assert getattr(cfg, 'missing', 'default') == 'default'
    assert hasattr(cfg, 'missing') is False
    assert hasattr(cfg, 'timeout') is True

    cfg.new_key = 'new value'
    assert raw['new_key'] == 'new value'
    assert cfg.new_key == 'new value'
    assert 'new_key' in dir(cfg)

    cfg.section = {'nested': {'value': 1}}
    assert raw['section'] == {'nested': {'value': 1}}
    assert cfg.section.nested.value == 1
    cfg.section.nested.value = 2
    assert raw['section']['nested']['value'] == 2

    cfg.debug = False
    assert raw['debug'] is False and cfg.debug is False

    cfg.none_value = None
    assert cfg.none_value is None
    assert hasattr(cfg, 'none_value') is True

    cfg.items = [1, 2, 3]
    assert cfg.items == [1, 2, 3]
    assert cfg.to_dict()['items'] is cfg.items

    empty_raw = {}
    empty_cfg = Config(empty_raw)
    assert empty_cfg.to_dict() is empty_raw
    assert getattr(empty_cfg, 'x', 1) == 1
    empty_cfg.x = 2
    assert empty_raw == {'x': 2}

    deep_raw = {'a': {'b': {'c': {'d': 4}}}}
    deep_cfg = Config(deep_raw)
    assert deep_cfg.a.b.c.d == 4
    deep_cfg.a.b.c.d = 5
    assert deep_raw['a']['b']['c']['d'] == 5

    for name in ('to_dict', 'debug', 'db', 'timeout', 'new_key', 'section'):
        assert name in dir(cfg)

# 1. Почему hasattr и getattr со значением по умолчанию перестанут работать, если бросать KeyError;
#
#    Если в __getattr__ бросать KeyError, то hasattr() и getattr(obj, name, default)
#    не смогут его обработать, так как они перехватывают только AttributeError. Поэтому
#    hasattr упал бы с KeyError вместо False, а getattr с значением по умолчанию
#    не вернул бы default. Именно поэтому отсутствующий ключ преобразуется в
#    AttributeError.
#
# 2. Как вы избежали бесконечной рекурсии при обращении к собственному атрибуту, в котором хранится словарь.
#
#    Рекурсии при доступе к _data нет, потому что __getattr__ и __setattr__ берут
#    этот атрибут напрямую через object.__getattribute__, а в __init__ он кладётся
#    через object.__setattr__. То есть обращение к _data не проходит снова через
#    переопределённые __getattr__/__setattr__.
