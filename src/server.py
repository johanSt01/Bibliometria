from flask import Flask, render_template, request, url_for
from app import EstadisticasDescriptivas
from Util.BibFileUtil import BibFileUtil

app = Flask(__name__, static_folder='Style')

# Ruta principal
@app.route('/', methods=['GET', 'POST'])
def index():
    imagen_histograma = None
    stats = None

    # Configuración de ruta y archivos
    ruta = "./Util/outputFile/"  # Cambiado para usar ruta relativa desde src
    archivo_entrada = ruta + "referencias_ordenadas_GnomeSort_year.bib"
    
    if request.method == 'POST':
        # Si el usuario selecciona "Año", calculamos las estadísticas y generamos el histograma
        campo = request.form.get("campo")
        if campo == "year":
            # Se cargan las entradas de los datos de la base de datos
            entradas = BibFileUtil.leer_archivo_bib(archivo_entrada)
            
            # Calcular estadísticas
            stats = EstadisticasDescriptivas.calcular_estadisticas_anio(entradas, campo)

            # Generar y obtener la ruta del histograma
            imagen_histograma = EstadisticasDescriptivas.generar_histograma(stats, campo)

        if campo == "author":
            # Se cargan las entradas de los datos de la base de datos
            entradas = BibFileUtil.leer_archivo_bib(archivo_entrada)
            
            # Calcular estadísticas
            stats = EstadisticasDescriptivas.calcular_estadisticas_max15(entradas, campo)
            
            # Generar y obtener la ruta del histograma
            imagen_histograma = EstadisticasDescriptivas.generar_histograma(stats, campo)

        if campo in ["ENTRYTYPE", "source"]:
            # Se cargan las entradas de los datos de la base de datos
            entradas = BibFileUtil.leer_archivo_bib(archivo_entrada)
            
            # Calcular estadísticas
            stats = EstadisticasDescriptivas.calcular_estadisticas(entradas, campo)
            
            # Generar y obtener la ruta del histograma
            imagen_histograma = EstadisticasDescriptivas.generar_histograma(stats, campo)
        
        if campo in ["journal", "publisher"]:
            # Se cargan las entradas de los datos de la base de datos
            entradas = BibFileUtil.leer_archivo_bib(archivo_entrada, campo)
            
            # Calcular estadísticas
            stats = EstadisticasDescriptivas.calcular_estadisticas_max15(entradas, campo)
            
            # Generar y obtener la ruta del histograma
            imagen_histograma = EstadisticasDescriptivas.generar_histograma(stats, campo)

        if campo == "author - year":
             # Leer las entradas del archivo
            entradas = BibFileUtil.leer_archivo_bib(archivo_entrada)
            
            # Calcular las frecuencias de tipo de producto por año
            stats = EstadisticasDescriptivas.calcular_estadisticas_dos_campos(entradas, "author", "year")
            
            # Generar y obtener la ruta del histograma
            imagen_histograma = EstadisticasDescriptivas.generar_histograma(stats, "author - year")
        
    # Cargar la descripción de las categorias y variables con sus frecuencias 
    # Cargar categorías y sinónimos
    categorias = EstadisticasDescriptivas.cargar_datos("./Util/Categorias.csv")

    # Leer entradas de la base de datos y contar frecuencias
    entradas = BibFileUtil.leer_archivo_bib(archivo_entrada)
    frecuencias_categorias, frecuencias_variables = EstadisticasDescriptivas.contar_frecuencia_categorias(entradas, categorias)

    # Crear datos para la plantilla organizados por categorías
    datos_frecuencias = {
        categoria: {
            "total": total,
            "variables": frecuencias_variables[categoria]
        }
        for categoria, total in frecuencias_categorias.items()
    }

    # Cargar la nube de palabras
    nube_palabras = EstadisticasDescriptivas.generar_nube_palabras_base64(frecuencias_variables)

    return render_template('index.html', imagen_histograma=imagen_histograma, estadisticas=stats, datos_frecuencias=datos_frecuencias, nube_palabras=nube_palabras)

if __name__ == '__main__':
    app.run(debug=True)
