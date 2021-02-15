from lark import Lark, Transformer
import CLI.calls.calls as calls
import CLI.arithm.arithm as arithm

cli_grammar = r'''

    start: command | arithm
    
    arithm.1 : ARITHM
    
    ARITHM: /.+/
    
    pipe: "|"

    command.2: call (pipe call)*

    call: name " " (arg)*

    name: /[a-zA-Z][a-zA-Z0-9_]*/

    arg: string | word 

    string : ESCAPED_STRING
    word : /[^\ |()\"\']+/

    %import common.ESCAPED_STRING
    %import common.WS
    // %import common.CNAME

    %ignore WS

'''

cli_parser = Lark(
    cli_grammar, start='start'
)


class CliTransformer(Transformer):
    def start(self, items):
        item, = items
        return item

    def command(self, items):  # items here are parsed commands divided by pipes
        assert len(items) % 2 == 1, f"something went wrong here!! {items}"
        pipe = []
        for idx, item in enumerate(items):
            if idx % 2 == 0:
                pipe.append(item)
        return pipe

    def call(self, items):
        name, *args = items
        # print(f"raw args: {args}")
        args = [arg.value for arg in args]
        # print(f"constructing call with name {name} and args: {args}")
        return calls.call_factory(name)(name, *args)

    def pipe(self, _):
        return None

    def name(self, items):
        (item,) = items
        return item

    def arg(self, items):
        (item,) = items
        # print(f"constructing arg: {item}")
        return item

    def string(self, items):
        (item,) = items
        # print(f"constructing string {item}")
        return item

    def word(self, items):
        (item,) = items
        return item

    def arithm(self, items):
        print(f"constructing arithmetics: {items}")
        (item,) = items
        return item

    def ARITHM(self, items):
        print(f"constructing ARITHM: {items}")
        return arithm.Arithm(items)
