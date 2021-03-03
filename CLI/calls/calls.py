from typing import Optional, Tuple, Type, Union, TextIO, \
    Callable, List, Generator, Iterable
from sys import stdin
import re
from io import StringIO
import os
from copy import copy


def is_stringio_empty(stringio: StringIO) -> bool:
    pos = stringio.tell()
    stringio.seek(0, os.SEEK_END)
    empty = stringio.tell() == 0
    stringio.seek(pos)
    return empty


def open_subshell() -> TextIO:
    return stdin


class GenCall:

    @staticmethod
    def filenames2files(filenames: List[str]) -> Generator[Tuple[Optional[TextIO], str], None, None]:
        for arg in filenames:
            try:
                file = open(arg, 'r')
                yield file, ""
            except OSError:
                yield None, f"Got error on opening file '{arg}'\n"
                continue

    @staticmethod
    def substitute_str(subst_string: str, mem: dict) -> str:
        complex_subst = re.compile("\$\{(.*?)\}")
        simple_subst = re.compile("\$([^\{])")

        def lookup(peel, match):
            var_match = match[0]
            var = peel(var_match)
            subst = mem.get(var, "")
            return str(subst)

        def perform_substitute(string: str,
                               regexp,
                               peel: Callable[[str], str]) -> str:
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

        # ${anything} -> anything
        complex_peel = lambda s: s[2:-1]
        # $v -> v
        simple_peel = lambda s: s[1:]

        subst_string = perform_substitute(subst_string,
                                          complex_subst,
                                          peel=complex_peel)
        subst_string = perform_substitute(subst_string,
                                          simple_subst,
                                          peel=simple_peel)

        return subst_string

    def __init__(self, name: str, *args: str):
        self.args: List[str] = list(args)
        self.name: str = name

    def substitute(self, mem: dict):
        args = self.args
        for idx, arg in enumerate(args):
            self.args[idx] = self.substitute_str(arg, mem)

    def execute(self, input: Optional[StringIO], mem: dict) -> Tuple[Optional[StringIO], str]:
        return StringIO(), "trying to execute non-existing command : \"" + str(self) + "\" on input: " + str(input)

    def __str__(self) -> str:
        return "Call: " + str(self.name) + ' ' + str(self.args)

    def __repr__(self) -> str:
        return self.__str__()


class Echo(GenCall):
    def execute(self, input: Optional[StringIO], mem: dict) -> Tuple[Optional[StringIO], str]:
        out = StringIO()
        for arg in self.args:
            out.write(str(arg))

        return out, ""


class Wc(GenCall):
    @staticmethod
    def wc(f: Union[TextIO, StringIO]) -> Tuple[int, int, int]:
        if isinstance(f, StringIO):
            it: Optional[Iterable] = f.getvalue().split("\n")
        else:
            it = f
        ln = -1
        wc = 0
        bc = 0
        for ln, line in enumerate(it):  # type: ignore
            wc += len(line.split(" "))
            bc += len((line + '\n').encode("utf8"))

        return ln + 1, wc, bc

    def execute(self,
                input: Optional[StringIO],
                mem: dict) -> Tuple[Optional[StringIO], str]:

        res: Tuple[int, int, int] = (0, 0, 0)
        file_args = self.filenames2files(copy(self.args))

        if input and not is_stringio_empty(input):
            self.args.append(" ")

            def update_file_args_with_input(file_args_to_update):
                yield from file_args_to_update
                yield input, ""

            file_args = update_file_args_with_input(file_args)

        out = StringIO()
        err = ""
        suc_filereads = 0
        for name, (file, file_err) in zip(self.args, file_args):
            if file_err:
                err += file_err
            if not file:
                continue
            vals: Tuple[int, int, int] = self.wc(file)
            out.write(name + " : " + " ".join([str(r) for r in vals]) + "\n")
            res = tuple(acc + val for acc, val in zip(res, vals))  # type: ignore
            file.close()
            suc_filereads += 1

        if suc_filereads == 0 and err == "":  # if no files were specified read from stdin
            vals_: Tuple[int, int, int] = self.wc(open_subshell())
            out.write("stdout : " + " ".join([str(r) for r in vals_]) + "\n")
            res = tuple(acc + val for acc, val in zip(res, vals_))  # type: ignore

        out.write("total : " + " ".join([str(r) for r in res]))
        return out, err


class Pwd(GenCall):

    def execute(self, input: Optional[StringIO], mem: dict) -> Tuple[Optional[StringIO], str]:
        return StringIO(self.substitute_str("${PWD}", mem)), ""


class Exit(GenCall):

    @staticmethod
    def execute(input: Optional[StringIO], mem: dict) -> Tuple[Optional[StringIO], str]:
        stdin.close()
        return None, ""


class Cat(GenCall):

    @staticmethod
    def cat(f: TextIO) -> StringIO:
        out = StringIO()
        out.write(f.read())
        return out

    def execute(self, input: Optional[StringIO], mem: dict) -> Tuple[StringIO, str]:
        file_args = self.filenames2files(copy(self.args))
        if input and not is_stringio_empty(input):
            self.args.append(" ")

            def update_file_args_with_input(file_args_to_update):
                yield from file_args_to_update
                yield input, ""

            file_args = update_file_args_with_input(file_args)

        out = StringIO()
        err = ""
        suc_filereads = 0
        for name, (file, file_err) in zip(self.args, file_args):
            if file_err:
                err += file_err
            if not file:
                continue

            # is there more efficient way to concat two iostrings?
            out.write(self.cat(file).getvalue())
            file.close()
            suc_filereads += 1

        if suc_filereads == 0 and err == "":  # if no files were specified read from stdin
            out.write(self.cat(open_subshell()).getvalue())

        return out, err


class Grep(GenCall):
    def grep(self):
        pass

    def execute(self, input: Optional[StringIO], mem: dict) -> Tuple[Optional[StringIO], str]:
        return None, "Executing grep command with " + str(self)


GenCall.cmd_dict = {  # type: ignore
    "echo": Echo,
    "wc": Wc,
    "pwd": Pwd,
    "exit": Exit,
    "cat": Cat,
    "grep": Grep,
}


def call_factory(name: str) -> Type:  # returns a type constructor
    return GenCall.cmd_dict.get(name, GenCall)  # type: ignore
