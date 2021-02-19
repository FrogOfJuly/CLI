from typing import Optional, Tuple, Type, Union, TextIO, Callable, List
from sys import stdin
import re
from io import StringIO


def open_subshell() -> TextIO:
    # res = []
    # while True:
    #     try:
    #         res.append(input('> '))
    #     except EOFError:
    #         out = '\n'.join(res)
    #         break
    # return out
    return stdin


class GenCall:
    @staticmethod
    def filenames2files(filenames: List[str]) -> Tuple[str, List[TextIO]]:
        err: str = ""
        file_args: List[TextIO] = []
        for arg in filenames:
            try:
                file = open(arg, 'r')
                file_args.append(file)
            except Exception:
                err += f"Got error on opening file {arg}\n"
                continue

        return err, file_args

    @staticmethod
    def substitute_str(subst_string: str, mem: dict) -> str:
        complex_subst = re.compile("\$\{(.*?)\}")
        simple_subst = re.compile("\$([^\{])")

        def lookup(peel, match):
            var = peel(match[0])
            subst = mem.get(var, "")
            return str(subst)

        def perform_substitute(string: str, regexp, peel: Callable[[str], str]) -> str:
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

        subst_string = perform_substitute(subst_string,
                                          complex_subst,
                                          peel=lambda s: s[2:-1])
        subst_string = perform_substitute(subst_string,
                                          simple_subst,
                                          peel=lambda s: s[1:])

        return subst_string

    def __init__(self, name: str, *args: str):
        self.args: List[str] = list(args)
        self.name: str = name

    def substitute(self, mem: dict):
        args = self.args
        for idx, arg in enumerate(args):
            self.args[idx] = self.substitute_str(arg, mem)

    def execute(self, input: Optional[str], mem: dict) -> Tuple[str, str]:
        return "", "trying to execute non-existing command : \"" + str(self) + "\" on input: " + str(input)

    def __str__(self) -> str:
        return "Call: " + str(self.name) + ' ' + str(self.args)

    def __repr__(self) -> str:
        return self.__str__()


class Echo(GenCall):
    def execute(self, input: Optional[str], mem: dict) -> Tuple[str, str]:
        out = ""
        for arg in self.args:
            out += " " + str(arg)

        return out, ""


class Wc(GenCall):
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

    def execute(self, input: Optional[str], mem: dict) -> Tuple[str, str]:
        res: Tuple[int, int, int] = (0, 0, 0)
        err, file_args = self.filenames2files(self.args)

        if input is not None:
            file_args.append(StringIO(input))
            self.args.append(" ")

        if len(file_args) == 0 and err == "":
            file_args = [stdin]
            self.args.append("stdin")

        out = ""
        for name, arg in zip(self.args, file_args):
            vals: Tuple[int, int, int] = self.wc(arg)
            out += name + " : " + " ".join([str(r) for r in vals]) + "\n"
            res = tuple(acc + val for acc, val in zip(res, vals))  # type: ignore

        return out + "total : " + " ".join([str(r) for r in res]), err


class Pwd(GenCall):

    def execute(self, input: Optional[str], mem: dict) -> Tuple[str, str]:
        return self.substitute_str("${PWD}", mem), ""


class Exit(GenCall):

    @staticmethod
    def execute(input: Optional[str], mem: dict) -> Tuple[str, str]:
        stdin.close()
        return None, ""


class Cat(GenCall):

    @staticmethod
    def cat(f: Union[TextIO]) -> str:
        out = ""
        for line in f:
            out += line

        return out

    def execute(self, input: Optional[str], mem: dict) -> Tuple[str, str]:
        err, file_args = self.filenames2files(self.args)

        if input is not None:
            file_args.append(StringIO(input))
            self.args.append(" ")

        if len(file_args) == 0 and err == "":
            file_args = [stdin]
            self.args.append("stdin")
        out = ""
        for name, arg in zip(self.args, file_args):
            out += self.cat(arg)

        return out, err


def call_factory(name: str) -> Type:  # returns a type constructor
    return {
        "echo": Echo,
        "wc": Wc,
        "pwd": Pwd,
        "exit": Exit,
        "cat": Cat,
    }.get(name, GenCall)
