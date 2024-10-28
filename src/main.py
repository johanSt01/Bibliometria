import os
import sys
from collections import Counter
import statistics

# Añadir el directorio actual al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Ordenamiento import GnomeSort
from Util.BibFileUtil import BibFileUtil

class EstadisticasDescriptivas:

    def limpiar_anio(valor_anio):
        """Elimina caracteres no numéricos de un valor de año."""
        return ''.join(filter(str.isdigit, valor_anio))
    
    def calcular_estadisticas(entradas, campo):
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

def imprimir_estadisticas(stats, campo):
    """Imprime las estadísticas de manera formateada"""
    if stats:
        print(f"\nEstadísticas descriptivas para el campo '{campo}':")
        print(f"Cantidad de valores: {stats['cantidad']}")
        #print(f"Media: {stats['media']:.2f}")
        print(f"Mediana: {stats['mediana']}")
        print(f"Moda: {stats['moda']}")
        print(f"Desviación estándar: {stats['desviacion_estandar']:.2f}")
        print(f"Varianza: {stats['varianza']:.2f}")
        print(f"Rango: {stats['rango']}")
        print(f"Valor mínimo: {stats['minimo']}")
        print(f"Valor máximo: {stats['maximo']}")
        
        print("\nFrecuencias:")
        for valor, frecuencia in stats['frecuencias'].items():
            print(f"{valor}: {frecuencia} ocurrencias")

def main():
    # Configuración de ruta y archivos
    ruta = "./Util/"  # Cambiado para usar ruta relativa desde src
    archivo_entrada = ruta + "filtradoPorDoi.bib"
    archivo_salida = ruta + "outputFile/referencias_ordenadas_GnomeSort_year.bib"

    # Asegurar que el directorio de salida existe
    os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)

    # Campo por el cual se va a ordenar
    campo_orden = "year"

    try:
        # Leer las entradas desde el archivo BibTeX
        entradas = BibFileUtil.leer_archivo_bib(archivo_entrada, campo_orden)

        salidas = BibFileUtil.leer_archivo_bib(archivo_salida, campo_orden)

        # Calcular estadísticas
        stats = EstadisticasDescriptivas.calcular_estadisticas(salidas, campo_orden)
        imprimir_estadisticas(stats, campo_orden)

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