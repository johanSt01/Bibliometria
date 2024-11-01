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
    ruta = "./Util/"  # Cambiado para usar ruta relativa desde src
    archivo_entrada = ruta + "filtradoPorDoi.bib"
    titulo = "Histograma de frecuencias"
    
    if request.method == 'POST':
        # Si el usuario selecciona "Año", calculamos las estadísticas y generamos el histograma
        campo = request.form.get("campo")
        if campo == "year":
            # Supón que tienes las entradas ya cargadas
            entradas = BibFileUtil.leer_archivo_bib(archivo_entrada, campo)
            
            # Calcular estadísticas
            stats = EstadisticasDescriptivas.calcular_estadisticas_anio(entradas, campo)

            # Generar y obtener la ruta del histograma
            imagen_histograma = EstadisticasDescriptivas.generar_histograma(stats, campo, titulo)

        if campo == "author":
            # Supón que tienes las entradas ya cargadas
            entradas = BibFileUtil.leer_archivo_bib(archivo_entrada, campo)
            
            # Calcular estadísticas
            stats = EstadisticasDescriptivas.autores_mas_frecuentes(entradas, campo)
            
            # Generar y obtener la ruta del histograma
            imagen_histograma = EstadisticasDescriptivas.generar_histograma({'frecuencias': stats}, campo, titulo)

    return render_template('index.html', imagen_histograma=imagen_histograma, estadisticas=stats)

if __name__ == '__main__':
    app.run(debug=True)
