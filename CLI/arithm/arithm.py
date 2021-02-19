from typing import Type


class Arithm:
    def __init__(self, *arithmic: str):
        # print(f"Arithm got {arithmic} as arguments")
        self.arithm: (str, ...) = arithmic

    def __str__(self):
        return str(self.arithm)

    def __repr__(self):
        return self.__str__()

    def update(self, mem: dict) -> (dict, str):
        return mem, f"Requesting to perform unknown operation {self.arithm}"


class Assignment(Arithm):
    def update(self, mem: dict) -> (dict, str):
        err = ""
        if len(self.arithm) != 2:
            err += f"Something went wrong with assign operator arguments {self.arithm}"
        left, right = self.arithm
        mem[left] = right
        return mem, err


def arithm_factory(name: str) -> Type:
    return {
        "=": Assignment
    }.get(name, Arithm)
