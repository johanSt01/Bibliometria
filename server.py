from flask import Flask, render_template, request
from app import EstadisticasDescriptivas
from Util.BibFileUtil import BibFileUtil

app = Flask(__name__, static_folder='Style')

# Configuración de archivo y datos preprocesados
ruta = "./Util/outputFile/"
archivo_entrada = ruta + "referencias_ordenadas_GnomeSort_year.bib"

# Cargar los datos de frecuencias y la nube de palabras una vez
categorias = EstadisticasDescriptivas.cargar_datos("./Util/Categorias.csv")
entradas = BibFileUtil.leer_archivo_bib(archivo_entrada)

frecuencias_categorias, frecuencias_variables = EstadisticasDescriptivas.contar_frecuencia_categorias(entradas, categorias)

# Generar los datos de frecuencias por categorías
datos_frecuencias = {
    categoria: {
        "total": total,
        "variables": frecuencias_variables[categoria]
    }
    for categoria, total in frecuencias_categorias.items()
}

# Generar la nube de palabras una vez
nube_palabras = EstadisticasDescriptivas.generar_nube_palabras_base64(frecuencias_variables)

#Cargar los datos del grafo
journal_data = EstadisticasDescriptivas.identificar_journals_mas_publicados(entradas)

# Generar el grafo en formato base64
img_grafo_base64 = EstadisticasDescriptivas.generar_grafo_journals(journal_data)

# Ruta principal
@app.route('/', methods=['GET', 'POST'])
def index():
    imagen_histograma = None
    imagen_histograma_dos_variables = None
    stats = None
    stats_dos_variables = None
    error_mensaje = None

    if request.method == 'POST':
        # Obtener los valores del formulario
        campo = request.form.get("campo", "").strip()
        campo1 = request.form.get("campo1", "").strip()
        campo2 = request.form.get("campo2", "").strip()

        # Procesar si solo una variable fue seleccionada
        if campo:
            try:
                # Procesar estadísticas para una sola variable
                if campo == "year":
                    stats = EstadisticasDescriptivas.calcular_estadisticas_anio(entradas, campo)
                elif campo == "author":
                    stats = EstadisticasDescriptivas.calcular_estadisticas_max15(entradas, campo)
                elif campo in ["ENTRYTYPE", "source"]:
                    stats = EstadisticasDescriptivas.calcular_estadisticas(entradas, campo)
                elif campo in ["journal", "publisher"]:
                    stats = EstadisticasDescriptivas.calcular_estadisticas_max15(entradas, campo)
                
                # Generar histograma para una variable
                imagen_histograma = EstadisticasDescriptivas.generar_histograma(stats, campo)
            except Exception as e:
                error_mensaje = f"Ocurrió un error al procesar la estadística para '{campo}': {str(e)}"
        
        # Procesar si se seleccionaron dos variables
        elif campo1 and campo2:
            # Verificar si los campos existen en las entradas
            campos_disponibles = {key for entrada in entradas for key in entrada.campos.keys()}
            campos_disponibles.add('ENTRYTYPE')
            
            if campo1 not in campos_disponibles or campo2 not in campos_disponibles:
                error_mensaje = f"Uno o ambos campos ingresados ('{campo1}', '{campo2}') no se encontraron en los datos."
                return render_template('index.html', error_mensaje=error_mensaje)

            try:
                # Calcular estadísticas descriptivas para las dos variables
                stats_dos_variables = EstadisticasDescriptivas.calcular_estadisticas_dos_campos(entradas, campo1, campo2)
                
                # Generar histograma para las dos variables
                imagen_histograma_dos_variables = EstadisticasDescriptivas.generar_histograma(stats_dos_variables, f"{campo1} - {campo2}")
            except Exception as e:
                error_mensaje = f"Ocurrió un error al calcular las estadísticas para '{campo1}' y '{campo2}': {str(e)}"
        
        else:
            error_mensaje = "Debe seleccionar una variable o dos variables válidas."

    return render_template(
        'index.html', 
        imagen_histograma=imagen_histograma, 
        imagen_histograma_dos_variables=imagen_histograma_dos_variables,
        estadisticas=stats, 
        estadisticas_dos_variables=stats_dos_variables,
        datos_frecuencias=datos_frecuencias,
        nube_palabras=nube_palabras,
        img_grafo_base64=img_grafo_base64,
        error_mensaje=error_mensaje
    )

if __name__ == '__main__':
    app.run(debug=True)
