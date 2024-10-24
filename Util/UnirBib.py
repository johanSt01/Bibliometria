import bibtexparser
import os
import glob

# Función para cargar y unir archivos .bib
def unir_archivos_bib(directorio, archivo_salida):
    entradas_totales = []
    
    # Buscar todos los archivos .bib en la carpeta
    archivos_bib = glob.glob(os.path.join(directorio, '*.bib'))

    for archivo in archivos_bib:
        with open(archivo, 'r', encoding='utf-8') as bibtex_file:  # Agregar encoding utf-8
            parser = bibtexparser.bparser.BibTexParser(common_strings=True)
            bib_database = bibtexparser.load(bibtex_file, parser=parser)
            entradas_totales.extend(bib_database.entries)

    # Crear el nuevo archivo unificado
    with open(archivo_salida, 'w', encoding='utf-8') as bibtex_output_file:  # Guardar también en utf-8
        bib_database_merged = bibtexparser.bibdatabase.BibDatabase()
        bib_database_merged.entries = entradas_totales
        bibtexparser.dump(bib_database_merged, bibtex_output_file)

    print(f'Archivos unidos en: {archivo_salida}')


# Directorio donde están los archivos .bib
directorio_bib = '../Bases de datos separadas'

# Archivo de salida
archivo_unido = 'BaseDatos.bib'

# Llamada a la función
unir_archivos_bib(directorio_bib, archivo_unido)
