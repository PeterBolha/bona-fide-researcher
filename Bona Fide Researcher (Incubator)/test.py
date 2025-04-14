import abc
from abc import ABC, abstractmethod


class CommonBase:
    def __init__(self, base_arg="Base arg"):
        self.base_arg = base_arg

class Letter(CommonBase):
    def __init__(self, letter: str):
        super().__init__()
        self.letter = letter

class Number(CommonBase):
    def __init__(self, number: int):
        super().__init__()
        self.number = number

class Interface1:
    @abc.abstractmethod
    def fun1(self):
        pass

class Interface2:
    @abc.abstractmethod
    def fun2(self):
        pass

class Foo(Interface1, Interface2):
    def __init__(self, a: int = None, b: str = None):
        self.a = a
        self.b = b

    def __eq__(self, other):
        return self.a == other.a and self.b == other.b

    def __hash__(self):
        return hash((self.a, self.b))

    def process(self, x: CommonBase):
        match x:
            case Number():
                print("Number: ", x.number)
            case Letter():
                print("Letter: ", x.letter)
            case CommonBase():
                print(x.base_arg)

foo1 = Foo(1)
foo2 = Foo(2)
fooX = Foo("xxx")

d = {}
d[foo1] = "foo 1"
d[foo2] = "foo 2"
print(d[foo1])
d[foo1] = "new foo 1"
print(d[foo1])

