import scrapy
import time
from HCIScrapy.database import DatabaseManager
import json
import math
import random 
from dotenv import load_dotenv
import os
from HCIScrapy.config import DB_SD

class SdpagesspiderSpider(scrapy.Spider):
    
    name = "sd_pages"

    stype = 'Pages'

    # Database
    db = DB_SD

    url_field = 'doi'


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.use_api = True
        load_dotenv()
        self.use_selenium = False
        self.API_KEY = os.getenv("SD_API_KEY")
        print(f'SPIDER KEY {self.API_KEY}')

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
            "Accept": "application/json",
        }
        
        # Build query parameters in a more REST-friendly way
        params = {
            "query": self.query,
            "count": self.rows_par_page,
            "httpAccept": "application/json"  # Explicitly request JSON response
        }
        
        request_data = {
            "url": self.base_url,
            "headers": HEADERS,
            "params": params,
            "method": "GET",  # Explicitly specify GET method
            "sort": "relevance"
        }
        
        print(f'Initiating GET request for query: {self.query}')
        if self.id_query_totals == -1 :
            self.total_results = self.get_number_results(request_data)
            self.id_query_totals = DatabaseManager.insert_query_totals(self.db, self.base_url, self.query, self.total_results)
        print(f'Total results from GET request: {self.total_results}')
        
        return
        request_data['count'] = self.rows_par_page
        self.max_pages = min(math.ceil(self.total_results/self.rows_par_page), 
                            math.ceil(self.max_results/self.rows_par_page))
        
        #self.max_pages = 1  # Consider removing this limitation if you need more pages
        
        for page_count in range(1, self.max_pages + 1):

            request_data_tempo = request_data.copy()
            start = (page_count - 1) * self.rows_par_page
            request_data_tempo['params']["start"] = start
            
            # Store query ID for tracking
            id_query = DatabaseManager.insert_page(self.db, page_count, f'{self.query}-{page_count}', self.id_query_totals)
            self.ids_query[f'{start}'] = id_query
            
            yield scrapy.Request(
                self.base_url,
                meta={'request_data': request_data_tempo},
                dont_filter=True,
                callback=self.parse,
                errback=self.handle_error  # Add error handling
            )
            
            time.sleep(random.uniform(1, 2))

    def handle_error(self, failure):
        # Add this new method to handle request failures
        print(f"Request failed: {failure.value}")
        # You might want to log this or handle retry logic



    def parse(self, response):

        # Get URLs using different methods
        current_url = response.url

        # Process the JSON response as before
        data = json.loads(response.text)
        search_results = data['search-results']
        start = search_results['opensearch:startIndex']
        id_query = self.ids_query[start]

        for entry in search_results['entry']:
            url = entry['prism:url']
            title = entry['dc:title']
            venue = entry['prism:publicationName']
            doi = entry['prism:doi']
            date = entry['prism:coverDate']
            
            yield {
                'db': self.db,
                'id_query': id_query,
                'url': url,
                'title': title,
                'venue': venue,
                'doi': doi,
                'date': date,
                'id_issues' : doi
            }



    def get_number_results(self, request_data):

        api_response, meta = self.request(request_data)
        response = json.loads(api_response.text)
        #print(f'GOT THE JSON..?  --- {response}' )
        if 'search-results' in response:
            search_results = response['search-results']
            if 'opensearch:totalResults' in search_results :
                return int(search_results['opensearch:totalResults'])
        return 0
