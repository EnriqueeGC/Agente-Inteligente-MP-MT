import itertools
from tabulate import tabulate

# Obtener variables únicas
def get_variables(expression):
    return sorted(set(filter(str.isalpha, expression)))

# Tokenizar expresión lógica
def tokenize(expression):
    tokens = []
    i = 0
    while i < len(expression):
        c = expression[i]
        if c.isspace():
            i += 1
        elif c in '¬∧∨()':
            tokens.append(c)
            i += 1
        elif expression[i:i+1] == '→':
            tokens.append('→')
            i += 1
        elif expression[i:i+1] == '↔':
            tokens.append('↔')
            i += 1
        elif c.isalpha():
            tokens.append(c)
            i += 1
        else:
            raise ValueError(f"Caracter inválido: {c}")
    return tokens

# Precedencias y asociatividad
precedencia = {'¬': 4, '∧': 3, '∨': 2, '→': 1, '↔': 0}
asociatividad = {'¬': 'right', '∧': 'left', '∨': 'left', '→': 'right', '↔': 'right'}

# Convertir infijo a postfijo
def infix_to_postfix(tokens):
    output = []
    stack = []
    for token in tokens:
        if token.isalpha():
            output.append(token)
        elif token in precedencia:
            while (stack and stack[-1] != '(' and
                   ((asociatividad[token] == 'left' and precedencia[token] <= precedencia[stack[-1]]) or
                    (asociatividad[token] == 'right' and precedencia[token] < precedencia[stack[-1]]))):
                output.append(stack.pop())
            stack.append(token)
        elif token == '(':
            stack.append(token)
        elif token == ')':
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
    while stack:
        output.append(stack.pop())
    return output

# Evaluar postfijo con pasos
def eval_postfix_with_steps(postfix, values):
    stack = []
    steps = []
    for token in postfix:
        if token.isalpha():
            stack.append((token, values[token]))
        elif token == '¬':
            a_expr, a_val = stack.pop()
            expr = f'¬{a_expr}'
            val = not a_val
            stack.append((expr, val))
            steps.append((expr, val))
        elif token in {'∧', '∨', '→', '↔'}:
            b_expr, b_val = stack.pop()
            a_expr, a_val = stack.pop()
            expr = f'({a_expr} {token} {b_expr})'
            if token == '∧':
                val = a_val and b_val
            elif token == '∨':
                val = a_val or b_val
            elif token == '→':
                val = (not a_val) or b_val
            elif token == '↔':
                val = a_val == b_val
            stack.append((expr, val))
            steps.append((expr, val))
    return stack[0][1], steps

# Verificar tipo de expresión (tautología, contradicción, etc.)
def analizar_resultados(resultados):
    if all(resultados):
        return "✅ Tautología (siempre verdadera)"
    elif all(not r for r in resultados):
        return "❌ Contradicción (siempre falsa)"
    else:
        return "⚖️ Contingencia (verdadera en algunos casos)"

# Tabla de verdad principal
def truth_table(expression):
    tokens = tokenize(expression)
    postfix = infix_to_postfix(tokens)
    variables = get_variables(expression)

    # Obtener estructura de pasos (subexpresiones)
    _, example_steps = eval_postfix_with_steps(postfix, {v: True for v in variables})
    headers = variables + [expr for expr, _ in example_steps]
    headers = list(dict.fromkeys(headers))  # Eliminar duplicados

    # Combinaciones desde VVV hasta FFF
    combinations = list(itertools.product([True, False], repeat=len(variables)))

    table = []
    resultados_finales = []
    for values in combinations:
        val_dict = dict(zip(variables, values))
        final_result, steps = eval_postfix_with_steps(postfix, val_dict)
        resultados_finales.append(final_result)
        step_dict = {expr: val for expr, val in steps}
        row = []
        for header in headers:
            if header in val_dict:
                row.append('V' if val_dict[header] else 'F')
            elif header in step_dict:
                row.append('V' if step_dict[header] else 'F')
        table.append(row)

    print("\n📋 Tabla de verdad:\n")
    print(tabulate(table, headers=headers, tablefmt="grid"))

    conclusion = analizar_resultados(resultados_finales)
    print(f"\n🔍 Análisis lógico: {conclusion}\n")

# -----------------------------
# Ejemplo de uso:
#expr = "((p ∧ q) ∧ (q ∨ r)) → (p ∨ r)"
#truth_table(expr)
