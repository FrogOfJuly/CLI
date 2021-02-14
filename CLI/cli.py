from sys import stdin
from CLI.parser import cli_parser, CliTransformer


class Test:
    pass


# main io loop
if __name__ == "__main__":
    tfm = CliTransformer()
    for line in stdin:
        tree = cli_parser.parse(line[:-1])
        calls = tfm.transform(tree)
        output = ""
        for call in calls:
            output, err = call.execute(input=output)
            print(err)
        print(output)
