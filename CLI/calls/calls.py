from typing import Optional, Tuple, Type, Union, TextIO


def open_subshell() -> str:
    res = []

    while True:
        try:
            res.append(input('> '))
        except EOFError:
            out = '\n'.join(res)
            break
    return out


class GenCall:
    def __init__(self, name: str, *args: str):
        self.args: Tuple[str] = args
        self.name: str = name

    def execute(self, input: Optional[str] = None) -> (str, str):
        return "", "trying to execute non-existing command : \"" + str(self) + "\" on input: " + input

    def __str__(self) -> str:
        return "Call: " + str(self.name) + ' ' + str(self.args)

    def __repr__(self) -> str:
        return self.__str__()


class Echo(GenCall):
    def execute(self, input: Optional[str] = None) -> (str, str):
        out = ""
        for arg in self.args:
            out += " " + str(arg)

        return out, ""


class WC(GenCall):
    def wc(self, f: Union[TextIO, str]) -> Tuple[int, int, int]:
        return 0, 0, 0

    def execute(self, input: Optional[str] = None) -> (str, str):
        res: Tuple[int, int, int] = (0, 0, 0)
        err: str = ""
        file_args: [Union[TextIO, str]] = []
        for arg in self.args:
            try:
                file_args.append(open(arg))
            except Exception as excep:
                err += str(excep)
                continue

        if len(self.args) == 0:
            subshell_input: str = open_subshell()
            file_args = [subshell_input]

        for arg in file_args:
            vals: Tuple[int, int, int] = self.wc(arg)
            res = tuple(acc + val for acc, val in zip(res, vals))

        return " ".join([str(r) for r in res]), ""


def call_factory(name: str) -> Type:  # returns a type constructor
    return {
        "echo": Echo,
        "wc": WC
    }.get(name, GenCall)
