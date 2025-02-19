import requests
from bs4 import BeautifulSoup
import json
import re
import urllib.parse

def buscar_en_duckduckgo(consulta):
    """Realiza una búsqueda en DuckDuckGo y devuelve los 3 primeros resultados."""
    url_busqueda = f"https://duckduckgo.com/html/?q={'+'.join(consulta.split(', '))}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    respuesta = requests.get(url_busqueda, headers=headers)
    soup = BeautifulSoup(respuesta.text, 'html.parser')
    
    resultados = []
    for resultado in soup.find_all('a', class_='result__a', limit=3):
        titulo = resultado.text.strip()
        enlace = resultado['href']
        
        # Extraer la URL real y limpiar parámetros extraños
        if 'uddg=' in enlace:
            enlace = urllib.parse.unquote(enlace.split('uddg=')[-1].split('&')[0])
        
        descripcion = "Descripción no disponible en DuckDuckGo"
        resultados.append((titulo, enlace, descripcion))
    
    return resultados

def obtener_html(url):
    """Obtiene el HTML de una página web dada una URL."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        respuesta = requests.get(url, headers=headers, timeout=10)
        respuesta.raise_for_status()
        return respuesta.text
    except requests.exceptions.RequestException as e:
        print(f"Error al acceder a {url}: {e}")
        return None

def extraer_texto(html):
    """Extrae el texto limpio de una página HTML."""
    soup = BeautifulSoup(html, 'html.parser')
    for script in soup(['script', 'style']):
        script.decompose()
    texto = ' '.join(soup.stripped_strings)
    return texto

def filtrar_informacion(texto, palabras_clave):
    """Filtra información relevante según palabras clave y elimina duplicados."""
    coincidencias = set()
    for line in texto.split('. '):
        for palabra in palabras_clave:
            if re.search(rf'\b{palabra}\b', line, re.IGNORECASE):
                if len(line) > 20:  # Evita fragmentos muy cortos
                    coincidencias.add(line.strip())
    return list(coincidencias)

def guardar_resultados(datos, archivo="resultados.json"):
    """Guarda los datos extraídos en un archivo JSON."""
    with open(archivo, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4, ensure_ascii=False)

def aracne_net_bug():
    """Ejecuta la búsqueda en DuckDuckGo y luego analiza el enlace elegido."""
    consulta = input("Introduce las palabras clave separadas por comas (ejemplo: palabra1, palabra2, palabra3): ")
    resultados = buscar_en_duckduckgo(consulta)
    
    if not resultados:
        print("No se encontraron resultados.")
        return
    
    print("\nResultados encontrados:")
    for i, (titulo, enlace, descripcion) in enumerate(resultados, start=1):
        print(f"{i}. {titulo}\n   {descripcion}\n   {enlace}\n")
    
    opcion = int(input("Selecciona un enlace (1-3): ")) - 1
    if opcion not in range(3):
        print("Selección no válida.")
        return
    
    url_seleccionada = resultados[opcion][1]
    print(f"\nAnalizando {url_seleccionada}...")
    html = obtener_html(url_seleccionada)
    if not html:
        return
    
    palabras_clave = consulta.split(', ')
    texto_extraido = extraer_texto(html)
    info_relevante = filtrar_informacion(texto_extraido, palabras_clave)
    
    resultado = {
        "url": url_seleccionada,
        "palabras_clave": palabras_clave,
        "informacion_encontrada": info_relevante
    }
    
    guardar_resultados(resultado)
    print(f"\nProceso completado. Información guardada en 'resultados.json'")

if __name__ == "__main__":
    aracne_net_bug()
