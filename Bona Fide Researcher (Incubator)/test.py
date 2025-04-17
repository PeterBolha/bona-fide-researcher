from typing import Set


class Person:
    def __init__(self, names: Set[str]):
        self.names = names

    def __str__(self):
        return "Person {}".format(self.names)

cole_val = "Coca"
cole_set = {cole_val}
# cole_set.add("Cole")
# cole_set.add("Cola")

adam = Person({"Adam"})
bob = Person({"Bob", "Burger"})
cole = Person(cole_set)

s1 = set()
s2 = {"homo", "sapiens"}

s1.update(s2)
print(s1)