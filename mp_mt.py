import re

def normalizar(frase):
    frase = frase.strip().lower()
    frase = re.sub(r'[.,;]$', '', frase)
    frase = re.sub(r'^(si\s+)?', '', frase)  # quitar 'si' inicial para análisis más limpio
    return frase.strip()

def extraer_partes_condicional(frase):
    frase = normalizar(frase)
    match = re.search(r'entonces', frase)
    if not match:
        return None, None
    partes = frase.split("entonces")
    antecedente = partes[0].strip()
    consecuente = partes[1].strip()
    return antecedente, consecuente

def aplicar_modus_ponens(premisa1, premisa2):
    antecedente, consecuente = extraer_partes_condicional(premisa1)
    premisa2_normalizada = normalizar(premisa2)
    
    if antecedente and premisa2_normalizada in antecedente:
        return consecuente
    return None

def aplicar_modus_tollens(premisa1, premisa2):
    antecedente, consecuente = extraer_partes_condicional(premisa1)
    premisa2_normalizada = normalizar(premisa2)
    
    if consecuente and ("no " + consecuente) in premisa2_normalizada:
        return "No " + antecedente
    return None

def main():
    print("=== Inferencia con Modus Ponens o Tollens ===")
    print("1. Modus Ponens")
    print("2. Modus Tollens")
    opcion = input("Selecciona una opción (1 o 2): ").strip()
    
    premisa1 = input("Ingresa la primera premisa (condicional): ")
    premisa2 = input("Ingresa la segunda premisa: ")

    if opcion == "1":
        conclusion = aplicar_modus_ponens(premisa1, premisa2)
    elif opcion == "2":
        conclusion = aplicar_modus_tollens(premisa1, premisa2)
    else:
        print("Opción inválida.")
        return

    if conclusion:
        print(f"\n>>> Conclusión inferida: {conclusion}")
    else:
        print("\n>>> No se pudo inferir una conclusión con las premisas dadas.")

if __name__ == "__main__":
    main()
