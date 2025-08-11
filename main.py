"""
Imagina que esta API es una biblioteca de películas:
La función load movies() es como un bibliotecario que carga el catálogo de libros(películas) cuando se abre la biblioteca.
La función get_movies() muestra todo el catálogo cuando alguien lo pide.
la función get_movie(id) es como si alguien preguntara por un libro específico por su código de identificación.
La función chatbot (query) es un asistente que busca libros según palabras clave y sinónimo.
La función get_movies_by_category (category) ayuda a encontrar películas según su género (acción, comedia, etc.).

"""

# Importamos las herramientas encesarias para construir nuestra API
from fastapi import FastAPI, HTTPException # FastAPI nos ayuda a crear la API y HTTPException maneja errores.
from fastapi.responses import HTMLResponse, JSONResponse # HTMLResponse sirve para páginas web, JSONResponse para respuestas en formato JSON.

import pandas as pd # pandas nos ayuda amanejar datos en tablas como si fueran un excel.
import nltk # Es una librería para procesar texto y analizar palabras.
from nltk.tokenize import word_tokenize # Se utiliza para dividir un texto en palabras individuales.
from nltk.corpus import wordnet # Nos ayuda a encontrar sinónimos de palabras.

# Indicamos la ruta donde NLTK buscará los datos descargados en nuestro computador.

nltk.data.path.append('/home/serhoyos/nltk_data')

# Descargamos las herramientas necesarias de NLTK para el análisis de palabras.

nltk.download('punkt') # Paquete para dividir frases en palabras.
nltk.download('wordnet') # Paquete para encontrar sinónimos de palabaras en inglés.

# Función para cargar las películas desde un archivo CSV

def load_movies():
    # Leemos el archivo que contien información de películas y seleccionamos las columnas mas importantes.
    df = pd.read_csv('Dataset/netflix_titles.csv')[['show_id', 'title', 'release_year', 'listed_in', 'rating', 'description']]

    # Renombramos las columnas para que sean mas fáciles de entender
    df.columns = ['id', 'title', 'year', 'category', 'rating', 'overview']

    # llenamos los espacios vacíos con texto vacío y convertimos los datos en una lista de diccionarios.
    return df.fillna('').to_dict(orient='records')

# Cargamos la películas al iniciar la API para no leer el archivo cada vez que alguien pregunte por ellas.
movies_list = load_movies()

# Función para encontrar sinónimos de una palabra

def get_synonyms(word):
    # Usamos wordnet para obtener distintas palabras que sinfifican lo mismo
    return {lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}

# Creamos la aplicación FastAPI, que será el motor de nuestra API
# Esto inicializa la API con un nombe y una versión
app = FastAPI(title="Mi aplicación de películas", version="1.0.0")

# cuando alguien entra a la API sin especificar nada, verá un mensaje de bienvenida.

@app.get('/', tags=['Home'])
def home():
    # cuando entremos en el navegador a http://127.0.0.1:8000/ veremos un mensaje de bienvenida
    return HTMLResponse('<h1>Bienvenido a la API de películas</h1>')

# Obteniendo la lista de películas
# Creamos una lista para obtener todas las pelícukas

# Ruta para obtener todas las películas disponibles

@app.get('/movies', tags=['Movies'])
def get_movies():
    # si hay películas, las enviamos, sino, mostramos un error.
    return movies_list or HTTPException(status_code=500, detail="No hay datos de películas disponibles")
# Ruta para obtener una película específica según du id
@app.get('/movies/{id}', tags=['Movies'])
def get_movie(id: str):
    # Buscamos en la lista de películas la que tenga el mismo id.
    return next((m for m in movies_list if m['id'] == id), {"detalle": "película no encontrada"})

# Ruta del chatbot que responde con películas según palabras clave de la categoría

@app.get('/chatbot', tags=['Chatbot'])
def chatbot(query: str):
    # Dividimos la consulta en palabras clave para entender mejor la intención del usuario
    query_words = word_tokenize(query.lower())

    # Buscamos sinónimos de las palabras clave para ampliar la búsqueda
    synonyms = {word for q in query_words for word in get_synonyms(q)} | set(query_words)

    # Filtramos la lista de películas buscando coinciencias en la categoría
    results = [m for m in movies_list if any(s in m['category'].lower() for s in synonyms)]

    # Si encontramos películas, enviamos la lista, sino, mostramos un mensaje de que no se encontraron coincidencias
    return JSONResponse (content={
        "respuesta": "Aquí tienes algunas películas relacionadas." if results else "No encontré películas en esa categoría",
        "películas": results
    })

# Ruta para buscar películas por categoría específica   

@app.get ('/movies/by_category/', tags=['Movies'])
def get_movies_by_category(category: str):
    # Filtramos la lista de películas según la categpría ingresada 
    return [m for m in movies_list if category.lower() in m['category'].lower()]

