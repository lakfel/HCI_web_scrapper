# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from HCIScrapy.database import DatabaseConfig
from datetime import datetime
import pyodbc
import math

class HciscrapyPipeline:
    def process_item(self, item, spider):
        return item
    

class MSSQLPipeline:

    def __init__(self):
        self.total_results = 0
        self.current_page = 0
        self.max_pages = 0
        self.db_param = ''
        self.query_param = ''
        self.original_search_query = ''


    def open_spider(self, spider):
        self.conn = DatabaseConfig.get_connection()
        self.cursor = self.conn.cursor()
        if spider.stype == 'Pages':
            try:
                self.db_param = getattr(spider, 'db', 'NoDB')
                self.query_param = getattr(spider, 'query', '')
                query = """
                        SELECT TOP 1 total_results
                        FROM Query_total_results
                        WHERE db = ? AND query = ?
                        ORDER BY timestamp DESC
                        """
                self.cursor.execute(query, (self.db_param, self.query_param))
                self.rows_par_page = 100
                self.max_pages = math.ceil(self.total_results / self.rows_par_page)

                # Definir consulta de búsqueda (puedes pasarla como atributo o definirla aquí)
                self.original_search_query = '(("All Metadata":VR) OR ("All Metadata":Virtual reality) OR ("All Metadata":augmented reality) OR ("All Metadata":AR) OR ("All Metadata":mixed reality) OR ("All Metadata":XR)) AND (("All Metadata":Multiuser) OR ("All Metadata":multi-user) OR ("All Metadata":collaborative))'
                
                spider.total_results = self.total_results
                spider.max_pages = self.max_pages
                spider.rows_par_page = self.rows_par_page
                #spider.original_search_query = self.original_search_query
            except Exception as e:
                spider.logger.error(f"Error en open_spider: {e}")
                self.total_results = 0
                self.max_pages = 0

                
    def process_item(self, item, spider):
        
        self.db_param = getattr(spider, 'db', 'NoDB')
        if spider.stype == 'Results':
            # Guardar datos para resultados IEEE
            self.cursor.execute(
                """
                INSERT INTO Query_total_results 
                (db, timestamp, url, query, total_results) 
                VALUES (?, ?, ?, ?, ?)
                """, 
                (
                    self.db_param,
                    datetime.now(),  # timestamp
                    item.get('url', ''),  # url
                    item.get('query', ''),  # query de búsqueda
                    item.get('total_results', 0)  # total de resultados
                )
            )
            self.conn.commit()
        elif spider.stype == 'Pages':
            return item
            try:
                self.cursor.execute(
                    'SELECT * FROM Issues WHERE doi = ?',
                    (item.get('doi'),'')
                )
                if self.cursor.fetchone()[0] == 0:
                    
                    db = getattr(spider, 'db' , 'NoDB')
                    query = getattr(spider, 'query', '')
                    

                    self.cursor.execute("""
                        INSERT INTO Query_status 
                        (DB, Query, Page_count, Url, Time_stamp) VALUES ( ?, ? , ?, ?, ?)
                        """ , 
                        (db, 
                        query, 
                        item.get('page_count'), 
                        item.get('url'),
                        datetime.now()
                        )
                    )
                    last_id = self.cursor.fetchone()[0]

                    self.cursor.execute("""
                            INSERT INTO Issues (
                            DB,	Title,	Doi,	Type,	Date,	Date_day,	Date_month,	Date_year,	Comments,	Abstract_truncated,	 Abstract,	Status,	Id_query,	Venue,	Downloads,	Citations, Url)
                            VALUES (?,	?,	?,	?,	?,	?,	?,	?,	?,	?,	?,	?,	?,	?,	?,	?, ?)
                        """,
                        (
                            db,
                            item.get("title",''),
                            item.get("doi",''),
                            item.get("type",''),
                            item.get("date",''),
                            item.get("date_day",''),
                            item.get("date_month",''),
                            item.get("date_year",''),
                            item.get("comments",''),
                            item.get("abstract_truncated",''),
                            item.get("abstract",''),
                            item.get("status",''),
                            last_id,
                            item.get("venue",''),
                            item.get("downloads",-1),
                            item.get("citations",-1),
                            item.get("url",'')
                        )
                    )

            except Exception as e:
                spider.logger.error(f"Error en process_item: {e}")
        return item

    def close_spider(self, spider):
        # Cerrar conexiones
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()

