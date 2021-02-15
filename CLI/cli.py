from sys import stdin
from CLI.parser import cli_parser, CliTransformer
from CLI.arithm.arithm import Arithm
from CLI.calls.calls import GenCall
from typing import Union, List


class Test:
    pass


# main io loop
if __name__ == "__main__":
    tfm = CliTransformer()
    memory = {}
    for line in stdin:
        tree = cli_parser.parse(line[:-1])
        stmt: Union[List[GenCall], Arithm] = tfm.transform(tree)
        print(stmt)
        if isinstance(stmt, Arithm):
            arithm = stmt
            memory, err = arithm.update(memory)
            print(err)
        else:
            calls = stmt
            output = ""
            for call in calls:
                output, err = call.execute(input=output)
                print(err)
            print(output)
