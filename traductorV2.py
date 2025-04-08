import itertools
import threading
import re
from tabulate import tabulate
import tablaDeVerdad

def normalizar_frase(frase):
    frase = re.sub(r'^(por lo tanto|además|entonces|sin embargo|por tanto)\s*', '', frase.strip()) # Eliminar conectores al inicio
    frase = re.sub(r'[.,;]$', '', frase) # Eliminar puntuación al final
    return frase.lower().strip() # Normalizar a minúsculas y quitar espacios

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
 
def reglas_mp_mt():
    print("\n=== Reglas de Inferencia ===")
    print("1. Modus Ponens: Si p → q y p, entonces q.")
    print("2. Modus Tollens: Si p → q y ¬q, entonces ¬p.")
    print("3. Salir")

    while True:
        opcion = input("Seleccione una opción (1-3): ")
        if opcion == '1':
            print("Modus Ponens: Si p → q y p, entonces q.")
        elif opcion == '2':
            print("Modus Tollens: Si p → q y ¬q, entonces ¬p.")
        elif opcion == '3':
            break
        else:
            print("Opción no válida. Intente nuevamente.")    

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
    print("\n=== Tabla de verdad ===")
    
    tablaDeVerdad.truth_table(str(forma_logica))
    

if __name__ == "__main__":
    main()

