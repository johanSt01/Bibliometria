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
        
        Args:
            entradas: Lista de entradas BibTeX
            campo: Campo a analizar (ejemplo: 'year')
            
        Returns:
            dict: Diccionario con las estadísticas calculadas
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

        Args:
            entradas: Lista de entradas BibTeX
            campo: Campo en el cual buscar los autores (por defecto, 'author')
            n_top: Número de autores más frecuentes a mostrar
            
        Returns:
            dict: Diccionario con los autores más frecuentes y sus respectivas frecuencias.
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
    
    # def generar_histograma(stats, nombre_archivo="histograma_frecuencias.png"):
    #     """
    #     Genera un histograma basado en las frecuencias de los años y lo guarda como imagen.

    #     Args:
    #         stats (dict): Estadísticas descriptivas que incluyen las frecuencias.
    #         nombre_archivo (str): Nombre del archivo de imagen de salida.
    #     """
    #     # Crear el histograma
    #     plt.figure(figsize=(10, 6))
    #     plt.bar(stats['frecuencias'].keys(), stats['frecuencias'].values(), color='skyblue')
    #     plt.xlabel('Año')
    #     plt.ylabel('Frecuencia')
    #     plt.title('Frecuencia de registros por año')
    #     plt.grid(axis='y', linestyle='--', alpha=0.7)

    #     # Guardar la imagen en la carpeta Style
    #     ruta_salida = os.path.join("Style", nombre_archivo)
    #     plt.savefig(ruta_salida)
    #     plt.close()

    #     return ruta_salida


def main():
    # Configuración de ruta y archivos
    ruta = "./Util/"  # Cambiado para usar ruta relativa desde src
    archivo_entrada = ruta + "filtradoPorDoi.bib"
    archivo_salida = ruta + "outputFile/referencias_ordenadas_GnomeSort_year.bib"

    # Asegurar que el directorio de salida existe
    os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)

    # Campo por el cual se va a ordenar
    campo_orden = "author"

    try:    
        # Leer las entradas desde el archivo BibTeX
        # entradas = BibFileUtil.leer_archivo_bib(archivo_entrada, campo_orden)

        salidas = BibFileUtil.leer_archivo_bib(archivo_salida, campo_orden)

        # Calcular estadísticas
        # stats = EstadisticasDescriptivas.calcular_estadisticas_anio(salidas, campo_orden)
        # EstadisticasDescriptivas.imprimir_estadisticas(stats, campo_orden)
        #EstadisticasDescriptivas.generar_histograma(stats)

        # Obtener los autores más frecuentes del primer puesto
        autores_frecuentes = EstadisticasDescriptivas.autores_mas_frecuentes(salidas, campo_orden)
        print("\nAutores más frecuentes en el primer puesto:")
        for autor, frecuencia in autores_frecuentes.items():
            print(f"{autor}: {frecuencia} artículos")

        stats_autores = EstadisticasDescriptivas.autores_mas_frecuentes(salidas, campo_orden)
        EstadisticasDescriptivas.generar_histograma(
            {'frecuencias': stats_autores}, 
            campo_orden, 
            titulo="Frecuencia de los primeros autores más frecuentes"
        )



        # Ordenar las entradas usando GnomeSort
        #GnomeSort.gnome_sort(entradas)

        # Escribir las entradas ordenadas en el archivo de salida
        #BibFileUtil.escribir_entradas_ordenadas(entradas, archivo_salida)
        
        #print(f"\nArchivo ordenado guardado exitosamente en: {archivo_salida}")
        
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo de entrada: {archivo_entrada}")
    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")

if __name__ == "__main__":
    main()