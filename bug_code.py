# Основная проблема: метод add возвращает ссылку на внутренний список array, поэтому вызывающий
# код через first.append(999) меняет состояние счётчика извне (alias). Если add вернет метод
# list(array), то появится новый объект, разрывая alias, и внутреннее состояние
# остаётся недоступным для порчи снаружи.

# Код с багом
def make_counter():
    array = []
    def add(x):
        array.append(x)
        return array
    return add

print("Итог с багом")
c = make_counter()
first = c(1)
first.append(999)
print(c(2))

# Исправленный код
def make_counter_fix():
    array = []
    def add(x):
        array.append(x)
        return list(array)
    return add

print("Итог без бага")
c = make_counter_fix()
first = c(1)
first.append(999)
print(c(2))