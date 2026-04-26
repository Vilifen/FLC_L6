from .token_types import TokenType
from .scan_error import ScanError
from .error_codes import ErrorCode
from .quadruple import Quadruple


class Parser:
    def __init__(self, tokens, scan_errors=None):
        self.tokens = [t for t in tokens if t.type != TokenType.WHITESPACE]
        self.pos = 0
        self.errors = scan_errors if scan_errors is not None else []
        self.temp_counter = 1  
        self.quadruples = []   
        self.stack = []        

    def _new_temp(self):
        """Создать новую временную переменную"""
        temp_name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp_name

    def _add_quadruple(self, op, arg1, arg2, result):
        """Добавить тетраду как экземпляр класса Quadruple"""
        quadruple = Quadruple(op, arg1, arg2, result)
        self.quadruples.append(quadruple)

    def parse(self):
        while self.pos < len(self.tokens) and self._current_token().type != TokenType.EOF:
            current = self._current_token()

            if current.type == TokenType.NEWLINE:
                self.pos += 1
                continue

            if current.type == TokenType.ERROR:
                self.pos += 1
                self._skip_to_next_line()
                continue

            self.E()

            if self.pos < len(self.tokens) and self._current_token().type not in (TokenType.NEWLINE, TokenType.EOF):
                if self._current_token().type != TokenType.ERROR:
                    self._record_error("Неожиданный токен", ErrorCode.UNEXPECTED_TOKEN)
                self._skip_to_next_line()

            if self.stack:
                result = self.stack.pop()
                print(f"Результат выражения: {result}")

        return self.errors, self.quadruples

    def _skip_to_next_line(self):
        while self.pos < len(self.tokens) and self._current_token().type not in (TokenType.NEWLINE, TokenType.EOF):
            self.pos += 1

    def _current_token(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def _match(self, expected_type):
        if self._current_token().type == expected_type:
            self.pos += 1
            return True
        return False

    def _record_error(self, message, code):
        token = self._current_token()
        self.errors.append(ScanError(code, message, token.line, token.column, token.value))

    def E(self):
        """E → T A"""
        left_val = self.T()
        result_val = self.A(left_val)
        self.stack.append(result_val)
        return result_val

    def T(self):
        """T → F B"""
        left_val = self.F()
        result_val = self.B(left_val)
        return result_val

    def A(self, left_val):
        """A → ε | + T A | - T A"""
        current = self._current_token()
        
        if current.type == TokenType.PLUS:
            self.pos += 1  
            right_val = self.T()
            result = self.A(right_val)
            
            temp_var = self._new_temp()
            self._add_quadruple('+', left_val, right_val, temp_var)
            return temp_var
            
        elif current.type == TokenType.MINUS:
            self.pos += 1  
            right_val = self.T()
            result = self.A(right_val)
            
            temp_var = self._new_temp()
            self._add_quadruple('-', left_val, right_val, temp_var)
            return temp_var
            
        else:
            return left_val

    def B(self, left_val):
        """B → ε | * F B | / F B | % F B"""
        current = self._current_token()
        
        if current.type == TokenType.MUL:
            self.pos += 1 
            right_val = self.F()
            result = self.B(right_val)
            
            temp_var = self._new_temp()
            self._add_quadruple('*', left_val, right_val, temp_var)
            return temp_var
            
        elif current.type == TokenType.DIV:
            self.pos += 1  
            right_val = self.F()
            result = self.B(right_val)
            
            temp_var = self._new_temp()
            self._add_quadruple('/', left_val, right_val, temp_var)
            return temp_var
            
        elif current.type == TokenType.MOD:
            self.pos += 1  
            right_val = self.F()
            result = self.B(right_val)
            
            temp_var = self._new_temp()
            self._add_quadruple('%', left_val, right_val, temp_var)
            return temp_var
            
        else:
            return left_val

    def F(self):
        """F → num | $id | (E)"""
        current = self._current_token()
        
        if current.type == TokenType.NUM:
            value = current.value
            self._match(TokenType.NUM)
            return value
            
        elif current.type == TokenType.ID:
            value = f"${current.value}"
            self._match(TokenType.ID)
            return value
            
        elif current.type == TokenType.LPAREN:
            self._match(TokenType.LPAREN)
            expr_val = self.E()
            if self._current_token().type != TokenType.ERROR:
                if not self._match(TokenType.RPAREN):
                    self._record_error("Отсутствует закрывающая скобка", ErrorCode.MISSING_RPAREN)
            return expr_val
            
        elif current.type == TokenType.ERROR:
            return None
            
        elif current.type in (TokenType.RPAREN, TokenType.EOF, TokenType.NEWLINE):
            self._record_error("Справа от оператора нет переменной или числа", ErrorCode.UNEXPECTED_TOKEN)
            return None
            
        else:
            self._record_error("Слева от оператора нет переменной или числа", ErrorCode.UNEXPECTED_TOKEN)
            self.pos += 1
            return None

    def print_quadruples(self):
        """Вывести все тетрады для отладки"""
        if not self.quadruples:
            print("\nНет сгенерированных тетрад")
            return
        
        print("\nСгенерированные тетрады:")
        print("№\tОперация\tArg1\tArg2\tResult")
        print("-" * 50)
        for i, quad in enumerate(self.quadruples, 1):
            print(f"{i}\t{quad.op}\t\t{quad.arg1}\t{quad.arg2}\t{quad.result}")
    
    def get_quadruples_list(self):
        """Вернуть список тетрад"""
        return self.quadruples