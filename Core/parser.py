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
        self.current_line_has_error = False  
        self.quadruples_before_line = []     

    def _new_temp(self):
        """Создать новую временную переменную"""
        temp_name = f"t{self.temp_counter}"
        self.temp_counter += 1
        return temp_name

    def _add_quadruple(self, op, arg1, arg2, result):
        """Добавить тетраду (только если нет ошибки в текущей строке)"""
        if not self.current_line_has_error:
            quadruple = Quadruple(op, arg1, arg2, result)
            self.quadruples.append(quadruple)
            self.quadruples_before_line.append(quadruple)

    def _clear_line_quadruples(self):
        """Очистить тетрады, сгенерированные для текущей строки"""
        count_to_remove = len(self.quadruples_before_line)
        for _ in range(count_to_remove):
            if self.quadruples:
                self.quadruples.pop()
        self.quadruples_before_line.clear()

    def parse(self):
        while self.pos < len(self.tokens) and self._current_token().type != TokenType.EOF:
            self.current_line_has_error = False
            self.quadruples_before_line.clear()
            
            line_start_pos = self.pos
            start_line_num = self._current_token().line
            
            current = self._current_token()

            if current.type == TokenType.NEWLINE:
                self.pos += 1
                continue

            if current.type == TokenType.ERROR:
                self.pos += 1
                self._skip_to_next_line()
                self.current_line_has_error = True
                self._clear_line_quadruples()
                continue

            quad_count_before = len(self.quadruples)
            
            try:
                self.E()
                
                if self.pos < len(self.tokens):
                    next_token = self._current_token()
                    if next_token.type not in (TokenType.NEWLINE, TokenType.EOF):
                        if next_token.type != TokenType.ERROR:
                            self._record_error("Неожиданный токен", ErrorCode.UNEXPECTED_TOKEN)
                            self.current_line_has_error = True
                

                if self.current_line_has_error:
                    self.quadruples = self.quadruples[:quad_count_before]
                    self.quadruples_before_line.clear()
                    self._skip_to_next_line()
                
            except Exception as e:
                self.quadruples = self.quadruples[:quad_count_before]
                self.quadruples_before_line.clear()
                self.current_line_has_error = True
                self._skip_to_next_line()

            if self.stack and not self.current_line_has_error:
                result = self.stack.pop()
                print(f"Результат выражения: {result}")
            elif self.stack:
                self.stack.clear()  

            while self.pos < len(self.tokens) and self._current_token().type != TokenType.NEWLINE and self._current_token().type != TokenType.EOF:
                self.pos += 1
            if self.pos < len(self.tokens) and self._current_token().type == TokenType.NEWLINE:
                self.pos += 1

            self.current_line_has_error = False

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
        self.current_line_has_error = True

    def E(self):
        left_val = self.T()
        result_val = self.A(left_val)
        if not self.current_line_has_error:
            self.stack.append(result_val)
        return result_val

    def T(self):
        left_val = self.F()
        result_val = self.B(left_val)
        return result_val

    def A(self, left_val):
        if self.current_line_has_error:
            return left_val
            
        current = self._current_token()
        
        if current.type == TokenType.PLUS:
            self.pos += 1
            right_val = self.T()
            
            if not self.current_line_has_error:
                temp_var = self._new_temp()
                self._add_quadruple('+', left_val, right_val, temp_var)
                return self.A(temp_var)
            else:
                return left_val
            
        elif current.type == TokenType.MINUS:
            self.pos += 1
            right_val = self.T()
            
            if not self.current_line_has_error:
                temp_var = self._new_temp()
                self._add_quadruple('-', left_val, right_val, temp_var)
                return self.A(temp_var)
            else:
                return left_val
        else:
            return left_val

    def B(self, left_val):
        if self.current_line_has_error:
            return left_val
            
        current = self._current_token()
        
        if current.type == TokenType.MUL:
            self.pos += 1
            right_val = self.F()
            
            if not self.current_line_has_error:
                temp_var = self._new_temp()
                self._add_quadruple('*', left_val, right_val, temp_var)
                return self.B(temp_var)
            else:
                return left_val
            
        elif current.type == TokenType.DIV:
            self.pos += 1
            right_val = self.F()
            
            if not self.current_line_has_error:
                temp_var = self._new_temp()
                self._add_quadruple('/', left_val, right_val, temp_var)
                return self.B(temp_var)
            else:
                return left_val
            
        elif current.type == TokenType.MOD:
            self.pos += 1
            right_val = self.F()
            
            if not self.current_line_has_error:
                temp_var = self._new_temp()
                self._add_quadruple('%', left_val, right_val, temp_var)
                return self.B(temp_var)
            else:
                return left_val
        else:
            return left_val

    def F(self):
        if self.current_line_has_error:
            if self.pos < len(self.tokens):
                self.pos += 1
            return None
            
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
            if not self.current_line_has_error:
                if self._current_token().type != TokenType.ERROR:
                    if not self._match(TokenType.RPAREN):
                        self._record_error("Отсутствует закрывающая скобка", ErrorCode.MISSING_RPAREN)
            return expr_val
            
        elif current.type == TokenType.ERROR:
            self.current_line_has_error = True
            return None
            
        elif current.type in (TokenType.RPAREN, TokenType.EOF, TokenType.NEWLINE):
            self._record_error("Справа от оператора нет переменной или числа", ErrorCode.UNEXPECTED_TOKEN)
            return None
            
        else:
            self._record_error("Слева от оператора нет переменной или числа", ErrorCode.UNEXPECTED_TOKEN)
            self.pos += 1
            return None

    def print_quadruples(self):
        if not self.quadruples:
            print("\nНет сгенерированных тетрад")
            return
        
        print("\nСгенерированные тетрады:")
        print("№\tОперация\tArg1\tArg2\tResult")
        print("-" * 50)
        for i, quad in enumerate(self.quadruples, 1):
            print(f"{i}\t{quad.op}\t\t{quad.arg1}\t{quad.arg2}\t{quad.result}")
    
    def get_quadruples_list(self):
        return self.quadruples