from lark import Lark, Transformer
import CLI.calls.calls as calls
import CLI.arithm.arithm as arithm

cli_grammar = r'''

    start: command | arithm
    
    arithm.1 : ARITHM
    
    ARITHM: /.+/
    
    pipe: "|"

    command.2: call (pipe call)*

    call: name | name " " (arg)+

    name: /[a-zA-Z][a-zA-Z0-9_]*/

    arg: string | word 

    string : ESCAPED_STRING
    word : /[^\ |()\"\']+/

    %import common.ESCAPED_STRING
    %import common.WS

    %ignore WS

'''

arithmetics_grammar = r'''
    arithmetics:  binary // | uop opnd
    binary : (opnd)(bop)(opnd)
    
    opnd : id | number
    number : SIGNED_NUMBER
    id : /[a-zA-Z][a-zA-Z0-9_]*/
     
    // unary : uop id
    
    bop : /[=]/  
    
    // uop : "one unary operation" | "another unary operation"
    
    %import common.WS
    %import common.SIGNED_NUMBER 
    
    %ignore WS
'''

cli_parser = Lark(
    cli_grammar, start='start'
)

arithmetics_parser = Lark(
    arithmetics_grammar, start='arithmetics'
)


class ArithmTransformer(Transformer):
    @staticmethod
    def arithmetics(items):
        item, = items
        return item

    @staticmethod
    def id(items):
        (item,) = items
        # print(f"got id: {item}")
        return str(item)

    @staticmethod
    def opnd(items):
        (item,) = items
        # print(f"got {item} as opnd")
        return item

    @staticmethod
    def number(items):
        item, = items
        # print(f"got {item} as argument for number")
        return int(item)

    @staticmethod
    def binary(items):
        assert len(items) == 3, f"something got very wrong, got \'{items}\' while parsing binary operator"
        left, op, right = items
        # print(f"got {op} with aruments {left} and {right}")
        return op(left, right)

    @staticmethod
    def bop(items):
        (item,) = items
        # print(f"constructing binary operation {item}")
        return arithm.arithm_factory(item)


class CliTransformer(Transformer):
    @staticmethod
    def start(items):
        item, = items
        return item

    @staticmethod
    def command(items):  # items here are parsed commands divided by pipes
        assert len(items) % 2 == 1, f"something went wrong here!! {items}"
        pipe = []
        for idx, item in enumerate(items):
            if idx % 2 == 0:
                pipe.append(item)
        return pipe

    @staticmethod
    def call(items):
        name, *args = items
        # print(f"raw args: {args}")
        args = [arg.value for arg in args]
        # print(f"constructing call with name {name} and args: {args}")
        return calls.call_factory(name)(name, *args)

    @staticmethod
    def pipe(_):
        return None

    @staticmethod
    def name(items):
        (item,) = items
        return item

    @staticmethod
    def arg(items):
        (item,) = items
        # print(f"constructing arg: {item}")
        return item

    @staticmethod
    def string(items):
        (item,) = items
        # print(f"constructing string {item}")
        return item

    @staticmethod
    def word(items):
        (item,) = items
        return item

    @staticmethod
    def arithm(items):
        item, = items
        # print(f"got {type(item)} as arithm")
        return item

    @staticmethod
    def ARITHM(items):
        # print(f"constructing ARITHM: {items}")
        tree = arithmetics_parser.parse(items)
        # print(tree.pretty())
        a = ArithmTransformer().transform(tree)
        return a
