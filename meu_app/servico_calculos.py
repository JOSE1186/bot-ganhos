def tentar_converter_para_float(texto):
    try:
        texto_limpo = texto.strip().replace(",", ".")
        return float(texto_limpo)
    except:
        return None
