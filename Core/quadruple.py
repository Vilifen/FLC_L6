class Quadruple:
    """Класс для представления тетрады"""
    def __init__(self, op, arg1, arg2, result):
        self.op = op      # операция (+, -, *, /, %)
        self.arg1 = arg1  # первый операнд
        self.arg2 = arg2  # второй операнд
        self.result = result  # результат операции
    
    def __str__(self):
        return f"({self.op}, {self.arg1}, {self.arg2}, {self.result})"
    
    def __repr__(self):
        return self.__str__()
