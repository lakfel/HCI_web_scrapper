import scrapy
from urllib.parse import quote, urlencode
import time
import random
from HCIScrapy.config import DB_SPRINGER

class SpringerissuesspiderSpider(scrapy.Spider):

    # Spider's name
    name = "springer_issues"

    # Database 
    
    db = DB_SPRINGER

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

        self.use_selenium = False
        self.use_api = False


    def start_requests(self):

        print(f' TOTAL Documents {len(self.documents)}')

        if not hasattr(self, 'documents'):
            self.documents = []
            self.logger.error('NO DOCUMENTS TO DOWNLOAD ')

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36"
        }
        #self.documents = [self.documents[1]]
        for url in self.documents:

            search_url = f"{self.base_url}{url}"
            print(f'SEARCHING-- {self.db}, {search_url}')
        
            yield scrapy.Request(
                search_url, 
                meta={'url': url},
                headers=headers,
                dont_filter=True
            )




    def parse(self, response):
        try:          
            
            url = response.meta['url']
            item = {'db' : self.db, 'url' : url, 'status' : 'OK', }
            
            metrics = response.css('li.app-article-metrics-bar__item')
            for metric in metrics:
                label = metric.css('.app-article-metrics-bar__label').xpath('.//text()').get()
                if label:
                    m_text = metric.css('.app-article-metrics-bar__count::text').get().strip()
                    if label == 'Accesses':
                        item['Downloads'] = int(''.join(m_text).strip().replace('k','000'))
                    elif label == 'Citations':
                        item['Citations'] = int(''.join(m_text).strip().replace('k','000'))
            abstract_a = response.css('section[data-title="Abstract"] .c-article-section__content').xpath('.//text()').getall()
            abstract = ''.join(abstract_a).strip()
            keywords = []
            # Select all keyword links with the specific data-track-action attribute
            kwds = response.css('a[data-track-action="view keyword"]::text').getall()
            if kwds:
                keywords = [k.strip() for k in kwds if k.strip()]
                

            item['keywords'] = ','.join(keywords)
            title = response.css('meta[name="dc.description"]::attr(content)').get()
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
                item['type'] = comments
            #print(item)
            yield item
        
        except Exception as e:
            self.logger.error(f"Error en parse_search: {e}")

    
