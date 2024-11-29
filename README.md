# 🕸️ PubMed Crawler 🧬

## 📄 Descripción
**PubMed Crawler** es un crawler web desarrollado con **Scrapy**, diseñado específicamente para rastrear y extraer información del sitio web de **PubMed** (https://pubmed.ncbi.nlm.nih.gov). Este proyecto tiene como objetivo recopilar artículos científicos que cumplan con criterios específicos, con el fin de ayudar a las personas a tener una búsqueda más rápida y especializadea, almacenando los datos en una base de datos **SQLite** para su posterior análisis.

## ✨ Características
- 🌐 **Dominio específico**: Limita el rastreo al dominio de PubMed.
- 🔎 **Profundidad de rastreo**: Configurable hasta máximo 4 niveles de profundidad.
- 🔗 **Inicio personalizable**: Permite al usuario especificar una URL de inicio (si no se especifica, tiene una por **default**).
- 🩺 **Filtrado por palabras clave**: Solo extrae páginas que contienen ciertas palabras clave médicas y científicas.
- 📹 **Tipos de contenido**: Verifica la presencia de imágenes, videos, PDFs, tablas, figuras y enlaces externos.
- 🕓 **Actualización reciente**: Rastrear solo páginas actualizadas en los últimos 180 días.
- 📝 **Tamaño de página**: Descarta páginas que exceden 2 MB.
- 🔖 **Etiquetas HTML requeridas**: Solo procesa páginas que contienen ciertas etiquetas HTML.
- 🌍 **Idioma**: Filtra páginas para que solo se procesen aquellas en inglés.
- 🔄 **Enlaces internos**: Sigue únicamente enlaces internos dentro del dominio permitido.
- 🗺️ **Ubicación geográfica**: Limita el rastreo a servidores ubicados en **Estados Unidos**.
- 📊 **Estructura de URL**: Solo sigue URLs que contienen un patrón específico.
- 🔒 **Evita autenticación**: Descarta páginas que requieren autenticación o parecen ser páginas de inicio de sesión.

## 💻 Tecnologías usadas
- **Python 3**
- **Chrome 114**
- **Scrapy**: Framework para la extracción de datos web.
- **Langid**: Biblioteca para la detección de idioma.
- **GeoIP2**: Para determinar la ubicación geográfica de los servidores.
- **SQLite3**: Base de datos ligera para almacenar los datos extraídos.
- **Dateutil**: Para manejar fechas y tiempos.
- **Otras bibliotecas estándar de Python**: `datetime`, `re`, `urllib`, `socket`, etc.

## ✅ Requisitos del proyecto
El proyecto cumple con los siguientes requisitos:

1. 🌐 **Por dominio**: Limita el rastreo al dominio `pubmed.ncbi.nlm.nih.gov`.
2. 🔍 **Por profundidad**: Establece un límite de 4 niveles de profundidad.
3. 🔗 **Por URL**: Permite ingresar una URL específica para comenzar el rastreo.
4. 🩺 **Por palabras clave**: Filtra páginas que contienen ciertas palabras clave definidas en la configuración.
5. 📹 **Por tipo de contenido**: Solo procesa páginas que contienen tipos de contenido específicos (imágenes, videos, PDFs, etc.).
6. 🕓 **Por frecuencia de actualización**: Rastrear solo páginas actualizadas en los últimos 180 días.
7. 📝 **Por tamaño de página**: Limita el tamaño de la página a 2 MB.
8. 🔖 **Por etiquetas HTML**: Solo procesa páginas que contienen ciertas etiquetas HTML (e.g., `<meta name="description">`).
9. 📅 **Por fecha de publicación**: Rastrear solo páginas publicadas después del 1 de enero de 2023.
10. 🌍 **Por idioma**: Filtra páginas en inglés.
11. 🔄 **Por tipo de enlace**: Sigue únicamente enlaces internos.
12. 🗺️ **Por ubicación geográfica**: Limita el rastreo a servidores en **Estados Unidos**.
13. 🔗 **Por estructura de URL**: Sigue solo URLs que contienen el patrón `.*pubmed.*`.
14. 🔒 **Por restricciones de acceso**: Evita páginas que requieren autenticación.
15. 🕓 **Por fecha de modificación**: Rastrear solo páginas modificadas recientemente (últimos 180 días).
16. 🔍 **Por patrones de URL**: Sigue URLs que coinciden con un patrón específico.
17. 🧠 **Por contexto semántico**: Filtra páginas relacionadas semánticamente con temas médicos y científicos.
18. ✅ **Por popularidad**: Tiene un contador de popularidad de enlaces.

**Nota**: Los requisitos 'por sitemap' y 'por autoridad del dominio' no se cumplen en la versión actual del crawler.

## ⚙️ ¿Cómo funciona?
El crawler utiliza **Scrapy** para rastrear el sitio web de **PubMed** siguiendo reglas y filtros definidos en la configuración (`CONFIG`). A continuación, se detalla su funcionamiento:

1. **Inicialización**: 
   - Carga la configuración y establece la URL de inicio.
   - Carga la base de datos **GeoIP2** para verificar ubicaciones geográficas.

2. **Rastreo**:
   - Sigue enlaces internos dentro del dominio permitido, respetando la profundidad máxima y otros límites.

3. **Filtrado**:
   - Verifica que la página no requiera autenticación.
   - Comprueba la ubicación geográfica del servidor.
   - Verifica el tamaño de la página.
   - Confirma la presencia de etiquetas HTML requeridas.
   - Verifica que contenga el tipo de contenido requerido.
   - Extrae y verifica la fecha de publicación.
   - Detecta el idioma del contenido.
   - Busca palabras clave en el texto.

4. **Extracción**:
   - Si la página cumple con todos los criterios, extrae la información relevante:
     - URL
     - Título
     - Fecha de publicación
     - Autores
     - Palabras clave encontradas
     - Fragmento del contenido
     - Tipo de contenido encontrado
     - Popularidad de enlaces entrantes

5. **Almacenamiento**:
   - Utiliza un pipeline para almacenar los datos extraídos en una base de datos **SQLite** (`datos_rastreados.db`).

## 🚀 Instrucciones de instalación y uso

### Requisitos previos
- **Python 3.13.0**
- **Scrapy**: Se puede instalar usando `pip install scrapy`
- **GeoIP2**: `pip install geoip2`
- **Langid**: `pip install langid`
- **Dateutil**: `pip install python-dateutil`

### 📥 Descarga de la Base de Datos GeoLite2
1. Descarga el archivo **GeoLite2-City.mmdb** desde [MaxMind GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data).
2. Coloca el archivo **GeoLite2-City.mmdb** en el directorio raíz del proyecto.

### ▶️ Ejecución del Crawler
1. Clona el repositorio o descarga los archivos del proyecto.

2. Navega al directorio del proyecto:
   cd pubmed_crawler
3. Instala las dependencias
4. Ejecuta el crawler
   scrapy crawl pubmed
   Puedes especificar una URL diferente:
       scrapy crawl pubmed -a start_url="https://pubmed.ncbi.nlm.nih.gov/specific_page"
   O un output en formato .json para cuestión de pruebas:
       scrapy crawl pubmed -o output.json
### 📊 Acceso a los datos extraídos
Los datos se almacenan en la base de datos SQLite datos_rastreados.db.
Puedes acceder a los datos utilizando herramientas como sqlite3 en la línea de comandos o herramientas gráficas como "DB Browser for SQLite": 
  sqlite3 datos_rastreados.db
O en la consola de SQLite:
  SELECT * FROM articulos;
### 🛑 Consideraciones éticas y legales
* Respeto a las oolíticas del sitio: El crawler respeta las directivas de robots.txt y limita la carga en el servidor mediante retrasos y límites en las solicitudes.
* Datos públicos: El crawler solo extrae información disponible públicamente y no accede a datos privados o protegidos.

### Datos personales
* Nombre completo: Hernández Cortez Kevin Uriel.
* Código: 217734547.
* Materia: Programación para internet - D17.
* Profesor: Guzman Montes Carlos Alberto.
* Fecha 29/11/24

Disfruta rastreando PubMed de manera eficiente y ética con PubMed Crawler! 🕸️✨
