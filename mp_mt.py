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
