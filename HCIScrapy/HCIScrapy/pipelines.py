# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from HCIScrapy.database import DatabaseConfig
from datetime import datetime
import pyodbc

class HciscrapyPipeline:
    def process_item(self, item, spider):
        return item
    

class MSSQLPipeline:

    def open_spider(self, spider):
        self.conn = DatabaseConfig.get_connection()
        self.cursor = self.conn.cursor()


    def process_item(self, item, spider):
        if spider.db == 'IEEE':
            #if spider.name == 'ieee_results':
            if spider.stype == 'Results':
                # Guardar datos para resultados IEEE
                self.cursor.execute(
                    """
                    INSERT INTO Query_total_results 
                    (db, timestamp, url, query, total_results) 
                    VALUES (?, ?, ?, ?, ?)
                    """, 
                    (
                        spider.db,
                        datetime.now(),  # timestamp
                        item.get('url', ''),  # url
                        item.get('query', ''),  # query de búsqueda
                        item.get('total_results', 0)  # total de resultados
                    )
                )
                self.conn.commit()
            elif spider.stype == 'Pages':


                
        return item

    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()

