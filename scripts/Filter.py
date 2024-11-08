import bibtexparser

# Función para leer el archivo .bib y almacenar las entradas
def leer_bibtex(ruta_archivo):
    with open(ruta_archivo, encoding='utf-8') as bibtex_file:
        bib_database = bibtexparser.load(bibtex_file)
    return bib_database.entries

# Función para filtrar entradas que tienen DOI
def filtrar_por_doi(entries):
    entradas_con_doi = [entry for entry in entries if 'doi' in entry]
    return entradas_con_doi

# Guardar los resultados filtrados en un archivo .bib
def guardar_bibtex(entradas, archivo_salida):
    bib_database = bibtexparser.bibdatabase.BibDatabase()
    bib_database.entries = entradas
    
    with open(archivo_salida, 'w', encoding='utf-8') as bibtex_file:
        writer = bibtexparser.bwriter.BibTexWriter()
        bibtex_file.write(writer.write(bib_database))

# Asegúrate de que la ruta al archivo es correcta
ruta_archivo_bib = '../Util/BaseDatos.bib'
archivo_salida = '../Util/filtradoPorDoi.bib'

# Leer el archivo unificado
try:
    entradas_unificadas = leer_bibtex(ruta_archivo_bib)
    # Filtrar las entradas que contienen DOI
    entradas_filtradas = filtrar_por_doi(entradas_unificadas)
    # Guardar el archivo filtrado por DOI
    guardar_bibtex(entradas_filtradas, archivo_salida)
    print(f'Se han guardado {len(entradas_filtradas)} entradas con DOI en el archivo "{archivo_salida}".')
except FileNotFoundError as e:
    print(f"Error: {e}")
