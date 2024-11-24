import scrapy
from urllib.parse import quote, urlencode
import time
import random
from HCIScrapy.database import DatabaseConfig

class SpringerissuesspiderSpider(scrapy.Spider):

    # Spider's name
    name = "springer_issues"

    # Database 
    db = 'Springer'

    # Spider's type [Results, Page, Issues]
    stype = 'Issues'
    
    url_field = 'url'

    def __init__(self, db_param='', query_param='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.db_param = db_param
        self.query_param = query_param
        self.total_results = 0
        self.max_pages = 0
        self.wait_timeout = 10
        self.metadata = {}
        self.base_url = 'https://link.springer.com'


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
                meta={'url': url},
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
            item = {'db' : self.db, 'url' : url, 'status' : 'OK', }
            
            metrics = response.css('li.app-article-metrics-bar__item')
            for metric in metrics:
                label = metric.css('.app-article-metrics-bar__label').xpath('.//text()').get()
                if label:
                    m_text = metric.css('.app-article-metrics-bar__count::text').get().strip()
                    if label == 'Accesses':
                        item['Downloads'] = ''.join(m_text).strip()
                    elif label == 'Citations':
                        item['Citations'] = ''.join(m_text).strip()
            abstract = response.css('meta[name="citation_abstract"]::attr(content)').get()
            if abstract:
                item['abstract'] = abstract
            title = response.css('meta[name="citation_title"]::attr(content)').get()
            if title:
                item['title'] = title
            doi = response.css('meta[name="DOI"]::attr(content)').get()
            if doi:
                item['doi'] = doi
            comments =  response.css('meta[property="og:type"]::attr(content)').get()
            if comments:
                item['comments'] = comments

            yield item
        
        except Exception as e:
            self.logger.error(f"Error en parse_search: {e}")

    
