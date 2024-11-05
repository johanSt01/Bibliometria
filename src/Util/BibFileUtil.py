import re

class BibFileUtil:
    class EntradaBib:
        def __init__(self, entrada_completa, clave, entry_type, campos):
            self.entrada_completa = entrada_completa
            self.clave = clave
            self.entry_type = entry_type
            self.campos = campos  # Diccionario que contiene todos los campos de la entrada

    @staticmethod
    def leer_archivo_bib(nombre_archivo):
        entradas = []
        entrada_actual = []
        clave_actual = ""
        entry_type_actual = ""
        campos = {}
        dentro_de_entrada = False
        
        # Abrimos el archivo y recorremos cada línea
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                if linea.strip().startswith("@"):
                    # Almacenar la entrada anterior si ya estamos dentro de una entrada
                    if dentro_de_entrada:
                        entradas.append(BibFileUtil.EntradaBib("".join(entrada_actual), clave_actual, entry_type_actual, campos))
                        entrada_actual = []
                        clave_actual = ""
                        entry_type_actual = ""
                        campos = {}
                    
                    dentro_de_entrada = True
                    entrada_actual.append(linea)
                    
                    # Extraer ENTRYTYPE y clave de entrada BibTeX (p. ej., "@article{clave,")
                    patron_clave = re.compile(r"@(\w+)\{([^,]+),")
                    coincidencia_clave = patron_clave.search(linea)
                    if coincidencia_clave:
                        entry_type_actual = coincidencia_clave.group(1)  # ENTRYTYPE como article, inproceedings, etc.
                        clave_actual = coincidencia_clave.group(2)
                elif dentro_de_entrada:
                    entrada_actual.append(linea)
                    
                    # Buscar todos los pares clave-valor dentro de la entrada
                    patron_campo = re.compile(r"(\w+)\s*=\s*\{(.+?)\}")
                    coincidencia_campo = patron_campo.search(linea)
                    if coincidencia_campo:
                        campo = coincidencia_campo.group(1).lower()  # Convertimos a minúscula para uniformidad
                        valor = coincidencia_campo.group(2)
                        campos[campo] = valor
                    
                    # Final de la entrada (línea que contiene '}')
                    if linea.strip() == "}":
                        entradas.append(BibFileUtil.EntradaBib("".join(entrada_actual), clave_actual, entry_type_actual, campos))
                        entrada_actual = []
                        clave_actual = ""
                        entry_type_actual = ""
                        campos = {}
                        dentro_de_entrada = False
        
        return entradas
