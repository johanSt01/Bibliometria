import re

class BibFileUtil:
    class EntradaBib:
        def __init__(self, entrada_completa, clave, valor_orden):
            self.entrada_completa = entrada_completa
            self.clave = clave
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
        Lee un archivo BibTeX y extrae sus entradas.
        
        Args:
            nombre_archivo: Ruta del archivo BibTeX a leer
            campo_orden: Campo por el cual se ordenarán las entradas
            
        Returns:
            Lista de objetos EntradaBib
        """
        conteo_entradas = 0
        
        # Primera pasada: contar el número de entradas en el archivo
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                if linea.strip().startswith("@"):
                    conteo_entradas += 1
        
        entradas = []
        entrada_actual = []
        clave_actual = ""
        valor_orden_actual = ""
        dentro_de_entrada = False
        
        # Segunda pasada: leer y almacenar las entradas
        with open(nombre_archivo, 'r', encoding='utf-8') as archivo:
            for linea in archivo:
                if linea.strip().startswith("@"):
                    # Si ya estamos dentro de una entrada, almacenar la anterior
                    if dentro_de_entrada:
                        entradas.append(BibFileUtil.EntradaBib("".join(entrada_actual), clave_actual, valor_orden_actual))
                        entrada_actual = []
                        clave_actual = ""
                        valor_orden_actual = ""
                    
                    dentro_de_entrada = True
                    entrada_actual.append(linea)
                    
                    # Extraer la clave de la entrada BibTeX (p. ej., "@article{clave,")
                    patron_clave = re.compile(r"@\w+\{([^,]+),")
                    coincidencia_clave = patron_clave.search(linea)
                    if coincidencia_clave:
                        clave_actual = coincidencia_clave.group(1)
                elif dentro_de_entrada:
                    entrada_actual.append(linea)
                    
                    # Buscar el valor del campo para ordenar si aún no ha sido encontrado
                    if not valor_orden_actual and linea.strip().lower().startswith(campo_orden.lower()):
                        patron_valor = re.compile(rf"{campo_orden}\s*=\s*\{{([^}}]+)\}}")
                        coincidencia_valor = patron_valor.search(linea)
                        if coincidencia_valor:
                            valor_orden_actual = coincidencia_valor.group(1)
                    
                    # Si encontramos el final de la entrada (la línea con '}')
                    if linea.strip() == "}":
                        entradas.append(BibFileUtil.EntradaBib("".join(entrada_actual), clave_actual, valor_orden_actual))
                        entrada_actual = []
                        clave_actual = ""
                        valor_orden_actual = ""
                        dentro_de_entrada = False
        
        # print(f"Número de archivos: {conteo_entradas}")
        return entradas