# Scrapy settings for pubmed_crawler project

BOT_NAME = "pubmed_crawler"

SPIDER_MODULES = ["pubmed_crawler.spiders"]
NEWSPIDER_MODULE = "pubmed_crawler.spiders"

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (compatible; MedCrawlerBot/1.0)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 16

# Configure a delay for requests for the same website (default: 0)
DOWNLOAD_DELAY = 2  # Delay of 2 seconds between requests to the same domain

# The download delay setting will honor only one of:
CONCURRENT_REQUESTS_PER_DOMAIN = 8
CONCURRENT_REQUESTS_PER_IP = 8

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers
DEFAULT_REQUEST_HEADERS = {
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en",
}

# Enable or disable spider middlewares
# SPIDER_MIDDLEWARES = {
#     "pubmed_crawler.middlewares.PubmedCrawlerSpiderMiddleware": 543,
# }

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,  # Middleware para gestionar reintentos
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
}

# Configure Retry Middleware
RETRY_ENABLED = True  # reintentos para solicitudes fallidas
RETRY_TIMES = 3  # número máximo de reintentos para cada solicitud
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 429]  # códigos HTTP que activarán un reintento

# Set a timeout for each request
DOWNLOAD_TIMEOUT = 15  # Timeout de 15 segundos para cada solicitud

# Enable or disable extensions
# EXTENSIONS = {
#     "scrapy.extensions.telnet.TelnetConsole": None,
# }

# Configure item pipelines
ITEM_PIPELINES = {
    "pubmed_crawler.pipelines.PubMedPipeline": 300,
}

# Close spider when the page count reaches limit
CLOSESPIDER_PAGECOUNT = 500

# Enable and configure the AutoThrottle extension (disabled by default)
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2  # delay de 2 seg
AUTOTHROTTLE_MAX_DELAY = 30  # max delay
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.5 
AUTOTHROTTLE_DEBUG = False  

# Enable and configure HTTP caching (disabled by default)
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400  # validación de caché (24 hrs)
HTTPCACHE_DIR = "httpcache"
HTTPCACHE_IGNORE_HTTP_CODES = [403, 404, 500, 503]
HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
