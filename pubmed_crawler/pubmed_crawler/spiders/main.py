import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
import langid
from datetime import datetime, timedelta
from collections import Counter
from dateutil import parser
import re
from urllib.parse import urlparse
import geoip2.database
import os
import socket
# CONFIGURACIONES DE SERVIDOR
CONFIG = {
    'dominio_permitido': "pubmed.ncbi.nlm.nih.gov",
    'profundidad_maxima': 4,
    'max_urls_a_rastrear': 500,
    'palabras_clave': [ # se puede modificar para filtrar lo que se desee encontrar
        "randomized controlled trial", "systematic review", "meta-analysis", "clinical guidelines", "evidence-based practice",
        "treatment efficacy", "risk factors", "treatment outcome", "cohort study", "clinical trial", "cross-sectional study",
        "case-control study", "drug therapy", "surgical procedures", "pharmacological intervention", "cancer", "cardiovascular disease",
        "diabetes", "infectious diseases", "mental health", "prevalence", "incidence", "mortality", "population health"
    ],
    'etiquetas_requeridas': ["p"],
    'agente_usuario': "Mozilla/5.0 (compatible; MedCrawlerBot/1.0)",
    'tamano_max_pagina': 2097152,  # 2 MB
    'idiomas_permitidos': ["en"],
    'fecha_publicacion_minima': datetime(2023, 1, 1),
    'contenido_requerido': ["imagen", "video", "pdf", "tabla", "figure", "enlace_externo"],  
    'actualizacion_dias_max': 180,  # se puede extender la cantidad de días 
    'etiquetas_html_requeridas': [ # metaetiquetas
        {'name': 'meta', 'attrs': {'name': 'description'}},  
        {'name': 'h1'},  
    ],
    'tipo_enlace_permitido': "interno",  #  se puede "interno", "externo", o "ambos"
    'ubicacion_geografica_permitida': "United States",  # ubicación predeterminada
    'estructura_url_permitida': r".*pubmed.*",  # patrón simplificado para pruebas para permitir cualquier URL que contenga "pubmed"
    'palabras_clave_autenticacion': ["login", "signin", "register", "account", "auth"],  # palabras clave para evitar autenticación
}

class PubMedSpider(CrawlSpider):
    """
        Clase principal, base del crawler
    """
    name = 'pubmed'
    allowed_domains = [CONFIG['dominio_permitido']]
    custom_settings = {
        'DEPTH_LIMIT': CONFIG['profundidad_maxima'],
        'USER_AGENT': CONFIG['agente_usuario'],
        'CLOSESPIDER_PAGECOUNT': CONFIG['max_urls_a_rastrear'],
    }

    def __init__(self, *args, **kwargs):
        """
            Se inicializa la clase con configuraciones de rastreo. Tambien cargamos
            la base de datos de "GeoIP" para verificar la ubicación geográfica de los servidores.
        """
        start_url = kwargs.get('start_url', CONFIG.get('url_inicial', "https://pubmed.ncbi.nlm.nih.gov"))
        self.start_urls = [start_url]
        super(PubMedSpider, self).__init__(*args, **kwargs)
        self.popularidad_enlaces = Counter()    
        geoip_db_path = os.path.abspath('GeoLite2-City.mmdb') # carga de bd geolite2
        if not os.path.exists(geoip_db_path):
            raise FileNotFoundError(f"No se encontró la base de datos GeoLite2 en la ruta especificada: {geoip_db_path}. Por favor, descargue la base de datos desde https://dev.maxmind.com/geoip/geolite2-free-geolocation-data y colóquela en la ubicación correcta.")
        try:
            self.geoip_reader = geoip2.database.Reader(geoip_db_path)
        except Exception as e:
            raise RuntimeError(f"No se pudo cargar la base de datos GeoLite2: {e}")
    
    def parse_start_url(self, response):
        """
            Se verifica la ubicación geográfica del servidor antes de procesar la URL de inicio.
        """
        if not self.is_location_allowed(response.url):
            self.logger.info(f"Página descartada por ubicación geográfica no permitida: {response.url}")
            return

        # Llamar al parse_item para procesar la página si la ubicación es permitida
        yield from self.parse_item(response)

    def is_location_allowed(self, url):
        """
            Se verifica si el servidor de la página está ubicado en la región correcta "usando GeoIP).
        """
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.hostname
            ip = socket.gethostbyname(domain) # extradción de IP del dominio
            response = self.geoip_reader.city(ip) # consulta de ubicación
            country = response.country.name
            if country == CONFIG['ubicacion_geografica_permitida']:
                return True
            else:
                self.logger.debug(f"Ubicación geográfica de {url} es {country}, no coincide con {CONFIG['ubicacion_geografica_permitida']}")
                return False
        except geoip2.errors.AddressNotFoundError:
            self.logger.error(f"No se pudo determinar la ubicación para {url}: Dirección IP no encontrada en la base de datos GeoIP.")
            return False
        except socket.gaierror:
            self.logger.error(f"No se pudo resolver el dominio {domain} a una dirección IP.")
            return False
        except Exception as e:
            self.logger.error(f"No se pudo determinar la ubicación para {url}: {e}")
            return False
    # se definen reglas basadas en el tipo de enlace permitido y la estructura de URL permitida
    if CONFIG['tipo_enlace_permitido'] == "interno":
        rules = (
            Rule(LinkExtractor(allow_domains=allowed_domains, allow=[CONFIG['estructura_url_permitida']]), callback='parse_item', follow=True),
        )
    elif CONFIG['tipo_enlace_permitido'] == "externo":
        rules = (
            Rule(LinkExtractor(deny_domains=allowed_domains, allow=[CONFIG['estructura_url_permitida']]), callback='parse_item', follow=True),
        )
    elif CONFIG['tipo_enlace_permitido'] == "ambos":
        rules = (
            Rule(LinkExtractor(allow=[CONFIG['estructura_url_permitida']]), callback='parse_item', follow=True),
        )
    else:
        raise ValueError("Valor inválido para 'tipo_enlace_permitido' en CONFIG")

    def parse_item(self, response):
        """
            Se procesa cada página rastreada: verificar autenticación, ubicación, tamaño y extrae información relevante.
            Se verifica si la URL contiene palabras clave relacionadas con autenticación.
        """
        self.logger.debug(f"Procesando URL: {response.url}")
        for palabra in CONFIG['palabras_clave_autenticacion']: #verificación de palabras
            if palabra in response.url.lower():
                self.logger.info(f"Página descartada porque la URL sugiere autenticación: {response.url}")
                return
        if response.status in [401, 403]: # RESPUESTA
            self.logger.info(f"Página descartada por requerir autenticación (código de estado {response.status}): {response.url}")
            return
        # verificacion por si la página tiene elementos que indiquen un formulario de autenticación
        if response.css('input[type="password"], form[id*="login"], form[class*="login"]'):
            self.logger.info(f"Página descartada porque parece ser una página de login: {response.url}")
            return
        # verificacion de la ubicación geográfica del servidor
        if not self.is_location_allowed(response.url):
            self.logger.info(f"Página descartada por ubicación geográfica no permitida: {response.url}")
            return
        # verificacion del tamaño de la página
        if len(response.body) > CONFIG['tamano_max_pagina']:
            self.logger.info(f"Página descartada por exceder el tamaño máximo: {response.url}")
            return
        # verificacion por si la página tiene las etiquetas HTML requeridas
        for etiqueta in CONFIG['etiquetas_html_requeridas']:
            if etiqueta['name'] == 'meta':
                if not response.css(f"meta[{list(etiqueta['attrs'].keys())[0]}='{list(etiqueta['attrs'].values())[0]}']"):
                    self.logger.info(f"Página descartada porque no tiene la metaetiqueta requerida: {response.url}")
                    return
            else:
                if not response.css(f"{etiqueta['name']}"):
                    self.logger.info(f"Página descartada porque no tiene la etiqueta <{etiqueta['name']}> requerida: {response.url}")
                    return
        # actualizacion del contador de popularidad de enlaces para cada enlace en la página 
        link_extractor = LinkExtractor(allow_domains=self.allowed_domains)
        links = link_extractor.extract_links(response)
        for link in links:
            self.popularidad_enlaces[link.url] += 1
        try:
            contenido_encontrado = [] # verificación de contenido (varios LOGS de apoyo)
            if "imagen" in CONFIG['contenido_requerido']:
                imagenes = response.css('img::attr(src)').getall()
                if imagenes:
                    contenido_encontrado.append("imagen")
                    self.logger.debug(f"Imágenes encontradas en {response.url}: {imagenes}")
            if "video" in CONFIG['contenido_requerido']:
                videos = response.css('video, iframe').getall()
                if videos:
                    contenido_encontrado.append("video")
                    self.logger.debug(f"Videos encontrados en {response.url}")
            if "pdf" in CONFIG['contenido_requerido']:
                enlaces_pdf = response.css('a::attr(href)').re(r'.*\.pdf$')
                if enlaces_pdf:
                    contenido_encontrado.append("pdf")
                    self.logger.debug(f"Enlaces a PDF encontrados en {response.url}: {enlaces_pdf}")
            if "tabla" in CONFIG['contenido_requerido']:
                tablas = response.css('table').getall()
                if tablas:
                    contenido_encontrado.append("tabla")
                    self.logger.debug(f"Tablas encontradas en {response.url}")
            if "figure" in CONFIG['contenido_requerido']:
                figuras = response.css('figure').getall()
                if figuras:
                    contenido_encontrado.append("figure")
                    self.logger.debug(f"Figuras encontradas en {response.url}")
            if "enlace_externo" in CONFIG['contenido_requerido']:
                enlaces_externos = response.css('a::attr(href)').re(r'^(http|https)://(?!pubmed\.ncbi\.nlm\.nih\.gov).*')
                if enlaces_externos:
                    contenido_encontrado.append("enlace_externo")
                    self.logger.debug(f"Enlaces externos encontrados en {response.url}: {enlaces_externos}")
            # si no se encuentra el tipo de contenido requerido, descartar la página
            if not contenido_encontrado:
                self.logger.info(f"Artículo descartado porque no tiene el contenido requerido: {response.url}")
                return
            # extracción de fecha de publicación con selectores Scrapy
            fecha_publicacion = response.css('meta[name="citation_publication_date"]::attr(content)').get(default='N/A')
            self.logger.debug(f"Fecha de publicación extraída: {fecha_publicacion}")
            # verificación la antigüedad de la publicación (usando fecha de publicación como proxy)
            if fecha_publicacion != 'N/A':
                try:
                    fecha_publicacion_dt = parser.parse(fecha_publicacion)
                    dias_recientes = timedelta(days=CONFIG['actualizacion_dias_max'])
                    if fecha_publicacion_dt < datetime.now() - dias_recientes:
                        self.logger.info(f"Artículo descartado por ser más antiguo de {CONFIG['actualizacion_dias_max']} días: {response.url}")
                        return
                except (ValueError, TypeError):
                    self.logger.warning(f"Formato de fecha inválido: {fecha_publicacion} en {response.url}")
            else:
                self.logger.info(f"Artículo descartado porque no se encontró información de publicación: {response.url}")
                return
            # extracción de título con selectores Scrapy
            titulo = response.css('title::text').get(default='N/A')
            self.logger.debug(f"Título extraído: {titulo}")
            # extracción de autores con selectores Scrapy
            autores = response.css('meta[name="citation_author"]::attr(content)').getall()
            autores = ', '.join(autores) if autores else 'N/A'
            self.logger.debug(f"Autores extraídos: {autores}")
            # extracción de fragmento del contenido
            fragmento_contenido = ' '.join(response.css('p::text').getall()).strip()[:200] or 'N/A'
            self.logger.debug(f"Fragmento del contenido: {fragmento_contenido}")
            # verificación si el fragmento es suficientemente largo para la detección de idioma
            if len(fragmento_contenido) < 50:
                self.logger.info(f"Fragmento demasiado corto para detección de idioma: {response.url}")
                return
            # detección del idioma
            idioma_detectado = langid.classify(fragmento_contenido)[0]
            self.logger.debug(f"Idioma detectado: {idioma_detectado}")
            if idioma_detectado not in CONFIG['idiomas_permitidos']:
                self.logger.info(f"Artículo descartado por idioma: {response.url}")
                return
            # búsqueda de palabras clave
            page_text = ' '.join(response.css('*::text').getall()).lower()
            keywords_lower = [kw.lower() for kw in CONFIG['palabras_clave']]
            palabras_clave_encontradas = ', '.join([
                kw for kw in keywords_lower if re.search(r'\b' + re.escape(kw) + r'\b', page_text)
            ])
            self.logger.debug(f"Palabras clave encontradas: {palabras_clave_encontradas}")
            # filtrar páginas que no contienen las palabras clave
            if not palabras_clave_encontradas:
                self.logger.info(f"Artículo descartado porque no contiene las palabras clave requeridas: {response.url}")
                return
            # Creamos el item
            item = {
                'URL': response.url,
                'Titulo': titulo,
                'Fecha de Publicación': fecha_publicacion,
                'Autores': autores,
                'Palabras Clave Encontradas': palabras_clave_encontradas,
                'Fragmento del Contenido': fragmento_contenido,
                'Tipo de Contenido Encontrado': ', '.join(contenido_encontrado),
                'Popularidad de Enlaces Entrantes': self.popularidad_enlaces[response.url]
            }
            self.logger.debug(f"Ítem generado: {item}")
            yield item

        except AttributeError as e:
            self.logger.error(f"Atributo no encontrado: {e} en {response.url}")
        except Exception as e:
            self.logger.exception(f"Error inesperado en {response.url}")
            raise e