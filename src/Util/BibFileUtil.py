import re

class BibFileUtil:
    class EntradaBib:
        def __init__(self, entrada_completa, clave, entry_type, valor_orden):
            self.entrada_completa = entrada_completa
            self.clave = clave
            self.entry_type = entry_type 
            self.valor_orden = valor_orden
    
    def escribir_entradas_ordenadas(entradas, archivo_salida):
        """
        Escribe las entradas ordenadas en un archivo de salida.
        
        Args:
            entradas: Lista de objetos EntradaBib
            archivo_salida: Ruta del archivo de salida
        """
        with open(archivo_salida, 'w', encoding='utf-8') as escritor:
            for entrada in entradas:
                escritor.write(entrada.entrada_completa)
                escritor.write("\n")
    
    def leer_archivo_bib(nombre_archivo, campo_orden):
        """
        Lee un archivo BibTeX y extrae sus entradas, incluyendo ENTRYTYPE.
        
        Args:
            nombre_archivo: Ruta del archivo BibTeX a leer
            campo_orden: Campo por el cual se ordenarán las entradas
            
        Returns:
            Lista de objetos EntradaBib
        """
        entradas = []
        entrada_actual = []
        clave_actual = ""
        entry_type_actual = ""
        valor_orden_actual = ""
        dentro_de_entrada = False
        
        # Abrimos el archivo y recorremos cada línea
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                if linea.strip().startswith("@"):
                    # Almacenar la entrada anterior si ya estamos dentro de una entrada
                    if dentro_de_entrada:
                        entradas.append(BibFileUtil.EntradaBib("".join(entrada_actual), clave_actual, entry_type_actual, valor_orden_actual))
                        entrada_actual = []
                        clave_actual = ""
                        entry_type_actual = ""
                        valor_orden_actual = ""
                    
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
                    
                    # Buscar el valor del campo para ordenar, si existe
                    if not valor_orden_actual and linea.strip().lower().startswith(campo_orden.lower()):
                        patron_valor = re.compile(rf"{campo_orden}\s*=\s*\{{([^}}]+)\}}")
                        coincidencia_valor = patron_valor.search(linea)
                        if coincidencia_valor:
                            valor_orden_actual = coincidencia_valor.group(1)
                    
                    # Final de la entrada (línea que contiene '}')
                    if linea.strip() == "}":
                        entradas.append(BibFileUtil.EntradaBib("".join(entrada_actual), clave_actual, entry_type_actual, valor_orden_actual))
                        entrada_actual = []
                        clave_actual = ""
                        entry_type_actual = ""
                        valor_orden_actual = ""
                        dentro_de_entrada = False
        
        return entradas
