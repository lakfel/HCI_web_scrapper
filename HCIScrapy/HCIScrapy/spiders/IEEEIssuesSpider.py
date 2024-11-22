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
        
        self.db_param = db_param
        self.query_param = query_param
        self.total_results = 0
        self.max_pages = 0
        self.wait_timeout = 10



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
                    'key_selector' : '.abstract-text',
                    'url': url},
                dont_filter=True
            )

            time.sleep(random.uniform(4, 9))



    def parse(self, response):
        try:
            

            with open("ieee_test.html", 'w') as file:
                print(response.text.encode("utf-8"),file=file)

            title = response.css('.document-title span').xpath('.//text()').get()
            doi = response.css('.stats-document-abstract-doi a').xpath('.//text()').get()
            date_str = response.css('.doc-abstract-pubdate').xpath('normalize-space(text())').get().strip()
            date_info = date_str.split()
            date_day = date_info[0]
            date_month = date_info[1]
            date_year = date_info[2]
            abstract_t = response.css('.abstract-text').xpath('.//text()').getall()
            abstract = ''.join(abstract_t).strip()
            metrics = response.css('div.document-banner-metric-count')
            citations = metrics[0].xpath('.//text()').get()
            downloads = metrics[1].xpath('.//text()').get()
            comments = 'Downloads refer to full text views'
            url = response.meta['url']

                    
            yield {
                'db' : self.db,
                'title': title,
                'doi' : doi,
                'date' : date_str,
                'date_day' : int(date_day),
                'date_month' : date_month,
                'date_year' : int(date_year),
                'abstract' : abstract,
                'status' : 'OK',
                'comments' : comments,
                'citations' : int(citations),
                'downloads' : int(downloads),
                'url' : url,
                # Añade más campos según necesites
            }
        except Exception as e:
            self.logger.error(f"Error en parse_search: {e}")
