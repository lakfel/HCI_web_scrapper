# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface

from HCIScrapy.database import DatabaseManager
from HCIScrapy.config import *
from datetime import datetime, timedelta



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
            fields = ['Title','Abstract','Keyword']
            fields_ands = []
            for field in fields:
                field_or = []
                for group in self.search_terms:
                    field_or.append(" OR ".join([f'{field}:({term})' for term in group]))
                fields_ands.append(" AND ".join([f'({term})' for term in field_or]))
            spider.query = " OR ".join([f'({term})' for term in fields_ands])
        elif spider.db == DB_IEEE:
            fields = ['Document Title','Abstract','Author Keywords']
            fields_ands = []
            for field in fields:
                field_or = []
                for group in self.search_terms:
                    field_or.append(" OR ".join([f'("{field}":{term})' for term in group]))
                fields_ands.append(" AND ".join([f'({term})' for term in field_or]))
            spider.query = " OR ".join([f'({term})' for term in fields_ands])
        elif spider.db == DB_SD:
            or_groups = []
            for group in self.search_terms:
                or_groups.append(" OR ".join([f'"{term}"' for term in group]))
            query = " AND ".join([f'({term})' for term in or_groups])
            spider.query = f'ttl({query}) OR abs({query})'
        elif spider.db == DB_SPRINGER :
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
        self.is_testing = STORAGE_TEST
        self.test_total_results = 100
        self.test_total_pages  = 2 

    
    def open_spider(self, spider):
        
        spider_db = getattr(spider, 'db', 'NoDB')
        id_query_totals, total_results, timestamp = DatabaseManager.get_query_totals(spider_db)

        if id_query_totals != -1:
            current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            date_difference = datetime.strptime(current_date, "%Y-%m-%d %H:%M:%S") - datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
            day_limit_diff = 30 
            if date_difference > timedelta(days=day_limit_diff):
                id_query_totals = -1
                total_results = 0

        spider.id_query_totals = id_query_totals
        spider.total_results = total_results

        if spider.stype == 'Pages':

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
            
            #spider.rows_par_page = 100
            url_field = getattr(spider, 'url_field', 'doi')
            db = getattr(spider, 'db' , 'NoDB')
            #print('REACHING THE DOCUMENTS')
            urls = DatabaseManager.get_issues( [url_field] , 
                                                                [
                                                                ('db','=',db),
                                                                ('status', ' IS ', None),
                                                                (url_field, 'IS NOT ', None),
                                                                #('abstract', ' IS ', None)
                                                                 ] )
            #print(f'Documents reached {len(urls)}')
            spider.documents = urls


                
    def process_item(self, item, spider):
        
        print(f'PROCESSING ITEMS....')
        inclusion_criterea = INCLUSION_CRITEREA[spider.db]['type']
        print(f'Inclusion criterea on types ',inclusion_criterea)
        
        self.db_param = getattr(spider, 'db', 'NoDB')
        pairs = [(field, value) for field, value in item.items()]
            
        if 'type' in item:
            print(f'Analysing issue type....')
            issue_type = item['type'].lower()
            print(f'Analysing issue type.... {issue_type}')
            if issue_type not in inclusion_criterea:
                print(f'Issue type not important  --- {issue_type}')
                # Check if status already exists in pairs
                status_index = next((i for i, pair in enumerate(pairs) if pair[0] == 'status'), None)
                if status_index is not None:
                    pairs[status_index] = ('status', 'EXC')
                else:
                    pairs.append(('status', 'EXC'))

        #TODO currently the issues table contains the id_query field, this is incorerct since issues are now independen of the search

        url_field_name = getattr(spider, 'url_field')
        url_field = item.get(url_field_name)
        DatabaseManager.upsert_issue(pairs, (url_field_name, url_field))

        #This should always happens
        if 'id_query' in item and 'id_issues' in item:
            values = [
                        ('query_status_id', item['id_query']),
                        ('id_issues',item['id_issues']),
                        ('db', getattr(spider, 'db', 'NoDB')),
                        ('id_trial',TRIAL)
                    ]
            DatabaseManager.upsert_issue_query(values, item['id_issues'], TRIAL)
        return item

    def close_spider(self, spider):
        # Cerrar conexiones
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()

