from .token_types import TokenType


class RPNExpression:
    def __init__(self, tokens):
        self.precedence = {
            TokenType.MUL: 2, TokenType.DIV: 2, TokenType.MOD: 2,
            TokenType.PLUS: 1, TokenType.MINUS: 1
        }

        self.all_tokens = tokens
        self.results = []
        self._process_by_lines()

    def _process_by_lines(self):
        line_groups = {}
        for t in self.all_tokens:
            if t.type.name in ("WHITESPACE", "SPACE"):
                continue
            if t.line not in line_groups:
                line_groups[t.line] = []
            line_groups[t.line].append(t)

        for line_num in sorted(line_groups.keys()):
            tokens_in_line = line_groups[line_num]

            parens = [t for t in tokens_in_line if t.type in (TokenType.LPAREN, TokenType.RPAREN)]
            balance = 0
            for p in parens:
                balance += 1 if p.type == TokenType.LPAREN else -1
                if balance < 0: break

            if balance != 0:
                continue

            is_valid_for_rpn = True
            rpn_ready_tokens = []

            for t in tokens_in_line:
                if t.type.name in ("NEWLINE", "EOF"):
                    continue

                if t.type in (TokenType.NUM, TokenType.LPAREN, TokenType.RPAREN) or t.type in self.precedence:
                    rpn_ready_tokens.append(t)
                else:
                    is_valid_for_rpn = False
                    break

            if is_valid_for_rpn and any(tk.type == TokenType.NUM for tk in rpn_ready_tokens):
                rpn_list = self._build_rpn(rpn_ready_tokens)

                answer = self._evaluate(rpn_list)

                if answer is not None:
                    self.results.append({
                        "expression": " ".join(rpn_list),
                        "result": str(answer)
                    })

    def _evaluate(self, rpn_list):
        stack = []
        try:
            for item in rpn_list:
                # Проверка на число (включая отрицательные и дробные)
                if self._is_number(item):
                    stack.append(float(item))
                else:
                    if len(stack) < 2:
                        return None
                    b, a = stack.pop(), stack.pop()

                    if item == '+':
                        stack.append(a + b)
                    elif item == '-':
                        stack.append(a - b)
                    elif item == '*':
                        stack.append(a * b)
                    elif item == '/':
                        # Используем обычное деление / вместо целочисленного //
                        stack.append(a / b if b != 0 else 0.0)
                    elif item == '%':
                        stack.append(a % b if b != 0 else 0.0)

            if len(stack) == 1:
                # Округляем до 2 знаков после запятой
                res = round(stack[0], 2)
                # Если число целое (напр. 5.0), убираем лишнюю точку при выводе
                return int(res) if res % 1 == 0 else res

            return None
        except Exception:
            return None

    def _is_number(self, s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    def _build_rpn(self, tokens):
        stack = []
        output = []
        for token in tokens:
            if token.type == TokenType.NUM:
                output.append(token.value)
            elif token.type == TokenType.LPAREN:
                stack.append(token)
            elif token.type == TokenType.RPAREN:
                while stack and stack[-1].type != TokenType.LPAREN:
                    output.append(stack.pop().value)
                if stack: stack.pop()
            elif token.type in self.precedence:
                while (stack and stack[-1].type in self.precedence and
                       self.precedence[stack[-1].type] >= self.precedence[token.type]):
                    output.append(stack.pop().value)
                stack.append(token)
        while stack:
            output.append(stack.pop().value)
        return output

