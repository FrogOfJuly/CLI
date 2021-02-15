class Arithm:
    def __init__(self, arithmic: str):
        self.arithm: str = arithmic

    def __str__(self):
        return self.arithm

    def __repr__(self):
        return self.__str__()

    def update(self, mem: dict) -> (dict, str):
        return mem, f"Requesting to perform unknown operation {self.arithm}"
