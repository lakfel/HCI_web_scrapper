import scrapy
import time
import random
from dotenv import load_dotenv
import os

class SdissuesspiderSpider(scrapy.Spider):
    # Spider's name
    name = "sd_issues"

    # Database 
    db = 'ScienceDirect'

    # Spider's type [Results, Page, Issues]
    stype = 'Issues'
    
    url_field = 'url'

    def __init__(self, db_param='', query_param='', *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.use_api = True
        load_dotenv()
        self.API_KEY = os.getenv("SD_API_KEY")
        self.wait_timeout = 10
        self.metadata = {}
        self.base_search_url = 'https://api.elsevier.com/content/search/sciencedirect'


    def start_requests(self):


        # Initial search
        HEADERS = {
            "X-ELS-APIKey": self.API_KEY,
            "Accept": "application/json",  # Cambia a "text/xml, application/atom+xml" si prefieres XML
        }

        params = {
            "query" : self.query
        }
        request_data = {
            "url" : self.base_search_url, 
            "headers" : HEADERS,
            "params" : params
        }

      

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



    

