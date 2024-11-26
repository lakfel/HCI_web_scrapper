import scrapy
import time
from HCIScrapy.database import DatabaseConfig
import json
import math
import random 
from dotenv import load_dotenv
import os

class SdpagesspiderSpider(scrapy.Spider):
    
    name = "sd_pages"

    stype = 'Pages'

    # Database
    db = 'ScienceDirect'

    url_field = 'url'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.use_api = True
        load_dotenv()
        self.use_selenium = False
        self.API_KEY = os.getenv("SD_API_KEY")
        self.use_api = True
        self.total_results = 0
        self.max_results = 6000
        self.rows_par_page = 100 
        self.wait_timeout = 10
        self.base_url = 'https://api.elsevier.com/content/search/sciencedirect'
        self.meta= {}
        self.js = {} # Dict key:name value: tuple ( statement, result)
        #TODO adapt IEEE to this 
        self.ids_query = {} # Temprorary measure to pass the query to the parser. With selenium is not possbile.

    def start_requests(self):

        HEADERS = {
            "X-ELS-APIKey": self.API_KEY,
            "Accept": "application/json",  # Cambia a "text/xml, application/atom+xml" si prefieres XML
        }
        params = {
            "query" : self.query,
            "count" : self.rows_par_page
        }
        request_data = {
            "url" : self.base_url, 
            "headers" : HEADERS,
            "params" : params,
            "sort" : "relevance"
        }
        
        self.total_results = self.get_number_results(request_data)
        print(f'TOTAL RESULTS {self.total_results}')
        DatabaseConfig.insert_query_totals(self.db, self.base_url, self.query, self.total_results)
        request_data['count'] = self.rows_par_page
        self.max_pages = min(math.ceil(self.total_results/self.rows_par_page),math.ceil(self.max_results/self.rows_par_page))
        
        self.max_pages = 2

        for page_count in range(1, self.max_pages + 1):
            
            request_data_tempo = request_data.copy()
            start = (page_count - 1) * self.rows_par_page
            #params_tempo["start"] = (page_count - 1) * self.rows_par_page
            request_data_tempo['params']["start"] = start


            #TODO This can be better generalized in order to add any type of storage
            id_query = DatabaseConfig.insert_page(self.db, self.query, page_count, f'{self.query}-{page_count}')
            self.ids_query[f'{start}'] = id_query

            yield scrapy.Request(
                self.base_url,
                meta = {
                        'request_data': request_data_tempo 
                        },
                dont_filter=True,
                callback=self.parse
            )

            time.sleep(random.uniform(4, 9))



    def parse(self, response):
        #id_query = self.ids_query[responseHtml.url]
        data = json.loads(response.text)
        
        print(f'GOT THE JSON..?  --- {data}' )
        search_results = data['search-results']





    def get_number_results(self, request_data):

        api_response, meta = self.request(request_data)
        response = json.loads(api_response.text)
        print(f'GOT THE JSON..?  --- {response}' )
        if 'search-results' in response:
            search_results = response['search-results']
            if 'opensearch:totalResults' in search_results :
                return int(search_results['opensearch:totalResults'])
        return 0
