""" 
import itertools
import threading
import re
from tabulate import tabulate  # Necesitarás instalar este paquete: pip install tabulate

# [Las funciones normalizar_frase, obtener_simbolo, procesar_frase, mostrar_diccionario, 
#  construir_inferencia e input_con_timeout permanecen igual que en el código anterior]
def normalizar_frase(frase):
    # Eliminar palabras de conexión iniciales y normalizar
    frase = re.sub(r'^(por lo tanto|además|entonces|sin embargo|por tanto)\s*', '', frase.strip())
    frase = re.sub(r'[.,;]$', '', frase)
    return frase.lower().strip()

def obtener_simbolo(frase, diccionario, letras, index):
    frase_normalizada = normalizar_frase(frase)
    
    # Verificar si ya existe una proposición similar
    for frase_existente, simbolo in diccionario.items():
        if frase_normalizada == normalizar_frase(frase_existente):
            return simbolo
        # Verificar si una está contenida en la otra (para partes de frases)
        if frase_normalizada in normalizar_frase(frase_existente) or normalizar_frase(frase_existente) in frase_normalizada:
            return simbolo
    
    # Si no existe, crear nueva entrada
    if frase_normalizada not in diccionario:
        diccionario[frase_normalizada] = letras[index[0]]
        index[0] += 1
    return diccionario[frase_normalizada]


def procesar_frase(frase, diccionario, letras, index):
    frase_original = frase.strip()
    if not frase_original:
        return ""
    
    frase = normalizar_frase(frase_original)

    # Manejar negaciones primero
    if frase.startswith("no "):
        simbolo = obtener_simbolo(frase[3:], diccionario, letras, index)
        return f"¬{simbolo}"

    # Conectores binarios
    conectores = [
        (" si y solo si ", " ↔ "),
        (" entonces ", " → "),
        (" y ", " ∧ "),
        (" o ", " ∨ ")
    ]
    
    for conector, simbolo_logico in conectores:
        if conector in frase:
            partes = [p.strip() for p in frase.split(conector)]
            if len(partes) == 2:
                izq = procesar_frase(partes[0], diccionario, letras, index)
                der = procesar_frase(partes[1], diccionario, letras, index)
                return f"({izq}{simbolo_logico}{der})"

    # Manejar implicaciones con comas
    if "," in frase:
        partes = [p.strip() for p in frase.split(",")]
        if len(partes) == 2:
            izq = procesar_frase(partes[0], diccionario, letras, index)
            der = procesar_frase(partes[1], diccionario, letras, index)
            return f"({izq} → {der})"

    return obtener_simbolo(frase_original, diccionario, letras, index)

def mostrar_diccionario(diccionario):
    print("\n=== Diccionario de proposiciones ===")
    # Ordenar por el símbolo (p, q, r, ...)
    for frase, simbolo in sorted(diccionario.items(), key=lambda item: item[1]):
        print(f"{simbolo}: {frase}")
        
def construir_inferencia(logica1, logica2, conclusion):
    if logica2:  # Si hay dos premisas
        return f"[{logica1} ∧ {logica2}] → {conclusion}"
    else:
        return f"{logica1} → {conclusion}"

def evaluar_expresion(expresion, valores):
    # Reemplazar símbolos por sus valores
    for simbolo, valor in valores.items():
        expresion = expresion.replace(simbolo, str(valor))
    
    # Evaluar operadores lógicos
    expresion = expresion.replace('¬', ' not ')
    expresion = expresion.replace('∧', ' and ')
    expresion = expresion.replace('∨', ' or ')
    expresion = expresion.replace('→', ' <= ')  # Implicación: p→q equivale a not p or q
    expresion = expresion.replace('↔', ' == ')  # Bicondicional
    
    try:
        return eval(expresion)
    except:
        return None

def generar_tabla_verdad(premisa1, premisa2, conclusion, diccionario):
    # Obtener todas las variables proposicionales únicas
    variables = sorted(set(diccionario.values()))
    n = len(variables)
    
    # Generar todas las combinaciones posibles de valores de verdad
    combinaciones = list(itertools.product([False, True], repeat=n))
    
    tabla = []
    encabezados = variables.copy()
    
    # Determinar qué premisas tenemos
    premisas = []
    if premisa1:
        premisas.append(premisa1)
        encabezados.append("Premisa 1")
    if premisa2:
        premisas.append(premisa2)
        encabezados.append("Premisa 2")
    encabezados.append("Conclusión")
    encabezados.append("Argumento Válido")
    
    for combinacion in combinaciones:
        fila = list(combinacion)
        valores = dict(zip(variables, combinacion))
        
        # Evaluar premisas
        eval_premisas = []
        valido = True
        
        for premisa in premisas:
            eval_p = evaluar_expresion(premisa, valores)
            eval_premisas.append(eval_p)
            fila.append(eval_p)
            if eval_p is False:
                valido = False
        
        # Evaluar conclusión
        eval_conclusion = evaluar_expresion(conclusion, valores)
        fila.append(eval_conclusion)
        
        # Un argumento es válido si todas las premisas verdaderas llevan a conclusión verdadera
        if valido and eval_conclusion is False:
            valido = False
        
        fila.append(valido)
        tabla.append(fila)
    
    return encabezados, tabla

def input_con_timeout(prompt, timeout=15):
    result = [None]

    def target():
        try:
            result[0] = input(prompt)
        except:
            result[0] = ""

    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        print("\n(Tiempo agotado. Continuando sin segunda premisa...)")
        return ""
    return result[0]

def main():
    letras = list("pqrstuvwxyzabcdefghijklmno")
    diccionario = {}
    index = [0]

    print("=== Traductor de frases naturales a lógica proposicional ===")
    premisa1 = input("Ingrese la primera premisa: ").strip()
    premisa2 = input_con_timeout("Ingrese la segunda premisa (opcional, tienes 15 segundos): ").strip()
    conclusion = input("Ingrese la conclusión: ").strip()

    # Procesar todas las frases con el mismo diccionario
    logica1 = procesar_frase(premisa1, diccionario, letras, index)
    logica2 = procesar_frase(premisa2, diccionario, letras, index) if premisa2 else None
    logica_conclusion = procesar_frase(conclusion, diccionario, letras, index)

    print("\n=== Traducción lógica ===")
    print(f"Premisa 1: {logica1}")
    if logica2:
        print(f"Premisa 2: {logica2}")
    print(f"Conclusión: {logica_conclusion}")

    print("\n=== Forma lógica sugerida para inferencia ===")
    formula = construir_inferencia(logica1, logica2, logica_conclusion)
    print(formula)

    mostrar_diccionario(diccionario)
    
    # Generar y mostrar tabla de verdad
    print("\n=== Tabla de Verdad ===")
    encabezados, tabla = generar_tabla_verdad(logica1, logica2, logica_conclusion, diccionario)
    
    # Convertir valores booleanos a "V" (True) y "F" (False)
    tabla_formateada = []
    for fila in tabla:
        fila_formateada = ["V" if x else "F" for x in fila]
        tabla_formateada.append(fila_formateada)
    
    print(tabulate(tabla_formateada, headers=encabezados, tablefmt="grid"))
    
    # Determinar validez del argumento
    argumento_valido = all(fila[-1] for fila in tabla)
    print("\n=== Resultado de Validez ===")
    if argumento_valido:
        print("El argumento es VÁLIDO (todas las premisas verdaderas llevan a conclusión verdadera)")
    else:
        print("El argumento es INVÁLIDO (existen casos donde premisas verdaderas llevan a conclusión falsa)")

if __name__ == "__main__":
    main() """
    
import itertools
import threading
import re
from tabulate import tabulate

def normalizar_frase(frase):
    frase = re.sub(r'^(por lo tanto|además|entonces|sin embargo|por tanto)\s*', '', frase.strip())
    frase = re.sub(r'[.,;]$', '', frase)
    return frase.lower().strip()

def obtener_simbolo(frase, diccionario, letras, index):
    frase_normalizada = normalizar_frase(frase)
    
    for frase_existente, simbolo in diccionario.items():
        if frase_normalizada == normalizar_frase(frase_existente):
            return simbolo
        if frase_normalizada in normalizar_frase(frase_existente) or normalizar_frase(frase_existente) in frase_normalizada:
            return simbolo
    
    if frase_normalizada not in diccionario:
        diccionario[frase_normalizada] = letras[index[0]]
        index[0] += 1
    return diccionario[frase_normalizada]

def procesar_frase(frase, diccionario, letras, index):
    frase_original = frase.strip()
    if not frase_original:
        return ""
    
    frase = normalizar_frase(frase_original)

    if frase.startswith("no "):
        simbolo = obtener_simbolo(frase[3:], diccionario, letras, index)
        return f"¬{simbolo}"

    conectores = [
        (" si y solo si ", " ↔ "),
        (" entonces ", " → "),
        (" y ", " ∧ "),
        (" o ", " ∨ ")
    ]
    
    for conector, simbolo_logico in conectores:
        if conector in frase:
            partes = [p.strip() for p in frase.split(conector)]
            if len(partes) == 2:
                izq = procesar_frase(partes[0], diccionario, letras, index)
                der = procesar_frase(partes[1], diccionario, letras, index)
                return f"({izq}{simbolo_logico}{der})"

    if "," in frase:
        partes = [p.strip() for p in frase.split(",")]
        if len(partes) == 2:
            izq = procesar_frase(partes[0], diccionario, letras, index)
            der = procesar_frase(partes[1], diccionario, letras, index)
            return f"({izq} → {der})"

    return obtener_simbolo(frase_original, diccionario, letras, index)

def mostrar_diccionario(diccionario):
    print("\n=== Diccionario de proposiciones ===")
    for frase, simbolo in sorted(diccionario.items(), key=lambda item: item[1]):
        print(f"{simbolo}: {frase}")

def construir_inferencia(logica1, logica2, conclusion):
    if logica2:
        return f"({logica1} ∧ {logica2}) → {conclusion}"
    else:
        return f"{logica1} → {conclusion}"

def input_con_timeout(prompt, timeout=15):
    result = [None]
    def target():
        try:
            result[0] = input(prompt)
        except:
            result[0] = ""
    thread = threading.Thread(target=target)
    thread.start()
    thread.join(timeout)
    if thread.is_alive():
        print("\n(Tiempo agotado. Continuando sin segunda premisa...)")
        return ""
    return result[0]

def evaluar_expresion(expresion, valores):
    # Crear copia para no modificar el original
    expr = expresion
    
    # Reemplazar negaciones primero
    for simbolo in valores:
        expr = expr.replace(f"¬{simbolo}", f" not {valores[simbolo]}")
    
    # Reemplazar símbolos por sus valores
    for simbolo, valor in valores.items():
        expr = expr.replace(simbolo, str(valor))
    
    # Reemplazar operadores lógicos
    expr = expr.replace('∧', ' and ')
    expr = expr.replace('∨', ' or ')
    expr = expr.replace('→', ' <= ')  # Implicación
    expr = expr.replace('↔', ' == ')  # Bicondicional
    
    try:
        return eval(expr)
    except:
        return None

def generar_tabla_verdad(premisa1, premisa2, conclusion, forma_logica, diccionario):
    variables = sorted(set(diccionario.values()))
    n = len(variables)
    
    # Generar combinaciones en orden inverso para empezar con True
    combinaciones = list(itertools.product([True, False], repeat=n))
    
    tabla = []
    encabezados = variables.copy()
    
    premisas = []
    if premisa1:
        premisas.append(premisa1)
        encabezados.append("Premisa 1")
    if premisa2:
        premisas.append(premisa2)
        encabezados.append("Premisa 2")
    encabezados.append("Conclusión")
    encabezados.append("Forma Lógica")
    encabezados.append("Argumento Válido")
    
    for combinacion in combinaciones:
        fila = list(combinacion)
        valores = dict(zip(variables, combinacion))
        
        # Evaluar premisas
        eval_premisas = []
        premisas_verdaderas = True
        
        for premisa in premisas:
            eval_p = evaluar_expresion(premisa, valores)
            eval_premisas.append(eval_p)
            fila.append(eval_p)
            if eval_p is False:
                premisas_verdaderas = False
        
        # Evaluar conclusión
        eval_conclusion = evaluar_expresion(conclusion, valores)
        fila.append(eval_conclusion)
        
        # Evaluar forma lógica completa
        eval_forma_logica = evaluar_expresion(forma_logica, valores)
        fila.append(eval_forma_logica)
        
        # Un argumento es válido si cuando todas las premisas son verdaderas, la conclusión también lo es
        valido = not (premisas_verdaderas and not eval_conclusion)
        fila.append(valido)
        
        tabla.append(fila)
    
    return encabezados, tabla

def main():
    letras = list("pqrstuvwxyzabcdefghijklmno")
    diccionario = {}
    index = [0]

    print("=== Traductor de frases naturales a lógica proposicional ===")
    premisa1 = input("Ingrese la primera premisa: ").strip()
    premisa2 = input_con_timeout("Ingrese la segunda premisa (opcional, tienes 15 segundos): ").strip()
    conclusion = input("Ingrese la conclusión: ").strip()

    logica1 = procesar_frase(premisa1, diccionario, letras, index)
    logica2 = procesar_frase(premisa2, diccionario, letras, index) if premisa2 else None
    logica_conclusion = procesar_frase(conclusion, diccionario, letras, index)
    forma_logica = construir_inferencia(logica1, logica2, logica_conclusion)

    print("\n=== Traducción lógica ===")
    print(f"Premisa 1: {logica1}")
    if logica2:
        print(f"Premisa 2: {logica2}")
    print(f"Conclusión: {logica_conclusion}")

    print("\n=== Forma lógica sugerida para inferencia ===")
    print(forma_logica)

    mostrar_diccionario(diccionario)
    
    print("\n=== Tabla de Verdad ===")
    encabezados, tabla = generar_tabla_verdad(logica1, logica2, logica_conclusion, forma_logica, diccionario)
    
    # Convertir valores booleanos a "V" (True) y "F" (False) y ajustar orden
    tabla_formateada = []
    for fila in tabla:
        fila_formateada = ["V" if x else "F" for x in fila]
        tabla_formateada.append(fila_formateada)
    
    print(tabulate(tabla_formateada, headers=encabezados, tablefmt="grid"))
    
    # Determinar validez del argumento
    argumento_valido = all(fila[-1] for fila in tabla)
    print("\n=== Resultado de Validez ===")
    if argumento_valido:
        print("El argumento es VÁLIDO (en todos los casos donde las premisas son verdaderas, la conclusión también lo es)")
    else:
        casos_invalidos = sum(1 for fila in tabla if fila[-3] and not fila[-4])  # Premisas verdaderas pero conclusión falsa
        print(f"El argumento es INVÁLIDO (existen {casos_invalidos} caso(s) donde premisas verdaderas llevan a conclusión falsa)")

if __name__ == "__main__":
    main()