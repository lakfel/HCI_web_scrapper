import scrapy
import time
from HCIScrapy.database import DatabaseManager
import requests
import re
import math
import random 
import urllib.parse 
from HCIScrapy.config import DB_SPRINGER


class SpringerpagesSpider(scrapy.Spider):

    # Spider's name
    name = "springer_pages"

    stype = 'Pages'

    # Database
    db = DB_SPRINGER

    url_field = 'url'


    def __init__(self,  *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.use_selenium = False
        self.use_api = False
        self.id_query_totals = -1
        self.total_results = 0
        self.rows_par_page = 20
        self.max_pages = 50
        self.max_results = 1000
        self.wait_timeout = 10
        self.base_url = 'https://link.springer.com/search?new-search=true&query='
        self.ids_query = {}

    def start_requests(self):

        # Starting in a number but it will be replaced in the first request
        

        base_search_url = f'{self.base_url}{urllib.parse.quote_plus(self.query)}'
        request_data = {
            "url" : base_search_url
        }
        if self.id_query_totals == -1 :
            print('No totals registered... retreiving totals') 
            req_data =  request_data.copy()
            self.total_results = self.get_number_results(request_data)
            self.id_query_totals = DatabaseManager.insert_query_totals(self.db, request_data['url'], self.query, self.total_results)
            print(f'Totals : {self.total_results} -- id_totals {self.id_query_totals}')
        
        print(f'RESULTS TOTAL --- {self.total_results} .... \n\t Id query ---- {self.id_query_totals}')
        


        self.max_pages = min(math.ceil(self.total_results/self.rows_par_page), self.max_pages)

 

        for page_count in range(1, self.max_pages + 1):
            search_url = f'{base_search_url}&page={page_count}'
            request_data = {
                    "url" : search_url
                }
           
            id_query = DatabaseManager.insert_page(self.db, page_count, search_url, self.id_query_totals )
            self.ids_query[search_url] = id_query
            print(f'IDQUERY DE ---- {search_url}')
            yield scrapy.Request(
                search_url,
                meta = {
                        'url': search_url
                        },
                dont_filter=True,
                callback=self.parse
            )
            time.sleep(random.uniform(1, 2))

    def parse(self, response):
   
        url = response.url
        id_query = self.ids_query[url]

        try:

            li_results = response.css('li[data-test="search-result-item"]')
            
            for li in li_results:
             
                stype = li.css('.c-meta__type::text').get()
                
                url = li.css('a.app-card-open__link::attr(href)').get()

                # Get title from the span inside the link
                title = li.css('.app-card-open__link > span::text').get()
                
                # Get publication date
                date_str = li.css('span.c-meta__item[data-test="published"]::text').get()

                item = {
                    'title': title,
                    'db': self.db,
                    'id_query': id_query,
                    'url': url,
                    'id_issues': url
                }
                print(f'ITEM -- {item}')

                yield item
                
        except Exception as e:
            self.logger.error(f"Error in parse: {e}")
        


    def get_number_results(self, request_data):
        try:
            # Use requests for this initial check since we're not in the Scrapy engine yet
            response, meta = self.request(request_data)
            
            results_text = response.css('span[data-test="results-data-total"]::text').get()
            if not results_text:
                raise ValueError("Tag not found -- data-test='results-data-total'.")
            
            match = re.search(r"of ([\d,]+) results", results_text)
            if not match:
                raise ValueError(f"Tag format error. {results_text}")
            
            total_results = int(match.group(1).replace(",", ""))
            return total_results

        except Exception as e:
            self.logger.error(f"Error extracting total results: {e}")
            return 0
