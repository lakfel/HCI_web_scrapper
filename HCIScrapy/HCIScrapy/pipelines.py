# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from HCIScrapy.database import DatabaseManager
from datetime import datetime
from HCIScrapy.config import STORAGE_TEST
from HCIScrapy.config import SEARCH_QUERY
from HCIScrapy.config import DB_ACM
from HCIScrapy.config import DB_IEEE
from HCIScrapy.config import DB_SD
from HCIScrapy.config import DB_SPRINGER

class HciscrapyPipeline:
    def process_item(self, item, spider):
        return item


class QueryPipeline:

    def __init__(self):
        # Terms of search grouped in ORS of ANDS
        # TODO: Not sure if feasible but generalize if the search is in all fields or only some
        self.search_terms = SEARCH_QUERY
        self.rows_per_page = 100
        
        
    def open_spider(self, spider):

        spider.search_terms = self.search_terms
        spider.rows_per_page = self.rows_per_page 
        
        if spider.db == DB_ACM:
            or_groups = []
            for group in self.search_terms:
                or_groups.append(" OR ".join([f'AllField:({term})' for term in group]))
            spider.query = " AND ".join([f'({term})' for term in or_groups])
        elif spider.db == DB_IEEE:
            or_groups = []
            for group in self.search_terms:
                or_groups.append(" OR ".join([f'("All Metadata":{term})' for term in group]))
            spider.query = " AND ".join([f'({term})' for term in or_groups])
        elif spider.db == DB_SPRINGER or spider.db == DB_SD:
            or_groups = []
            for group in self.search_terms:
                or_groups.append(" OR ".join([f'"{term}"' for term in group]))
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
        self.is_testing = STORAGE_TEST
        self.test_total_results = 100
        self.test_total_pages  = 2 

    # TODO store the initial total results query seems completely unnecesary
    def open_spider(self, spider):

        if not self.is_testing:
            self.conn = DatabaseManager.get_connection()
            self.cursor = self.conn.cursor()
        if spider.stype == 'Pages':

            if self.is_testing:
                spider.total_results = self.test_total_results
                spider.max_pages =  self.test_total_pages
                spider.rows_par_page = self.rows_par_page
                return

            try:
                # TODO Change IEEE and create ACM with the same worflow that Springer
                """self.db_param = getattr(spider, 'db', 'NoDB')
                self.query_param = getattr(spider, 'query', '')
                query = '''
                        SELECT TOP 1 total_results
                        FROM Query_total_results
                        WHERE db = ? AND query = ?
                        ORDER BY timestamp DESC
                        '''
                self.cursor.execute(query, (self.db_param, self.query_param))
                self.total_results  = self.cursor.fetchone()[0]
                self.max_pages = math.ceil(self.total_results / self.rows_par_page)
                
                spider.total_results = self.total_results"""
                #spider.max_pages = self.max_pages
                #spider.rows_par_page = self.rows_par_page

            except Exception as e:
                spider.logger.error(f"Error en open_spider: {e}")
                self.total_results = 0
                self.max_pages = 0
        elif spider.stype == 'Issues':

            if self.is_testing:
                if getattr(spider, 'db', DB_ACM) == DB_ACM:
                    spider.documents = ['/doi/10.1145/3686215.3688380']
                elif getattr(spider, 'db', DB_ACM) == DB_IEEE:
                    spider.documents = ['/document/10311503/']
                elif getattr(spider, 'db', DB_ACM) == DB_SPRINGER:
                    spider.documents = ['/article/10.1007/s11831-022-09831-7']
                elif getattr(spider, 'db', DB_ACM) == DB_SD:
                    spider.documents = ['10.1016/j.meddos.2024.07.005']
                return
            
            spider.rows_par_page = 100
            url_field = getattr(spider, 'url_field', 'doi')
            db = getattr(spider, 'db' , 'NoDB')
            #print('REACHING THE DOCUMENTS')
            urls = DatabaseManager.get_issues( [url_field] , 
                                                                [
                                                                    ('status', 'IS', None),
                                                                    ('db', '=',db),
                                                                    ('url', 'IS NOT', None)
                                                                ] )
            #print(f'Documents reached {len(urls)}')
            spider.documents = urls


                
    def process_item(self, item, spider):
        print(f'PROCESSING ITEMS....')
        if self.is_testing:
            with open("mssqlpipelineTest.txt", 'a',  encoding='utf-8') as file:
                for field, value in item.items():
                    print(f"{field}: {value}")
                    #print(f"{field}: {value}".encode("utf-8"), file=file)
                
                    
            return item

        self.db_param = getattr(spider, 'db', 'NoDB')
        #print('---------------------------------------------------------------------------------------------')

        if spider.stype == 'Pages' or spider.stype == 'Issues':
            pairs = [(field, value) for field, value in item.items()]
            url_field_name = getattr(spider, 'url_field')
            url_field = item.get(url_field_name)

            DatabaseManager.upsert_issue(pairs, (url_field_name, url_field))
        return item

    def close_spider(self, spider):
        # Cerrar conexiones
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()

