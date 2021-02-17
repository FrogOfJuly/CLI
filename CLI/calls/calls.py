from typing import Optional, Tuple, Type, Union, TextIO, Callable, List
from sys import stdin
import re


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
    @staticmethod
    def substitute_str(subst_string: str, mem: dict) -> str:
        complex_subst = re.compile("\$\{(.*?)\}")
        simple_subst = re.compile("\$([^\{])")

        def lookup(peel, match):
            var = peel(match[0])
            subst = mem.get(var, "")
            return str(subst)

        def perfrom_substitude(string: str, regexp, peel: Callable[[str], str]):
            new_string = re.sub(regexp,
                                repl=lambda x: lookup(peel=peel,
                                                      match=x),
                                string=string)
            while string != new_string:
                string = new_string
                new_string = re.sub(regexp,
                                    repl=lambda x: lookup(peel=peel,
                                                          match=x),
                                    string=string)

            return new_string

        subst_string = perfrom_substitude(subst_string,
                                          complex_subst,
                                          peel=lambda s: s[2:-1])
        subst_string = perfrom_substitude(subst_string,
                                          simple_subst,
                                          peel=lambda s: s[1:])

        return subst_string

    def __init__(self, name: str, *args: str):
        self.args: List[str] = list(args)
        self.name: str = name

    def substitude(self, mem: dict):
        args = self.args
        for idx, arg in enumerate(args):
            self.args[idx] = self.substitute_str(arg, mem)

    def execute(self, input: Optional[str] = None, mem: dict = {}) -> (str, str):
        return "", "trying to execute non-existing command : \"" + str(self) + "\" on input: " + input

    def __str__(self) -> str:
        return "Call: " + str(self.name) + ' ' + str(self.args)

    def __repr__(self) -> str:
        return self.__str__()


class Echo(GenCall):
    def execute(self, input: Optional[str] = None, mem: dict = {}) -> (str, str):
        out = ""
        for arg in self.args:
            out += " " + str(arg)

        return out, ""


class WC(GenCall):
    @staticmethod
    def wc(f: Union[TextIO, str]) -> Tuple[int, int, int]:
        if isinstance(f, str):
            lines = f.split('\n')
            lc = len(lines)
            words = []
            for line in lines:
                words += line.split(' ')
            wc = len(words)
            bc = len(f.encode("utf8"))
            return lc, wc, bc
        ln = -1
        wc = 0
        bc = 0
        for ln, line in enumerate(f):
            wc += len(line.split(" "))
            bc += len((line + '\n').encode("utf8"))

        return ln + 1, wc, bc

    def execute(self, input: Optional[str] = None, mem: dict = {}) -> (str, str):
        res: Tuple[int, int, int] = (0, 0, 0)
        err: str = ""
        file_args: [Union[TextIO, str]] = []
        for arg in self.args:
            try:
                file = open(arg, 'r')
                file_args.append(file)
            except Exception:
                err += f"Got error on opening file {arg}\n"
                continue

        if input is not None:
            file_args.append(input)
            self.args.append(" ")

        if len(file_args) == 0 and err == "":
            subshell_input: str = open_subshell()
            file_args = [subshell_input]
            self.args.append("stdin")

        out = ""
        for name, arg in zip(self.args, file_args):
            vals: Tuple[int, int, int] = self.wc(arg)
            out += name + ": " + " ".join([str(r) for r in vals]) + "\n"
            res = tuple(acc + val for acc, val in zip(res, vals))

        return out + "total :" + " ".join([str(r) for r in res]), err


class PWD(GenCall):

    def execute(self, input: Optional[str] = None, mem: dict = {}) -> (str, str):
        return self.substitute_str("${PWD}", mem), ""


class EXIT(GenCall):

    def execute(self, input: Optional[str] = None, mem: dict = {}) -> (str, str):
        stdin.close()
        return None, ""


class CAT(GenCall):
    def cat(self, f: Union[TextIO, str]) -> str:
        if isinstance(f, str):
            return f
        out = ""
        for line in f:
            out += line

        return out

    def execute(self, input: Optional[str] = None, mem: dict = {}) -> (str, str):
        err: str = ""
        file_args: [Union[TextIO, str]] = []
        for arg in self.args:
            try:
                file = open(arg, 'r')
                file_args.append(file)
            except Exception:
                err += f"Got error on opening file {arg}\n"
                continue

        if len(file_args) == 0 and err == "":
            subshell_input: str = open_subshell()
            file_args = [subshell_input]
            self.args.append("stdin")
        out = ""
        for name, arg in zip(self.args, file_args):
            out += self.cat(arg)

        return out, err


def call_factory(name: str) -> Type:  # returns a type constructor
    return {
        "echo": Echo,
        "wc": WC,
        "pwd": PWD,
        "exit": EXIT,
        "cat": CAT,
    }.get(name, GenCall)
