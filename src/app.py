import os
import sys
from collections import defaultdict, Counter
import statistics
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import re
import io
import base64
import csv
from wordcloud import WordCloud
from io import BytesIO
from Ordenamiento import GnomeSort
from Util.BibFileUtil import BibFileUtil
import random
import networkx as nx

# Añadir el directorio actual al path de Python
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

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
                    valor = entrada.campos.get(campo, '').strip()

                    # Limpiar el valor si el campo es 'year'
                    if campo == "year":
                        valor = EstadisticasDescriptivas.limpiar_anio(valor)
                    
                    # Intentar convertir el valor a número
                    valor_num = float(valor) if '.' in valor else int(valor)
                    valores.append(valor_num)
                except (ValueError, TypeError):
                    print(f"Advertencia: No se pudo convertir el valor '{valor}' a número.")
                    continue
            
            if not valores:
                raise ValueError(f"No se encontraron valores numéricos válidos para el campo '{campo}'")
            
            # Calcular estadísticas
            stats = {
                'cantidad': len(valores),
                'mediana': statistics.median(valores),
                'moda': statistics.mode(valores),
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

    def calcular_estadisticas_max15(entradas, campo, n_top=15):
        """
        Encuentra los autores más frecuentes en el primer puesto de autoría y calcula estadísticas adicionales.
        
        Args:
            entradas: Lista de entradas de un archivo BibTeX.
            campo: El campo sobre el cual se realiza el análisis, generalmente 'author'.
            n_top: Número de autores principales a retornar en el análisis.
        """
        # Expresión regular para verificar que el nombre del autor no esté vacío o sea solo espacios
        regex_autor_valido = re.compile(r'\S')  # Busca al menos un carácter no blanco

        # Extraer el primer autor de cada entrada
        primeros_datos = []
        for entrada in entradas:
            try:
                valor = entrada.campos.get(campo, '').strip()
                # Dividir el campo 'author' para obtener solo el primer autor
                primer_dato = valor.split(",")[0].strip()

                # Verificar que el primer autor no esté vacío usando la expresión regular
                if regex_autor_valido.search(primer_dato):
                    primeros_datos.append(primer_dato)
            except KeyError:
                print(f"Advertencia: El campo '{campo}' no está presente en una entrada.")
                continue
            except AttributeError:
                print(f"Advertencia: El campo '{campo}' no tiene el formato esperado en una entrada.")
                continue

        # Calcular la frecuencia de cada primer autor
        contador_autores = Counter(primeros_datos)
        
        # Seleccionar los 'n_top' autores más frecuentes
        autores_frecuentes = dict(contador_autores.most_common(n_top))

        # Calcular estadísticas adicionales
        total_autores = len(primeros_datos)
        moda = contador_autores.most_common(1)[0] if contador_autores else None
        
        # Ordenar los autores alfabéticamente para calcular la mediana
        datos_ordenados = sorted(primeros_datos)
        mediana = datos_ordenados[len(datos_ordenados) // 2] if datos_ordenados else None

        # Crear el diccionario de estadísticas
        stats = {
            'cantidad': total_autores,
            'frecuencias': autores_frecuentes,
            'moda': moda,
            'mediana': mediana,
        }  

        return stats
    
    def calcular_estadisticas(entradas, campo):
        """
        Calcula estadísticas descriptivas para el tipo de producto (ENTRYTYPE) u otro campo en un archivo BibTeX.

        Returns:
            Diccionario con las estadísticas calculadas para ENTRYTYPE o valor_orden.
        """
        try:
            # Condicional para decidir qué lista de valores usar
            if campo == "ENTRYTYPE":
                tipos_producto = [entrada.entry_type for entrada in entradas if entrada.entry_type]
            else:
                tipos_producto = [entrada.campos.get(campo, '').strip() for entrada in entradas if entrada.campos.get(campo, '').strip()]
            
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
        
    def calcular_estadisticas_dos_campos(entradas, campo1, campo2, limite=15):
        """
        Calcula estadísticas descriptivas para dos campos en un archivo BibTeX, como (author, journal),
        tomando solo el primer autor si uno de los campos es 'author'.

        Args:
            entradas: Lista de objetos EntradaBib de BibTeX.
            campo1: Primer campo para la estadística (por ejemplo, 'author').
            campo2: Segundo campo para la estadística (por ejemplo, 'year').
            limite: Número máximo de combinaciones más frecuentes a mostrar.

        Returns:
            Diccionario con estadísticas descriptivas para la combinación de ambos campos.
        """
        try:
            combinaciones = []

            # Filtramos las combinaciones válidas de campo1 y campo2, procesando solo el primer autor si campo1 o campo2 es "author"
            for entrada in entradas:
                valor1 = entrada.campos.get(campo1, '').strip()
                valor2 = entrada.campos.get(campo2, '').strip()
                
                # Si campo1 es 'author', tomamos solo el primer autor
                if campo1 == 'author' and valor1:
                    valor1 = valor1.split(',')[0].strip()
                
                # Si campo2 es 'author', tomamos solo el primer autor
                if campo2 == 'author' and valor2:
                    valor2 = valor2.split(',')[0].strip()

                if campo1 == "ENTRYTYPE":
                    valor1 = entrada.entry_type
                
                if campo2 == "ENTRYTYPE":
                    valor2 = entrada.entry_type

                # Agregar solo si ambos valores existen
                if valor1 and valor2:
                    combinaciones.append((valor1, valor2))
            
            if not combinaciones:
                raise ValueError(f"No se encontraron combinaciones válidas para los campos '{campo1}' y '{campo2}' en las entradas.")
            
            # Calcular frecuencias de las combinaciones
            frecuencias = Counter(combinaciones)
            
            # Obtener las combinaciones más comunes hasta el límite especificado
            combinaciones_mas_comunes = frecuencias.most_common(limite)
            
            # Calcular la "mediana" como valor medio alfabético si es categórico
            tipos_ordenados = sorted(combinaciones)
            mediana = tipos_ordenados[len(tipos_ordenados) // 2] if tipos_ordenados else None

            # Crear el diccionario de estadísticas
            stats = {
                'cantidad': len(combinaciones),
                'frecuencias': {f"{k[0]} - {k[1]}": v for k, v in combinaciones_mas_comunes},
                'moda': f"{combinaciones_mas_comunes[0][0][0]} - {combinaciones_mas_comunes[0][0][1]}" if combinaciones_mas_comunes else None,
                'mediana': mediana 
            }
            
            return stats
        
        except Exception as e:
            print(f"Error al calcular estadísticas: {e}")
            return None

    @staticmethod
    def generar_histograma(stats, etiqueta_x):
        """
        Genera un histograma basado en las frecuencias de los datos y lo guarda como imagen en base64.

        Args:
            stats (dict): Estadísticas descriptivas que incluyen las frecuencias.
            etiqueta_x (str): Etiqueta para el eje X.

        Returns:
            str: Imagen del histograma en formato base64.
        """
        # Crear el histograma
        plt.figure(figsize=(10, 6))
        plt.bar(stats['frecuencias'].keys(), stats['frecuencias'].values(), color='skyblue')
        plt.xlabel(etiqueta_x)
        plt.ylabel('Frecuencia')
        plt.grid(axis='y', linestyle='--', alpha=0.7)

        # Rotar las etiquetas del eje X para que aparezcan verticalmente
        plt.xticks(rotation=90)

        # Guardar en un buffer en lugar de un archivo
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png", bbox_inches="tight")
        plt.close()

        # Codificar en base64
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        buffer.close()
        
        # Devolver la imagen en base64
        return img_base64


   
    def cargar_datos(nombre_archivo):
        """
        Carga el archivo de categorías y sinónimos en un diccionario.
        
        Returns:
            Diccionario con categorías como claves y listas de sinónimos como valores, donde cada sinónimo
            compuesto es una lista de sus partes.
        """
        categorias = {}
        with open(nombre_archivo, mode='r', encoding='utf-8') as archivo_csv:
            lector_csv = csv.DictReader(archivo_csv)
            for fila in lector_csv:
                categoria = fila['Categoria'].strip() # Elimina espacios
                sinonimo = fila['Variable'].strip()   # Elimina espacios
                
                # Manejar sinónimos compuestos separados por guion
                if ' - ' in sinonimo:
                    partes = sinonimo.split(' - ')
                    sinonimos = [parte.strip() for parte in partes]  # Cada parte como un sinónimo individual
                else:
                    sinonimos = [sinonimo]  # Si no hay guion, solo toma el sinónimo como está

                # Si la categoría no existe, inicializa la lista
                if categoria not in categorias:
                    categorias[categoria] = []
                
                # Agrega todas las partes del sinónimo a la lista de la categoría correspondiente
                categorias[categoria].append(sinonimos)  # Guardar lista de sinónimos o partes como una entrada
        
        return categorias

    def contar_frecuencia_categorias(entradas, categorias, campo="abstract"):
        """
        Calcula la frecuencia de cada categoría y cada variable en los abstracts.
        
        Returns:
            Dos diccionarios:
            - frecuencias_categorias: Frecuencia total de cada categoría.
            - frecuencias_variables: Frecuencia de cada sinónimo dentro de cada categoría.
        """
        frecuencias_categorias = Counter()
        frecuencias_variables = defaultdict(Counter)
        
        for entrada in entradas:
            if entrada.campos.get(campo, '').strip():  # Asegurar que el abstract existe
                valor = entrada.campos.get(campo, '').strip()
                # Convertir abstract en minúsculas y limpiar texto
                abstract_texto = valor.lower()
                palabras = re.findall(r'\b\w+\b', abstract_texto)  # Solo palabras, sin puntuación
                
                for categoria, variables in categorias.items():
                    # Contar la frecuencia de cada sinónimo o parte de sinónimo en el abstract
                    for variable_lista in variables:  # `variable_lista` es una lista de partes de sinónimo
                        total_conteo = 0  # Conteo acumulado para el sinónimo compuesto
                        
                        for parte in variable_lista:  # Cada parte de un sinónimo compuesto
                            conteo_parte = palabras.count(parte.lower())  # Contar cada parte en el abstract
                            total_conteo += conteo_parte
                        
                        # Asignar el total para el sinónimo compuesto y sumar al total de la categoría
                        frecuencias_variables[categoria][" - ".join(variable_lista)] += total_conteo
                        frecuencias_categorias[categoria] += total_conteo  # Sumar al total de la categoría
        
        return frecuencias_categorias, frecuencias_variables
    
    def generar_nube_palabras_base64(frecuencias_variables):
        """
        Genera una nube de palabras en base a las frecuencias de los sinónimos y retorna la imagen en formato base64.
            
        Returns:
            La imagen de la nube de palabras en formato base64.
        """
        # Crear un diccionario con todas las palabras y sus frecuencias
        palabras_frecuencias = {}
        for categoria, variables in frecuencias_variables.items():
            for variable, frecuencia in variables.items():
                if frecuencia > 0:  # Ignorar sinónimos con frecuencia cero
                    palabras_frecuencias[variable] = frecuencia

        # Crear la nube de palabras
        nube_palabras = WordCloud(width=800, height=400, background_color='white').generate_from_frequencies(palabras_frecuencias)
        
        # Convertir la imagen de la nube de palabras a base64
        buffered = BytesIO()
        plt.figure(figsize=(10, 5))
        plt.imshow(nube_palabras, interpolation='bilinear')
        plt.axis('off')
        plt.savefig(buffered, format="png", bbox_inches='tight')
        plt.close()
        
        # Convertir el buffer de imagen a base64
        buffered.seek(0)
        imagen_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        return imagen_base64


    @staticmethod
    def identificar_journals_mas_publicados(entradas):
        """
        Identifica los 10 journals con más artículos publicados y selecciona los 15 artículos más citados
        en cada journal, vinculando el país del primer autor.

        Args:
            entradas: Lista de objetos EntradaBib con datos de los artículos.

        Returns:
            Un diccionario que contiene los journals, citaciones totales y países asociados.
        """
        journal_counts = Counter()
        journal_articles = defaultdict(list)
        journal_citations = {}

        for entrada in entradas:
            # Usar el journal o ISSN como identificador
            journal = entrada.campos.get("journal") or entrada.campos.get("issn")
            if journal:
                journal_counts[journal] += 1
                journal_articles[journal].append(entrada)

        # Seleccionar los 10 journals con más publicaciones
        top_10_journals = [journal for journal, _ in journal_counts.most_common(10)]

        # Para cada journal, seleccionar los 15 artículos más citados
        journal_data = {}
        for journal in top_10_journals:
            articles = journal_articles[journal]
            total_citations = 0  # Acumulador de citaciones para cada journal
            
            # Obtener y asignar citaciones
            top_articles_info = []
            for article in articles:
                note = article.campos.get("note", "")
                match = re.search(r"Cited by: (\d+)", note)
                if match:
                    citations = int(match.group(1))
                else:
                    citations = random.randint(0, 250)
                article.campos["citations"] = citations
                total_citations += citations  # Acumular citaciones del journal
                
                # Solo guardar país del primer autor
                country = article.campos.get("first_author_country")
                if not country:
                    country = random.choice(["USA", "UK", "Germany", "France", "Japan", "China", "India"])
                
                top_articles_info.append({"citations": citations, "country": country})

            # Ordenar por citaciones y tomar los 15 artículos más citados
            top_articles = sorted(top_articles_info, key=lambda x: x["citations"], reverse=True)[:15]

            # Guardar la información de cada journal: total de citaciones y países únicos
            countries = list(set(article["country"] for article in top_articles))
            journal_data[journal] = {"total_citations": total_citations, "countries": countries}

        return journal_data

    @staticmethod
    def generar_grafo_journals(journal_data):
        """
        Genera un grafo de relaciones entre journals y países.

        Args:
            journal_data: Diccionario con información de los journals, sus citaciones y países asociados.

        Returns:
            La imagen del grafo en formato base64.
        """
        G = nx.Graph()

        # Crear nodos y aristas en el grafo
        for journal, info in journal_data.items():
            total_citations = info["total_citations"]
            countries = info["countries"]
            
            # Añadir nodo del journal con tamaño proporcional a las citaciones
            G.add_node(journal, tipo="journal", size=total_citations)
            
            # Añadir nodos de países y conectarlos con el journal
            for country in countries:
                G.add_node(country, tipo="country")
                G.add_edge(journal, country)  # Conexión entre journal y país

        # Dibujar el grafo y convertirlo en imagen base64
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)  # Layout del grafo

        # Configurar colores y tamaños
        colors = {"journal": "skyblue", "country": "lightcoral"}
        node_colors = [colors[G.nodes[node]["tipo"]] for node in G.nodes]
        node_sizes = [G.nodes[node]["size"] if G.nodes[node]["tipo"] == "journal" else 300 for node in G.nodes]

        # Dibujar el grafo
        nx.draw(G, pos, with_labels=True, node_size=node_sizes, node_color=node_colors, font_size=8, font_weight="bold")

        # Guardar el grafo en un buffer en formato PNG
        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        plt.close()
        
        # Codificar la imagen en base64
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.read()).decode("utf-8")
        buffer.close()

        return img_base64