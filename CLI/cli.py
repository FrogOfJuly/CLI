import sys

sys.path.insert(0, '.')

from CLI.parser import cli_parser, CliTransformer
from CLI.arithm.arithm import Arithm
from CLI.calls.calls import GenCall
from typing import Union, List



import os


def init_memory() -> dict:
    return {"PWD": os.getcwd()}


# main io loop
if __name__ == "__main__":
    tfm = CliTransformer()
    memory = init_memory()
    # for line in stdin:
    while True:

        try:
            line = sys.stdin.readline()
        except ValueError:
            break

        line = line[:-1]
        if line == "":
            continue
        tree = cli_parser.parse(line)
        stmt: Union[List[GenCall], Arithm] = tfm.transform(tree)
        if isinstance(stmt, Arithm):
            arithm: Arithm = stmt  # type: ignore
            memory, err = arithm.update(memory)
            if err != "":
                print(err)
        else:
            calls: List[GenCall] = stmt  # type: ignore
            output = None
            for call in calls:
                call.substitute(mem=memory)
                output, err = call.execute(input=output, mem=memory)
                if err != "":
                    print(err)
            if output != "" and output is not None:
                print(output)
