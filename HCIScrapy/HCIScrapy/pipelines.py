# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from HCIScrapy.database import DatabaseConfig
from datetime import datetime
import math

class HciscrapyPipeline:
    def process_item(self, item, spider):
        return item


class QueryPipeline:

    def __init__(self):
        # Terms of search grouped in ORS of ANDS
        # TODO: Not sure if feasible but generalize if the search is in all fields or only some
        self.search_terms = [
                ["VR", "Virtual reality", "augmented reality", "AR", "mixed reality", "XR"],  
                ["Multiuser", "multi-user", "collaborative"]  
            ]
        self.rows_per_page = 100
        
        
    def open_spider(self, spider):
        spider.search_terms = self.search_terms
        spider.rows_per_page = self.rows_per_page 
        if spider.db == 'IEEE':
            or_groups = []
            for group in self.search_terms:
                or_groups.append(" OR ".join([f'("All Metadata":{term})' for term in group]))
            spider.query = " AND ".join([f'({term})' for term in or_groups])

class MSSQLPipeline:

    def __init__(self):
        self.total_results = 0
        self.current_page = 0
        self.max_pages = 0
        self.db_param = ''
        self.query_param = ''
        self.original_search_query = ''
        self.rows_par_page = 100
        # Testing params
        self.is_testing = False
        self.test_total_results = 100
        self.test_total_pages  = 2 

    # TODO store the initial total results query seems completely unnecesary
    def open_spider(self, spider):
        self.conn = DatabaseConfig.get_connection()
        self.cursor = self.conn.cursor()
        if spider.stype == 'Pages':

            if self.is_testing:
                spider.total_results = self.test_total_results
                spider.max_pages =  self.test_total_pages
                spider.rows_par_page = self.rows_par_page
                return

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
                self.total_results  = self.cursor.fetchone()[0]
                self.max_pages = math.ceil(self.total_results / self.rows_par_page)
                
                spider.total_results = self.total_results
                spider.max_pages = self.max_pages
                spider.rows_par_page = self.rows_par_page

            except Exception as e:
                spider.logger.error(f"Error en open_spider: {e}")
                self.total_results = 0
                self.max_pages = 0
        elif spider.stype == 'Issues':

            if self.is_testing:
                if getattr(spider, 'db', 'ACM') == 'ACM':
                    spider.documents = ['/doi/10.1145/3686215.3688380']
                elif getattr(spider, 'db', 'ACM') == 'IEEE':
                    spider.documents = ['/document/10311503/']
                    return
            
            url_field = getattr(spider, 'url_field', 'doi')
            db = getattr(spider, 'db' , 'NoDB')
            print('REACHING THE DOCUMENTS')
            urls = DatabaseConfig.get_all_unreached_issues_urls( url_field , 
                                                                [
                                                                    ('status', 'IS', None),
                                                                    ('db', '=',db),
                                                                    ('url', 'IS NOT', None)
                                                                ] )
            print(f'Documents reached {len(urls)}')
            spider.documents = urls


                
    def process_item(self, item, spider):
        
        if self.is_testing:
            with open("mssqlpipelineTest.txt", 'a',  encoding='utf-8') as file:
                for field, value in item.items():
                    print(f"{field}: {value}")
                    print(f"{field}: {value}".encode("utf-8"), file=file)
                
                    
            return item

        self.db_param = getattr(spider, 'db', 'NoDB')
        print('---------------------------------------------------------------------------------------------')
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
            try:
                print("Storing pages .... ")
                unique_field = item.get( 'unique_id' , 'doi')
                value_id = item.get( unique_field , '')
                print(f"First verification Field: {unique_field}, Value {value_id}.... ")
                self.cursor.execute(
                    'SELECT * FROM Issues WHERE ? = ?',
                    (unique_field,value_id)
                )

                if self.cursor.fetchone() is None:
                    print(f'It did not exist, adding')

                    db = getattr(spider, 'db' , 'NoDB')
            
                    def safe_int(value, default=-1):
                        try:
                            return int(value)
                        except (ValueError, TypeError):
                            return default

                    def safe_str(value):
                        return str(value) if value else None
                    # TODO : Move this to de database, probably only ussing the upsert and probably merging these 2 elifs
                    self.cursor.execute("""
                        INSERT INTO Issues (
                        DB, Title, Doi, Type, Date, Date_day, Date_month, Date_year, 
                        Comments, Abstract_truncated, Abstract, Status, Id_query, 
                        Venue, Downloads, Citations, Url)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        db,
                        safe_str(item.get("title")),
                        safe_str(item.get("doi")),
                        safe_str(item.get("type")),
                        safe_str(item.get("date")),
                        safe_int(item.get("date_day"), None),  # Asume NULL si no hay valor
                        safe_int(item.get("date_month"), None),
                        safe_int(item.get("date_year"), None),
                        safe_str(item.get("comments")),
                        safe_str(item.get("abstract_truncated")),
                        safe_str(item.get("abstract")),
                        safe_str(item.get("status")),
                        safe_int(item.get("query_id"), None),
                        safe_str(item.get("venue")),
                        safe_int(item.get("downloads"), 0),   # Usa 0 como predeterminado si no hay valor
                        safe_int(item.get("citations"), 0),
                        safe_str(item.get("url"))
                    ))
                    self.conn.commit()
            except Exception as e:
                spider.logger.error(f"Error en process_item: {e}")
        elif spider.stype == 'Issues':
            pairs = [(field, value) for field, value in item.items()]
            url_field_name = getattr(spider, 'url_field')
            url_field = item.get(url_field_name)
            DatabaseConfig.upsert_issue(pairs, (url_field_name, url_field))
        return item

    def close_spider(self, spider):
        # Cerrar conexiones
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()

