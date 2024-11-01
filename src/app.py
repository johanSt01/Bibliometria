import os
import sys
from collections import Counter
import statistics
import matplotlib.pyplot as plt
import re
import io
import base64

# Añadir el directorio actual al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Ordenamiento import GnomeSort
from Util.BibFileUtil import BibFileUtil

class EstadisticasDescriptivas:

    def limpiar_anio(valor_anio):
        """Elimina caracteres no numéricos de un valor de año."""
        return ''.join(filter(str.isdigit, valor_anio))
    
    def calcular_estadisticas_anio(entradas, campo):
        """
        Calcula estadísticas descriptivas para un campo específico del archivo BibTeX.            
        Returns:
            Diccionario con las estadísticas calculadas
        """
        try:
            # Extraer los valores numéricos del campo especificado
            valores = []
            for entrada in entradas:
                try:
                    # Limpiar el valor si el campo es 'year'
                    if campo == "year":
                        entrada.valor_orden = EstadisticasDescriptivas.limpiar_anio(entrada.valor_orden)
                    
                    # Intentar convertir el valor a número
                    valor = float(entrada.valor_orden) if '.' in entrada.valor_orden else int(entrada.valor_orden)
                    valores.append(valor)
                except (ValueError, TypeError):
                    print(f"Advertencia: No se pudo convertir el valor '{entrada.valor_orden}' a número.")
                    continue
            
            if not valores:
                raise ValueError(f"No se encontraron valores numéricos válidos para el campo '{campo}'")
            
            # Calcular estadísticas
            stats = {
                'cantidad': len(valores),
                #'media': statistics.mean(valores),
                'mediana': statistics.median(valores),
                'moda': statistics.mode(valores),
                'desviacion_estandar': statistics.stdev(valores) if len(valores) > 1 else 0,
                'varianza': statistics.variance(valores) if len(valores) > 1 else 0,
                'rango': max(valores) - min(valores),
                'minimo': min(valores),
                'maximo': max(valores)
            }
            
            # Calcular frecuencias
            frecuencias = Counter(valores)
            stats['frecuencias'] = dict(sorted(frecuencias.items()))
            
            return stats
            
        except Exception as e:
            print(f"Error al calcular estadísticas: {str(e)}")
            return None
    
    def autores_mas_frecuentes(entradas, campo, n_top=15):
        """
        Encuentra los autores más frecuentes en el primer puesto de autoría.
        Returns:
            Diccionario con los autores más frecuentes y sus respectivas frecuencias.
        """
        # Expresión regular para verificar que el nombre del autor no esté vacío o sea solo espacios
        regex_autor_valido = re.compile(r'\S')  # Busca al menos un carácter no blanco

        # Extraer el primer autor de cada entrada
        primeros_autores = []
        for entrada in entradas:
            try:
                # Dividir el campo 'author' para obtener solo el primer autor
                primer_autor = entrada.valor_orden.split(",")[0].strip()

                # Verificar que el primer autor no esté vacío usando la expresión regular
                if regex_autor_valido.search(primer_autor):
                    primeros_autores.append(primer_autor)
            except KeyError:
                print(f"Advertencia: El campo '{campo}' no está presente en una entrada.")
                continue
            except AttributeError:
                print(f"Advertencia: El campo '{campo}' no tiene el formato esperado en una entrada.")
                continue

        # Calcular la frecuencia de cada primer autor
        contador_autores = Counter(primeros_autores)
        
        # Seleccionar los 'n_top' autores más frecuentes
        autores_frecuentes = dict(contador_autores.most_common(n_top))

        return autores_frecuentes
    
    def calcular_estadisticas(entradas, campo="ENTRYTYPE"):
        """
        Calcula estadísticas descriptivas para el tipo de producto (ENTRYTYPE) u otro campo en un archivo BibTeX.
        
        Args:
            entradas: Lista de objetos EntradaBib con la información de cada entrada.
            campo: Indica si estamos calculando estadísticas para ENTRYTYPE o para valor_orden.
            
        Returns:
            Diccionario con las estadísticas calculadas para ENTRYTYPE o valor_orden.
        """
        try:
            # Condicional para decidir qué lista de valores usar
            if campo == "ENTRYTYPE":
                tipos_producto = [entrada.entry_type for entrada in entradas if entrada.entry_type]
            else:
                tipos_producto = [entrada.valor_orden for entrada in entradas if entrada.valor_orden]
            
            if not tipos_producto:
                raise ValueError(f"No se encontraron valores válidos para el campo '{campo}' en las entradas.")
            
            # Calcular frecuencias y moda
            frecuencias = Counter(tipos_producto)
            moda = frecuencias.most_common(1)[0] if frecuencias else None

            # Calcular la "mediana" como valor medio alfabético si es categórico
            tipos_ordenados = sorted(tipos_producto)
            mediana = tipos_ordenados[len(tipos_ordenados) // 2] if tipos_ordenados else None
            
            # Crear el diccionario de estadísticas
            stats = {
                'cantidad': len(tipos_producto),
                'frecuencias': dict(frecuencias),
                'moda': moda,
                'mediana': mediana
            }
            
            return stats
            
        except Exception as e:
            print(f"Error al calcular estadísticas: {str(e)}")
            return None
        
    def generar_histograma(stats, etiqueta_x, titulo):
        """
        Genera un histograma basado en las frecuencias de los datos y lo guarda como imagen en base 64.

        Args:
            stats (dict): Estadísticas descriptivas que incluyen las frecuencias.
            etiqueta_x (str): Etiqueta para el eje X.
            titulo (str): Título del histograma.
        """
        # Crear el histograma
        plt.figure(figsize=(10, 6))
        plt.bar(stats['frecuencias'].keys(), stats['frecuencias'].values(), color='skyblue')
        plt.xlabel(etiqueta_x)
        plt.ylabel('Frecuencia')
        plt.title(titulo)
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Guardar en un buffer en lugar de un archivo
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        plt.close()

        # Codificar en base64
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        
        # Devolver la imagen en base64
        return img_base64

def main():
    # Configuración de ruta y archivos
    ruta = "./Util/"  # Cambiado para usar ruta relativa desde src
    archivo_entrada = ruta + "filtradoPorDoi.bib"
    archivo_salida = ruta + "outputFile/referencias_ordenadas_GnomeSort_year.bib"

    # Asegurar que el directorio de salida existe
    os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)

    # Campo por el cual se va a ordenar
    campo_orden = "ENTRYTYPE"

    try:    
        # Leer las entradas desde el archivo BibTeX
        # entradas = BibFileUtil.leer_archivo_bib(archivo_entrada, campo_orden)
        salidas = BibFileUtil.leer_archivo_bib(archivo_salida, campo_orden)

        # Calcular estadísticas
        # stats = EstadisticasDescriptivas.calcular_estadisticas_anio(salidas, campo_orden)
        # EstadisticasDescriptivas.imprimir_estadisticas(stats, campo_orden)
        #EstadisticasDescriptivas.generar_histograma(stats)

        # Obtener los autores más frecuentes del primer puesto
        # autores_frecuentes = EstadisticasDescriptivas.autores_mas_frecuentes(salidas, campo_orden)
        # print("\nAutores más frecuentes en el primer puesto:")
        # for autor, frecuencia in autores_frecuentes.items():
        #     print(f"{autor}: {frecuencia} artículos")

        # Verificar que cada entrada tenga el ENTRYTYPE correcto
        # for entrada in salidas:
        #     print(f"ENTRYTYPE: {entrada.entry_type}, Clave: {entrada.clave}")
        tipo_producto = EstadisticasDescriptivas.calcular_estadisticas(salidas, campo_orden)
        print(tipo_producto)
        
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo de entrada: {archivo_entrada}")
    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")

if __name__ == "__main__":
    main()