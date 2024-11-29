import sqlite3
# aquí se implementa la lógica para crear/manejar la base de datos
class PubMedPipeline:

    def open_spider(self, spider):
        self.conn = sqlite3.connect('datos_rastreados.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS articulos (
                URL TEXT PRIMARY KEY,
                Titulo TEXT,
                Fecha_Publicacion TEXT,
                Autores TEXT,
                Palabras_Clave_Encontradas TEXT,
                Fragmento_Contenido TEXT,
                Tipo_Contenido_Encontrado TEXT,
                Popularidad_Enlaces_Entrantes INTEGER
            )
        ''')

    def close_spider(self, spider):
        # confirmamos y cerramos la conexión a la base de datos al terminar el crawler
        if self.conn:
            self.conn.commit()
            self.conn.close()

    def process_item(self, item, spider):
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO articulos (URL, Titulo, Fecha_Publicacion, Autores, Palabras_Clave_Encontradas, Fragmento_Contenido, Tipo_Contenido_Encontrado, Popularidad_Enlaces_Entrantes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                item.get('URL'),
                item.get('Titulo', 'N/A'),
                item.get('Fecha de publicación', 'N/A'),
                item.get('Autores', 'N/A'),
                item.get('Palabras clave', 'N/A'),
                item.get('Fragmento del contenido', 'N/A'),
                item.get('Tipo de contenido', 'N/A'),
                item.get('Popularidad de enlaces',0)
            ))
            self.conn.commit()
        except sqlite3.Error as e:
            spider.logger.error(f"Error al insertar en la base de datos: {e} con item: {item}")
        return item
