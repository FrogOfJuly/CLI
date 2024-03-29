from typing import Type, Tuple


class Arithm:
    def __init__(self, *arithmic: str):
        # print(f"Arithm got {arithmic} as arguments")
        self.arithm: Tuple[str, ...] = arithmic

    def __str__(self):
        return str(self.arithm)

    def __repr__(self):
        return "Arithm obj: " + self.__str__()

    def update(self, mem: dict) -> Tuple[dict, str]:
        return mem, f"Requesting to perform unknown operation {self.arithm}"


class Assignment(Arithm):
    def update(self, mem: dict) -> Tuple[dict, str]:
        err = ""
        if len(self.arithm) != 2:
            err += f"Something went wrong with assign operator arguments {self.arithm}"
        left, right = self.arithm
        mem[left] = right
        return mem, err


Arithm.cmd_dict = { # type: ignore
    "=": Assignment
}


def arithm_factory(name: str) -> Type:
    return Arithm.cmd_dict.get(name, Arithm)# type: ignore
