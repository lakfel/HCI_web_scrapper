import scrapy
from urllib.parse import quote, urlencode
import time
import random
from HCIScrapy.database import DatabaseConfig

class IeeeissuesspiderSpider(scrapy.Spider):

    # Spider's name
    name = "ieee_issues"

    # Database 
    db = 'IEEE'

    # Spider's type [Results, Page, Issues]
    stype = 'Issues'

    allowed_domains = ["ieeexplore.ieee.org"]

    base_url = "https://ieeexplore.ieee.org"
    
    url_field = 'url'

    def __init__(self, db_param='', query_param='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.use_selenium = True
        self.db_param = db_param
        self.query_param = query_param
        self.total_results = 0
        self.max_pages = 0
        self.wait_timeout = 10
        self.metadata = {}


    def start_requests(self):


        print(f' TOTAL Documents {len(self.documents)}')
        if not hasattr(self, 'documents'):
            self.documents = []
            self.logger.error('NO DOCUMENTS TO DOWNLOAD ')

        for url in self.documents:


            search_url = f"{self.base_url}{url}"
            print(f'SEARCHING-- {self.db}, {search_url}')
        
            yield scrapy.Request(
                search_url, 
                meta={
                    'use_selenium': True, 
                    'key_selector' : 'meta[name="parsely-type"]',
                    'url': url},
                dont_filter=True
            )

            time.sleep(random.uniform(4, 9))



    def parse(self, response):
        try:
            #with open("ieee_test.html", 'w') as file:
            #    print(response.text.encode("utf-8"),file=file)
            #with open("ieee_test_meta.js", 'w') as file:
            #    print(self.metadata,file=file)                
            
            url = response.meta['url']
            item = {'db' : self.db, 'url' : url}

            metadata = self.metadata[url]

            if 'title' in metadata:
                item['title'] = metadata['title']
            if 'doi' in metadata:
                item['doi'] = metadata['doi']
            if 'xploreDocumentType' in metadata:
                item['comments'] = metadata['xploreDocumentType']
            if 'displayPublicationDate' in metadata:
                item['date'] = metadata['displayPublicationDate'].strip()
                #date_day = int(date.split()[0].split('-')[0])
                #date_month = date.split()[1]
                #item['date_day'] = date_day
                #item['date_month'] = date_month
                #item['date'] = date
                #date_year = int(date.split()[2])
            if 'publicationYear' in metadata:
                item['date_year'] = metadata['publicationYear']
            if 'abstract' in metadata:
                item['abstract'] = metadata['abstract']

            item['status'] = 'OK'

            if 'publicationTitle' in metadata:
                item['venue'] = metadata['publicationTitle']

            if 'metrics'in metadata:
                metrics = metadata['metrics']
                if 'citationCountPaper' in metrics:
                    item['Citations'] = metrics['citationCountPaper']
                if 'totalDownloads' in metrics:
                    item['Downloads'] = metrics['totalDownloads']

            del self.metadata[url]

            yield item
        
        except Exception as e:
            self.logger.error(f"Error en parse_search: {e}")

    
