import os
import sys

# Añadir el directorio actual al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Ordenamiento import GnomeSort
from BibFileUtil import BibFileUtil


def main():
    # Configuración de ruta y archivos
    ruta = "../Util/"  # Cambiado para usar ruta relativa desde src
    archivo_entrada = ruta + "filtradoPorDoi.bib"
    archivo_salida = ruta + "outputFile/referencias_ordenadas_GnomeSort_year.bib"

    # Asegurar que el directorio de salida existe
    os.makedirs(os.path.dirname(archivo_salida), exist_ok=True)

    # Campo por el cual se va a ordenar
    campo_orden = "year"

    try:
        # Leer las entradas desde el archivo BibTeX
        entradas = BibFileUtil.leer_archivo_bib(archivo_entrada, campo_orden)

        # Ordenar las entradas usando GnomeSort
        GnomeSort.gnome_sort(entradas)

        # Escribir las entradas ordenadas en el archivo de salida
        BibFileUtil.escribir_entradas_ordenadas(entradas, archivo_salida)
        
        print(f"Archivo ordenado guardado exitosamente en: {archivo_salida}")
        
    except FileNotFoundError:
        print(f"Error: No se pudo encontrar el archivo de entrada: {archivo_entrada}")
    except Exception as e:
        print(f"Error durante la ejecución: {str(e)}")

if __name__ == "__main__":
    main()