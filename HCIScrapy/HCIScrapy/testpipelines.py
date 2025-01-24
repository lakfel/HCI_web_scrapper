# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface


from HCIScrapy.config import *

class TestingMSSQLPipeline:

    def __init__(self):
        print('---------- Using TestingMSSQLPipeline ----------')
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

    # TODO store the initial total results query seems completely unnecesary
    def open_spider(self, spider):

        if spider.stype == 'Pages':
            spider.total_results = self.test_total_results
            spider.max_pages =  self.test_total_pages
            spider.rows_par_page = self.rows_par_page
            return
        elif spider.stype == 'Issues':
            if getattr(spider, 'db', DB_ACM) == DB_ACM:
                spider.documents = ['/doi/10.1145/3686215.3688380']
            elif getattr(spider, 'db', DB_ACM) == DB_IEEE:
                spider.documents = ['/document/10311503/']
            elif getattr(spider, 'db', DB_ACM) == DB_SPRINGER:
                spider.documents = ['/article/10.1007/s11831-022-09831-7']
            elif getattr(spider, 'db', DB_ACM) == DB_SD:
                spider.documents = ['10.1016/j.meddos.2024.07.005']
            return
            

                
    def process_item(self, item, spider):

        print(f'Testing MSSQL --- PROCESSING ITEMS....')
        inclusion_criterea = INCLUSION_CRITEREA[spider.db]['type']
        print(f'Inclusion criterea on types ',inclusion_criterea)
        
        if 'issue_type' in item:
            issue_type = item['issue_type']
            if issue_type not in inclusion_criterea:
                    print(f'Issue type not important : {issue_type}')
        with open("mssqlpipelineTest.txt", 'a',  encoding='utf-8') as file:
            for field, value in item.items():
                print(f"{field}: {value}")
                #print(f"{field}: {value}".encode("utf-8"), file=file)
            
                
        return item


    def close_spider(self, spider):
        # Cerrar conexiones
        if hasattr(self, 'cursor'):
            self.cursor.close()
        if hasattr(self, 'conn'):
            self.conn.close()
